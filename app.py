import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
import os
from datetime import datetime
import base64
import hashlib
import re
from supabase import create_client, Client

# ✅ INICIALIZAÇÃO DO SUPABASE
@st.cache_resource
def init_supabase():
    """Inicializa o cliente Supabase"""
    try:
        supabase_url = st.secrets["supabase"]["url"]
        supabase_key = st.secrets["supabase"]["key"]
        supabase: Client = create_client(supabase_url, supabase_key)
        return supabase
    except Exception as e:
        st.error(f"❌ Erro ao conectar ao Supabase: {e}")
        st.info("💡 Verifique se configurou o secrets.toml corretamente")
        return None

supabase = init_supabase()
# Teste de conexão simples
if supabase:
    st.write("✅ Supabase conectado!")
else:
    st.error("❌ Falha na conexão")

# ✅ FUNÇÃO SEGURA PARA APP_URL
def _get_app_url():
    try:
        if hasattr(st, "secrets") and st.secrets and "APP_URL" in st.secrets:
            return st.secrets["APP_URL"]
    except:
        pass
    return "https://relatoriofinanceiro-ua9w8bfoe6ajqu6ynauset.streamlit.app"

APP_URL = _get_app_url()

# ── CONFIGURAÇÃO INICIAL ──────────────────────────────────────────────────────
def get_image_base64(path):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, path)
    if os.path.exists(full_path):
        with open(full_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

st.set_page_config(
    page_title="Financeiro PCP | Bonsono",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="collapsed"
)

REPRESENTANTES_DB = "representantes.csv"  # Mantido apenas para representantes (local)

# ── CSS ESTILIZADO ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #f7f8fc; }
.page-header {
    background: linear-gradient(135deg, #0f2942 0%, #1a4a7a 60%, #1e6fbf 100%);
    border-radius: 16px; padding: 32px 40px; margin-bottom: 32px;
    display: flex; align-items: center; gap: 24px;
    box-shadow: 0 8px 32px rgba(15,41,66,0.18);
}
.header-logo {
    height: 64px; width: 64px; object-fit: contain;
    background: #fff; border-radius: 12px;
    padding: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.25);
    flex-shrink: 0;
}
.page-header h1 {
    font-family: 'Inter', sans-serif; font-size: 2rem;
    font-weight: 800; color: #fff; margin: 0;
    letter-spacing: -0.5px; line-height: 1.2;
}
.page-header .subtitle {
    color: #a8c8f0;
    font-size: 0.85rem; font-weight: 300;
    border-top: 1px solid rgba(255,255,255,0.15);
    padding-top: 6px; margin-top: 6px;
}
.upload-label   { font-family: 'Inter', sans-serif; font-size: 0.78rem; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: #6b7a99; margin-bottom: 8px; display: block; }
.kpi-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 16px; margin: 24px 0; }
.kpi-card { background: #fff; border-radius: 14px; padding: 22px 20px 18px 20px; box-shadow: 0 2px 12px rgba(15,41,66,0.07); position: relative; overflow: hidden; }
.kpi-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; }
.kpi-card.total::before     { background: #0f2942; }
.kpi-card.assist::before    { background: #e07b3a; }
.kpi-card.lojas::before     { background: #2ecc71; }
.kpi-card.avista::before    { background: #8e44ad; }
.kpi-card.boleto::before    { background: #2980b9; }
.kpi-card.comercial::before { background: #d4a017; }
.kpi-card.cheque::before    { background: #e74c3c; }
.kpi-label { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px; color: #8a94a6; margin-bottom: 8px; }
.kpi-value { font-family: 'Inter', sans-serif; font-size: 1.45rem; font-weight: 800; color: #0f2942; line-height: 1.1; }
.kpi-badge { display: inline-block; margin-top: 8px; font-size: 0.72rem; font-weight: 600; padding: 2px 8px; border-radius: 20px; background: #f0f4ff; color: #3a5bab; }
.sec-title { font-family: 'Inter', sans-serif; font-size: 1rem; font-weight: 700; color: #0f2942; margin: 32px 0 12px 0; display: flex; align-items: center; gap: 8px; }
.sec-title::after { content: ''; flex: 1; height: 1px; background: #e2e8f0; margin-left: 8px; }
.stDownloadButton > button { background: #0f2942 !important; color: white !important; border: none !important; border-radius: 10px !important; padding: 10px 24px !important; font-family: 'Inter', sans-serif !important; font-weight: 700 !important; font-size: 0.85rem !important; }
.stDownloadButton > button:hover { background: #1a4a7a !important; }
[data-testid="stFileUploader"] { background: #fff; border-radius: 14px; padding: 8px; box-shadow: 0 2px 10px rgba(15,41,66,0.06); }
.info-box { background: #eef4ff; border-left: 4px solid #2980b9; border-radius: 10px; padding: 16px 20px; color: #1a3a5c; font-size: 0.88rem; line-height: 1.8; }
.saved-badge   { background: #d4edda; color: #155724; border-radius: 8px; padding: 8px 16px; font-size: 0.85rem; font-weight: 600; display: inline-block; margin-top: 8px; }
.already-badge { background: #fff3cd; color: #856404; border-radius: 8px; padding: 8px 16px; font-size: 0.85rem; font-weight: 600; display: inline-block; margin-top: 8px; }
.rep-banner {
    background: linear-gradient(135deg, #1a4a7a, #2980b9);
    color: white; padding: 12px 20px; border-radius: 10px;
    margin: 16px 0; display: flex; align-items: center; gap: 12px;
}
.readonly-badge {
    background: #fff3cd; color: #856404; padding: 4px 12px;
    border-radius: 20px; font-size: 0.75rem; font-weight: 600;
}
.debug-box {
    background: #fff3cd; border: 1px solid #ffc107;
    border-radius: 8px; padding: 12px; font-size: 0.8rem;
}
.success-box {
    background: #d4edda; border-left: 4px solid #28a745;
    border-radius: 8px; padding: 12px; margin: 16px 0;
}
</style>
""", unsafe_allow_html=True)

logo_b64 = get_image_base64("logo-bonsono.png")

# ── HELPERS DE FORMATAÇÃO E LÓGICA ────────────────────────────────────────────
def format_brl(value):
    try:
        return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

def is_boleto(tipo):
    if not pd.notna(tipo):
        return False
    t = str(tipo).upper()
    return bool("DIAS" in t or "GRANDES REDES" in t or re.search(r'\d+/\d+', t))

def is_a_vista(tipo):
    t = str(tipo).upper()
    return ("À VISTA" in t or "A VISTA" in t) if pd.notna(tipo) else False

def load_data(file):
    df = pd.read_excel(file, header=2)
    df["Vlr. Nota"] = pd.to_numeric(df["Vlr. Nota"], errors="coerce").fillna(0)
    return df

def calcular_totais(df):
    df["_is_assistencia"] = df["Descrição (Tipo de Operação)"].str.upper().str.contains("ASSISTENCIA", na=False)
    df["_is_loja"]        = df["Regiao Vendedor"].str.upper().str.strip() == "LOJAS"
    df["_is_a_vista"]     = df["Descrição (Tipo de Negociação)"].apply(is_a_vista)
    df["_is_boleto"]      = df["Descrição (Tipo de Negociação)"].apply(is_boleto)
    df["_is_comercial"]   = df["Regiao Vendedor"].str.upper().str.contains("REGIAO", na=False)
    return {
        "total_geral":       df["Vlr. Nota"].sum(),
        "total_assistencia": df[df["_is_assistencia"]]["Vlr. Nota"].sum(),
        "total_lojas":       df[df["_is_loja"]]["Vlr. Nota"].sum(),
        "total_a_vista":     df[df["_is_a_vista"]]["Vlr. Nota"].sum(),
        "total_boleto":      df[df["_is_boleto"]]["Vlr. Nota"].sum(),
        "total_comercial":   df[df["_is_comercial"]]["Vlr. Nota"].sum(),
        "qtd_notas":         len(df),
    }, df

# ── GERENCIAMENTO DE HISTÓRICO COM SUPABASE ───────────────────────────────────
def _normalize_col_name(name):
    """Normaliza nome de categoria para nome de coluna válido"""
    return f"extra_{name.lower().strip().replace(' ', '_').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ç', 'c')}"

def carregar_historico():
    """Carrega histórico do Supabase"""
    if supabase is None:
        st.error("❌ Supabase não conectado")
        return pd.DataFrame()
    
    try:
        # Buscar todos os registros da tabela historico_financeiro
        response = supabase.table("historico_financeiro").select("*").order("data").execute()
        
        if not response.data:
            return pd.DataFrame()
        
        df = pd.DataFrame(response.data)
        
        # Converter data para string no formato YYYY-MM-DD
        if "data" in df.columns:
            df["data"] = pd.to_datetime(df["data"], errors="coerce").dt.strftime("%Y-%m-%d")
        
        # Preencher NaN com 0
        df = df.fillna(0)
        
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar histórico: {e}")
        return pd.DataFrame()

def salvar_historico(data_ref, totais, extras_por_cat=None):
    """Salva histórico no Supabase"""
    if supabase is None:
        st.error("❌ Supabase não conectado")
        return False
    
    try:
        data_str = data_ref.strftime("%Y-%m-%d")
        
        # Verificar se já existe registro para esta data
        existing = supabase.table("historico_financeiro").select("data").eq("data", data_str).execute()
        
        if existing.data:
            # Deletar registro existente
            supabase.table("historico_financeiro").delete().eq("data", data_str).execute()
        
        # Preparar novo registro
        novo_registro = {"data": data_str, **totais}
        
        # Adicionar extras como colunas dinâmicas
        if extras_por_cat:
            for cat, val in extras_por_cat.items():
                col_name = _normalize_col_name(cat)
                novo_registro[col_name] = float(val)
        
        # Inserir no Supabase
        supabase.table("historico_financeiro").insert(novo_registro).execute()
        
        return True
    except Exception as e:
        st.error(f"❌ Erro ao salvar histórico: {e}")
        return False

def deletar_registro_historico(data_str):
    """Deleta um registro do histórico por data"""
    if supabase is None:
        st.error("❌ Supabase não conectado")
        return False
    
    try:
        supabase.table("historico_financeiro").delete().eq("data", data_str).execute()
        return True
    except Exception as e:
        st.error(f"❌ Erro ao deletar registro: {e}")
        return False

# ── GERENCIAMENTO DE REPRESENTANTES ───────────────────────────────────────────
def carregar_representantes_secrets():
    reps = {}
    try:
        if not hasattr(st, "secrets") or not st.secrets:
            return reps
        if "representantes" not in st.secrets:
            return reps
        for token, dados in st.secrets["representantes"].items():
            if isinstance(dados, str) and "|" in dados:
                partes = dados.split("|")
                if len(partes) >= 2:
                    nome, regioes = partes[0], partes[1]
                    reps[token] = {
                        "nome": nome.strip(),
                        "regioes": [r.strip() for r in regioes.split(";") if r.strip()],
                        "ativo": True,
                        "fonte": "secrets"
                    }
    except:
        pass
    return reps

def salvar_representantes_csv(token, nome, regioes_str):
    if os.path.exists(REPRESENTANTES_DB):
        try:
            df = pd.read_csv(REPRESENTANTES_DB)
        except:
            df = pd.DataFrame(columns=["token", "nome", "regioes", "ativo"])
    else:
        df = pd.DataFrame(columns=["token", "nome", "regioes", "ativo"])
    novo = pd.DataFrame([{"token": token, "nome": nome, "regioes": regioes_str, "ativo": True}])
    if not df.empty and token in df["token"].values:
        df = df[df["token"] != token]
    df = pd.concat([df, novo], ignore_index=True)
    df.to_csv(REPRESENTANTES_DB, index=False)
    return True

def carregar_representantes_csv():
    reps = {}
    if os.path.exists(REPRESENTANTES_DB):
        try:
            df = pd.read_csv(REPRESENTANTES_DB)
            for _, row in df.iterrows():
                if pd.notna(row["token"]):
                    regioes = row["regioes"].split(";") if pd.notna(row["regioes"]) else []
                    reps[row["token"]] = {
                        "nome": row["nome"],
                        "regioes": [r.strip() for r in regioes if r.strip()],
                        "ativo": bool(row.get("ativo", True)),
                        "fonte": "csv"
                    }
        except:
            pass
    return reps

def validar_token(token):
    if not token:
        return None
    reps_secrets = carregar_representantes_secrets()
    if token in reps_secrets and reps_secrets[token]["ativo"]:
        return reps_secrets[token]
    reps_csv = carregar_representantes_csv()
    if token in reps_csv and reps_csv[token]["ativo"]:
        return reps_csv[token]
    return None

def gerar_token(nome, senha_admin="bonsono2024"):
    raw = f"{nome}:{senha_admin}:{datetime.now().isoformat()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]

# ── VIEW READ-ONLY PARA REPRESENTANTES ────────────────────────────────────────
def visualizar_view_representante(df, representante, data_filtro=None):
    st.markdown(f"""
    <div class="rep-banner">
        <span>👤</span>
        <div>
            <strong>Área do Representante</strong><br>
            <small>{representante['nome']} • Visualização consultiva</small>
        </div>
        <span class="readonly-badge">🔒 Somente leitura</span>
    </div>
    """, unsafe_allow_html=True)
    
    if representante["regioes"]:
        df = df[df["Regiao Vendedor"].isin(representante["regioes"])].copy()
    
    if data_filtro:
        try:
            df["Dt. Neg."] = pd.to_datetime(df["Dt. Neg."], errors="coerce")
            df = df[df["Dt. Neg."].dt.strftime("%Y-%m-%d") == data_filtro]
        except:
            st.warning(f"⚠️ Data inválida: {data_filtro}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📋 Pedidos", len(df))
    with col2:
        st.metric("💰 Valor Total", format_brl(df["Vlr. Nota"].sum()))
    with col3:
        medio = df["Vlr. Nota"].mean() if len(df) > 0 else 0
        st.metric("🎫 Ticket Médio", format_brl(medio))
    
    cols_exibir = ["Nro. Único", "Previsão de entrega", "Nome Parceiro (Parceiro)", "Vlr. Nota", "Apelido (Vendedor)", "Regiao Vendedor"]
    cols_disponiveis = [c for c in cols_exibir if c in df.columns]
    df_exibir = df[cols_disponiveis].copy()
    
    if "Previsão de entrega" in df_exibir.columns:
        df_exibir["Previsão de entrega"] = pd.to_datetime(df_exibir["Previsão de entrega"], errors="coerce").dt.strftime("%d/%m/%Y")
    if "Vlr. Nota" in df_exibir.columns:
        df_exibir["Vlr. Nota"] = df_exibir["Vlr. Nota"].map(format_brl)
    
    rename_map = {"Nro. Único": "Nº Único", "Previsão de entrega": "Prev. Entrega", "Nome Parceiro (Parceiro)": "Parceiro", "Vlr. Nota": "Valor", "Apelido (Vendedor)": "Vendedor", "Regiao Vendedor": "Região"}
    df_exibir = df_exibir.rename(columns={k: v for k, v in rename_map.items() if k in df_exibir.columns})
    
    st.dataframe(df_exibir, use_container_width=True, hide_index=True, height=500)
    
    if len(df_exibir) > 0:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_exibir.to_excel(writer, sheet_name="Meus Pedidos", index=False)
        nome_arquivo = f"pedidos_{representante['nome'].split()[0]}_{data_filtro or 'todos'}.xlsx"
        st.download_button(label="⬇️ Exportar meus pedidos (Excel)", data=buffer.getvalue(), file_name=nome_arquivo, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ── HEADER COM LOGO ───────────────────────────────────────────────────────────
st.markdown(f"""
<div class="page-header">
    <img class="header-logo" src="image/png;base64,{logo_b64}" />
    <div>
        <h1>Relatório Financeiro da Produção</h1>
        <p class="subtitle">📡 Análise automática gerada a partir do Portal de Vendas — Sankhya</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── VERIFICAR CONEXÃO COM SUPABASE ────────────────────────────────────────────
if supabase is None:
    st.error("""
    ### ⚠️ Supabase Não Configurado
    
    Para usar este aplicativo, você precisa configurar o Supabase:
    
    1. Crie uma conta em [supabase.com](https://supabase.com)
    2. Crie um novo projeto
    3. Vá em Settings → API e copie a URL e a chave anon
    4. No Streamlit Cloud, vá em Settings → Secrets e adicione:
    
    ```toml
    [supabase]
    url = "https://seu-projeto.supabase.co"
    key = "sua-chave-anon"
    
    APP_URL = "https://seu-app.streamlit.app"
    ```
    
    5. No SQL Editor do Supabase, execute:
    
    ```sql
    CREATE TABLE historico_financeiro (
        id SERIAL PRIMARY KEY,
        data DATE UNIQUE NOT NULL,
        total_geral DECIMAL(15,2),
        total_assistencia DECIMAL(15,2),
        total_lojas DECIMAL(15,2),
        total_a_vista DECIMAL(15,2),
        total_boleto DECIMAL(15,2),
        total_comercial DECIMAL(15,2),
        qtd_notas INTEGER,
        created_at TIMESTAMP DEFAULT NOW()
    );
    ```
    """)
    st.stop()

# ── PARÂMETROS DA URL E AUTH ──────────────────────────────────────────────────
query_params = st.query_params
token_rep = query_params.get("token")
data_filtro_url = query_params.get("data")

representante_logado = None
if token_rep:
    representante_logado = validar_token(token_rep)
    if representante_logado:
        st.sidebar.success(f"✅ Acesso: {representante_logado['nome']}")
        if representante_logado.get("fonte"):
            st.sidebar.caption(f"Fonte: {representante_logado['fonte']}")
    else:
        st.sidebar.error("❌ Token inválido ou expirado")

# ── DEBUG MODE ────────────────────────────────────────────────────────────────
if "debug" in query_params:
    with st.expander("🔧 DEBUG MODE", expanded=True):
        st.markdown('<div class="debug-box">', unsafe_allow_html=True)
        st.write("**Query params:**", dict(query_params))
        st.write("**Token válido?**", validar_token(token_rep) is not None)
        st.write("**APP_URL:**", APP_URL)
        st.write("**Supabase conectado:**", supabase is not None)
        st.markdown('</div>', unsafe_allow_html=True)

# ── ABAS PRINCIPAIS ───────────────────────────────────────────────────────────
aba_hoje, aba_historico = st.tabs(["📋 Relatório do Dia", "📅 Histórico"])

# ═════════════════════════════════════════════════════════════════════════════
# ABA 1 — RELATÓRIO DO DIA
# ═════════════════════════════════════════════════════════════════════════════
uploaded_file = None 
with aba_hoje:
    
    if representante_logado and not uploaded_file:
        st.info("📁 Faça upload do arquivo do dia para visualizar seus pedidos.")
        uploaded_file = st.file_uploader("Selecionar arquivo .xlsx do Sankhya", type=["xlsx", "xls"])
        if uploaded_file:
            try:
                df_raw = load_data(uploaded_file)
                totais, df = calcular_totais(df_raw)
                visualizar_view_representante(df, representante_logado, data_filtro_url)
            except Exception as e:
                st.error(f"Erro ao processar arquivo: {e}")
        st.stop()
    
    st.markdown('<span class="upload-label">&#128194; Selecionar arquivo</span>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["xlsx", "xls"], label_visibility="collapsed")

    if uploaded_file:
        try:
            df_raw = load_data(uploaded_file)
            totais, df = calcular_totais(df_raw)
            t = totais

            CATEGORIAS_EXTRA = ["Atacado", "Credimoveis", "Carajás", "Outro"]
            CORES_EXTRA = {"Atacado": "#1abc9c", "Credimoveis": "#e74c3c", "Carajás": "#f39c12", "Outro": "#7f8c8d"}

            if "extras" not in st.session_state:
                st.session_state.extras = []

            with st.expander("➕ Adicionar valor extra (notas já faturadas fora da planilha)"):
                col_e1, col_e2, col_e3, col_e4 = st.columns([2, 2, 3, 1])
                with col_e1:
                    extra_cat = st.selectbox("Categoria", CATEGORIAS_EXTRA, key="extra_cat")
                with col_e2:
                    extra_val = st.number_input("Valor (R$)", min_value=0.0, step=100.0, format="%.2f", key="extra_val")
                with col_e3:
                    extra_obs = st.text_input("Observação (opcional)", key="extra_obs")
                with col_e4:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Adicionar"):
                        if extra_val > 0:
                            st.session_state.extras.append({"categoria": extra_cat, "valor": extra_val, "obs": extra_obs})
                            st.rerun()
                if st.session_state.extras:
                    st.markdown("**Valores adicionados:**")
                    for i, ex in enumerate(st.session_state.extras):
                        c1, c2 = st.columns([5, 1])
                        with c1:
                            obs_txt = f" — {ex['obs']}" if ex['obs'] else ""
                            st.markdown(f"• **{ex['categoria']}**: {format_brl(ex['valor'])}{obs_txt}")
                        with c2:
                            if st.button("🗑️", key=f"del_extra_{i}"):
                                st.session_state.extras.pop(i)
                                st.rerun()
                    if st.button("🗑️ Limpar todos"):
                        st.session_state.extras = []
                        st.rerun()

            extras_por_cat = {}
            for ex in st.session_state.extras:
                extras_por_cat[ex["categoria"]] = extras_por_cat.get(ex["categoria"], 0) + ex["valor"]
            total_extras = sum(extras_por_cat.values())
            total_geral_ajustado = t["total_geral"] + total_extras
            pct = lambda v: f"{v/total_geral_ajustado*100:.1f}% do total" if total_geral_ajustado else "—"

            col_data, col_salvar = st.columns([1, 2])
            with col_data:
                data_ref = st.date_input("📅 Data de referência deste relatório", value=datetime.today())
            with col_salvar:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("💾  Salvar no histórico"):
                    t_salvar = {**t, "total_geral": total_geral_ajustado}
                    salvo = salvar_historico(data_ref, t_salvar, extras_por_cat)
                    if salvo:
                        st.markdown('<div class="success-box"><strong>✅ Salvo com sucesso no Supabase!</strong><br>Os dados estão permanentemente armazenados no banco de dados.</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="already-badge">⚠️ Já existe um registro para essa data.</span>', unsafe_allow_html=True)

            # ── KPI Cards (7 colunas com Cheque) ──
            cards_extras_html = ""
            for cat, val in extras_por_cat.items():
                cor = CORES_EXTRA.get(cat, "#7f8c8d")
                cards_extras_html += (
                    f'<div class="kpi-card" style="border-top:4px solid {cor};">'
                    f'<div class="kpi-label">&#128230; {cat}</div>'
                    f'<div class="kpi-value">{format_brl(val)}</div>'
                    f'<span class="kpi-badge">{pct(val)}</span>'
                    f'</div>'
                )

            df["_is_cheque"] = df["Descrição (Tipo de Negociação)"].str.upper().str.contains("CHEQUE", na=False)
            total_cheque = df[df["_is_cheque"]]["Vlr. Nota"].sum()

            st.markdown(
                '<div class="kpi-grid" style="grid-template-columns: repeat(7, 1fr);">'
                '<div class="kpi-card total"><div class="kpi-label">&#128176; Total Geral</div>'
                f'<div class="kpi-value">{format_brl(total_geral_ajustado)}</div><span class="kpi-badge">{t["qtd_notas"]} notas</span></div>'
                '<div class="kpi-card assist"><div class="kpi-label">&#128296; Assistência</div>'
                f'<div class="kpi-value">{format_brl(t["total_assistencia"])}</div><span class="kpi-badge">{pct(t["total_assistencia"])}</span></div>'
                '<div class="kpi-card lojas"><div class="kpi-label">&#127978; Lojas</div>'
                f'<div class="kpi-value">{format_brl(t["total_lojas"])}</div><span class="kpi-badge">{pct(t["total_lojas"])}</span></div>'
                '<div class="kpi-card avista"><div class="kpi-label">&#128181; À Vista</div>'
                f'<div class="kpi-value">{format_brl(t["total_a_vista"])}</div><span class="kpi-badge">{pct(t["total_a_vista"])}</span></div>'
                '<div class="kpi-card boleto"><div class="kpi-label">&#128196; Boleto</div>'
                f'<div class="kpi-value">{format_brl(t["total_boleto"])}</div><span class="kpi-badge">{pct(t["total_boleto"])}</span></div>'
                '<div class="kpi-card comercial"><div class="kpi-label">&#129309; Comercial</div>'
                f'<div class="kpi-value">{format_brl(t["total_comercial"])}</div><span class="kpi-badge">{pct(t["total_comercial"])}</span></div>'
                f'<div class="kpi-card cheque"><div class="kpi-label">&#128179; Cheque</div><div class="kpi-value">{format_brl(total_cheque)}</div><span class="kpi-badge">{pct(total_cheque)}</span></div>'
                + cards_extras_html + '</div>',
                unsafe_allow_html=True
            )

            # ── Mix de Faturamento ──
            st.markdown('<div class="sec-title">&#129383; Mix de Faturamento</div>', unsafe_allow_html=True)
            total_outros = max(t["total_geral"] - (t["total_assistencia"] + t["total_lojas"] + t["total_a_vista"] + t["total_boleto"] + total_cheque), 0)
            mix_labels = ["Boleto", "Lojas", "À Vista", "Assistência", "Cheque", "Outros"]
            mix_values = [t["total_boleto"], t["total_lojas"], t["total_a_vista"], t["total_assistencia"], total_cheque, total_outros]
            mix_cores = ["#2980b9", "#2ecc71", "#8e44ad", "#e07b3a", "#e74c3c", "#95a5a6"]
            for cat, val in extras_por_cat.items():
                mix_labels.append(cat); mix_values.append(val); mix_cores.append(CORES_EXTRA.get(cat, "#7f8c8d"))
            mix_df = pd.DataFrame({"Categoria": mix_labels, "Valor": mix_values, "Cor": mix_cores})
            mix_df = mix_df[mix_df["Valor"] > 0].reset_index(drop=True)
            col_chart, col_table = st.columns([1.4, 1])
            with col_chart:
                fig_mix = go.Figure(go.Pie(labels=mix_df["Categoria"], values=mix_df["Valor"], hole=0.52, marker=dict(colors=mix_df["Cor"].tolist()), textposition="outside", textinfo="label+percent", hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>"))
                fig_mix.update_layout(margin=dict(t=30, b=30, l=20, r=20), showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter, sans-serif", size=12), height=400)
                st.plotly_chart(fig_mix, use_container_width=True)
            with col_table:
                mix_tbl = mix_df[["Categoria", "Valor"]].copy()
                mix_tbl["% do Total"] = (mix_tbl["Valor"] / total_geral_ajustado * 100).map("{:.1f}%".format)
                mix_tbl["Valor"] = mix_tbl["Valor"].map(format_brl)
                st.dataframe(mix_tbl, use_container_width=True, hide_index=True, height=400)

            resumo_neg = df.groupby("Descrição (Tipo de Negociação)")["Vlr. Nota"].agg(Qtd="count", Total="sum").sort_values("Total", ascending=False).reset_index()
            resumo_neg_tbl = resumo_neg.copy()
            resumo_neg_tbl["% do Total"] = (resumo_neg_tbl["Total"] / t["total_geral"] * 100).map("{:.1f}%".format)
            resumo_neg_tbl["Total"] = resumo_neg_tbl["Total"].map(format_brl)

            # ── Notas Assistência ──
            st.markdown('<div class="sec-title">&#128296; Notas de Assistência</div>', unsafe_allow_html=True)
            df_assist = df[df["_is_assistencia"]][["Nro. Nota", "Dt. Neg.", "Nome Parceiro (Parceiro)", "Vlr. Nota", "Descrição (Tipo de Negociação)", "Apelido (Vendedor)"]].copy()
            df_assist["Vlr. Nota"] = df_assist["Vlr. Nota"].map(format_brl)
            df_assist["Dt. Neg."] = pd.to_datetime(df_assist["Dt. Neg."], errors="coerce").dt.strftime("%d/%m/%Y")
            st.dataframe(df_assist.rename(columns={"Nro. Nota": "Nota", "Dt. Neg.": "Data", "Nome Parceiro (Parceiro)": "Parceiro", "Descrição (Tipo de Negociação)": "Tipo Neg.", "Apelido (Vendedor)": "Vendedor"}), use_container_width=True, hide_index=True)

            # ── Tabela Completa de Pedidos ──
            st.markdown('<div class="sec-title">&#128203; Todos os Pedidos da Produção</div>', unsafe_allow_html=True)
            col_f1, col_f2, col_f3 = st.columns([2, 2, 2])
            with col_f1:
                busca = st.text_input("🔍 Buscar parceiro ou nº único", placeholder="Ex: Magazine, 12345...")
            with col_f2:
                regioes_disponiveis = sorted(df["Regiao Vendedor"].dropna().unique().tolist())
                filtro_regioes = st.multiselect("Região", options=regioes_disponiveis, default=regioes_disponiveis, placeholder="Selecione uma ou mais...")
            with col_f3:
                negociacoes = ["Todas"] + sorted(df["Descrição (Tipo de Negociação)"].dropna().unique().tolist())
                filtro_neg = st.selectbox("Tipo de Negociação", negociacoes)

            df_tabela = df.copy()
            if busca:
                mask_busca = df_tabela["Nome Parceiro (Parceiro)"].str.contains(busca, case=False, na=False) | df_tabela["Nro. Único"].astype(str).str.contains(busca, case=False, na=False)
                df_tabela = df_tabela[mask_busca]
            if filtro_regioes:
                df_tabela = df_tabela[df_tabela["Regiao Vendedor"].isin(filtro_regioes)]
            if filtro_neg != "Todas":
                df_tabela = df_tabela[df_tabela["Descrição (Tipo de Negociação)"] == filtro_neg]

            df_exibir = df_tabela[["Nro. Único", "Previsão de entrega", "Nome Parceiro (Parceiro)", "Vlr. Nota", "Descrição (Tipo de Negociação)", "Descrição (Tipo de Operação)", "Apelido (Vendedor)", "Regiao Vendedor"]].copy()
            df_exibir["Previsão de entrega"] = pd.to_datetime(df_exibir["Previsão de entrega"], errors="coerce").dt.strftime("%d/%m/%Y")
            df_exibir["Vlr. Nota"] = df_exibir["Vlr. Nota"].map(format_brl)
            st.caption(f"Exibindo **{len(df_exibir)}** pedido(s)")
            st.dataframe(df_exibir.rename(columns={"Nro. Único": "Nº Único", "Previsão de entrega": "Prev. Entrega", "Nome Parceiro (Parceiro)": "Parceiro", "Vlr. Nota": "Valor", "Descrição (Tipo de Negociação)": "Negociação", "Descrição (Tipo de Operação)": "Operação", "Apelido (Vendedor)": "Vendedor", "Regiao Vendedor": "Região"}), use_container_width=True, hide_index=True, height=420)

            # ── Export ──
            st.markdown('<div class="sec-title">&#11015;&#65039; Exportar</div>', unsafe_allow_html=True)
            categorias_export = ["Total Geral", "Assistência", "Lojas", "À Vista", "Boleto", "Comercial", "Cheque"]
            valores_export = [total_geral_ajustado, t["total_assistencia"], t["total_lojas"], t["total_a_vista"], t["total_boleto"], t["total_comercial"], total_cheque]
            for cat, val in extras_por_cat.items():
                categorias_export.append(cat); valores_export.append(val)
            resumo_export = pd.DataFrame({"Categoria": categorias_export, "Valor": valores_export})
            resumo_export["% do Total"] = (resumo_export["Valor"] / total_geral_ajustado * 100).round(2)
            resumo_export["Valor"] = resumo_export["Valor"].map(format_brl)
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                resumo_export.to_excel(writer, sheet_name="Resumo", index=False)
                resumo_neg_tbl.to_excel(writer, sheet_name="Por Negociação", index=False)
            st.download_button(label="⬇️ Baixar Resumo em Excel", data=buffer.getvalue(), file_name=f"resumo_financeiro_{data_ref.strftime('%d-%m-%Y')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")
    else:
        st.markdown("""
        <div class="info-box"><strong>Como usar:</strong> faça o upload do arquivo <code>.xlsx</code> exportado do Sankhya e clique em <strong>Salvar no histórico</strong>.<br><br>
        💾 <strong>Os dados são salvos no Supabase</strong> e permanecem disponíveis permanentemente!</div>
        """, unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# ABA 2 — HISTÓRICO (COM SUPABASE)
# ═════════════════════════════════════════════════════════════════════════════
with aba_historico:
    hist = carregar_historico()
    if hist.empty:
        st.info("📭 Nenhum histórico ainda. Faça upload e clique em **Salvar no histórico**.")
    else:
        hist["data_dt"] = pd.to_datetime(hist["data"], format="%Y-%m-%d", errors="coerce")
        hist_sorted = hist.sort_values("data_dt")
        st.markdown('<div class="sec-title">&#128197; Filtrar período</div>', unsafe_allow_html=True)
        col_de, col_ate = st.columns(2)
        with col_de:
            data_de = st.date_input("De", value=hist_sorted["data_dt"].min().date() if not hist_sorted.empty else datetime.today().date())
        with col_ate:
            data_ate = st.date_input("Até", value=hist_sorted["data_dt"].max().date() if not hist_sorted.empty else datetime.today().date())
        mask = (hist_sorted["data_dt"].dt.date >= data_de) & (hist_sorted["data_dt"].dt.date <= data_ate)
        h = hist_sorted[mask].copy()
        if h.empty:
            st.warning("⚠️ Nenhum registro no período selecionado.")
        else:
            h["data_fmt"] = h["data_dt"].dt.strftime("%d/%m/%Y")
            st.markdown('<div class="sec-title">&#128202; Comparativo por Período</div>', unsafe_allow_html=True)
            categorias_hist = {"Total Geral": ("total_geral", "#0f2942"), "Comercial": ("total_comercial", "#d4a017"), "Lojas": ("total_lojas", "#2ecc71"), "Boleto": ("total_boleto", "#2980b9"), "À Vista": ("total_a_vista", "#8e44ad"), "Assistência": ("total_assistencia", "#e07b3a")}
            opcoes = st.multiselect("Selecionar categorias:", options=list(categorias_hist.keys()), default=["Total Geral", "Comercial", "Lojas", "Boleto"])
            if opcoes:
                fig = go.Figure()
                for nome in opcoes:
                    col_key, cor = categorias_hist[nome]
                    if col_key in h.columns:
                        fig.add_trace(go.Bar(name=nome, x=h["data_fmt"], y=h[col_key], marker_color=cor, hovertemplate=f"<b>{nome}</b><br>%{{x}}<br>R$ %{{y:,.2f}}<extra></extra>"))
                fig.update_layout(barmode="group", xaxis_title="Data", yaxis_title="Valor (R$)", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter, sans-serif", size=12), legend=dict(orientation="h", y=-0.2), margin=dict(t=20, b=60, l=20, r=20), height=420)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('<div class="sec-title">&#128203; Tabela de Registros</div>', unsafe_allow_html=True)
            
            cols_base = ["data_fmt", "total_geral", "total_assistencia", "total_lojas", "total_a_vista", "total_boleto", "total_comercial"]
            cols_extras = [c for c in h.columns if c.startswith("extra_")]
            cols_tabela = [c for c in cols_base if c in h.columns] + cols_extras
            
            tbl = h[cols_tabela].copy()
            
            for c in ["total_geral", "total_assistencia", "total_lojas", "total_a_vista", "total_boleto", "total_comercial"] + cols_extras:
                if c in tbl.columns:
                    tbl[c] = pd.to_numeric(tbl[c], errors="coerce").map(format_brl)
            
            rename_map = {"data_fmt": "Data", "total_geral": "Total Geral", "total_assistencia": "Assistência", "total_lojas": "Lojas", "total_a_vista": "À Vista", "total_boleto": "Boleto", "total_comercial": "Comercial"}
            for c in cols_extras:
                rename_map[c] = c.replace("extra_", "").replace("_", " ").title()
            
            tbl = tbl.rename(columns={k: v for k, v in rename_map.items() if k in tbl.columns})
            st.dataframe(tbl, use_container_width=True, hide_index=True)
            
            st.markdown('<div class="sec-title">&#11015;&#65039; Exportar Histórico</div>', unsafe_allow_html=True)
            buf_hist = io.BytesIO()
            tbl.to_excel(buf_hist, index=False, engine="openpyxl")
            st.download_button(label="⬇️ Baixar Histórico em Excel", data=buf_hist.getvalue(), file_name=f"historico_financeiro_{data_de}_{data_ate}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            
            with st.expander("🗑️ Remover um registro"):
                datas_disp = h["data_fmt"].tolist()
                data_del = st.selectbox("Selecione a data para remover:", datas_disp)
                if st.button("Remover"):
                    data_del_iso = pd.to_datetime(data_del, format="%d/%m/%Y", errors="coerce").strftime("%Y-%m-%d")
                    deletado = deletar_registro_historico(data_del_iso)
                    if deletado:
                        st.success(f"✅ Registro de {data_del} removido do banco de dados.")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao remover registro.")

# ═════════════════════════════════════════════════════════════════════════════
# SIDEBAR: GERENCIAMENTO DE REPRESENTANTES
# ═════════════════════════════════════════════════════════════════════════════
if not representante_logado:
    with st.sidebar:
        st.markdown("### 🔐 Área Administrativa")
        with st.expander("👥 Gerenciar Representantes", expanded=True):
            reps_secrets = carregar_representantes_secrets()
            reps_csv = carregar_representantes_csv()
            all_reps = {**reps_secrets, **reps_csv}
            st.info("💡 No Cloud, configure tokens em **Settings → Secrets**.")
            with st.form("novo_rep"):
                st.markdown("**Cadastrar novo representante**")
                novo_nome = st.text_input("Nome completo")
                novo_regioes = st.multiselect("Regiões de acesso", options=["REGIAO 1", "REGIAO 2", "REGIAO 3", "REGIAO 4", "LOJAS", "ATACADO"])
                submit_rep = st.form_submit_button("Gerar token")
                if submit_rep and novo_nome:
                    token = gerar_token(novo_nome)
                    regioes_str = ";".join(novo_regioes)
                    salvar_representantes_csv(token, novo_nome, regioes_str)
                    link_representante = f"{APP_URL}/?token={token}"
                    st.success(f"✅ Token gerado para {novo_nome}!")
                    st.markdown("**🔗 Link de acesso:**")
                    st.text_input("📋 Clique para copiar:", value=link_representante, label_visibility="collapsed")
                    with st.expander("📋 Como usar"):
                        st.markdown(f"1. Copie o link\n2. Envie para **{novo_nome}**\n3. Ele verá apenas pedidos das regiões: {', '.join(novo_regioes) if novo_regioes else 'Todas'}")
                    st.warning(f"⚠️ Para Cloud, adicione em Secrets:\n```toml\n[representantes]\n\"{token}\" = \"{novo_nome}|{regioes_str}\"\n```")
            if all_reps:
                st.markdown("---")
                st.markdown(f"**Representantes** ({len(all_reps)}):")
                for token, rep in all_reps.items():
                    status = "🟢" if rep["ativo"] else "🔴"
                    fonte = "🔐 Cloud" if rep.get("fonte") == "secrets" else "💻 Local"
                    with st.container():
                        st.markdown(f"{status} **{rep['nome']}** {fonte}<br><small>Regiões: {', '.join(rep['regioes']) if rep['regioes'] else 'Todas'}</small>", unsafe_allow_html=True)
                        st.text_input(f"Link:", value=f"{APP_URL}/?token={token}", label_visibility="collapsed", key=f"link_{token}")
                        if st.button("📋 Copiar config", key=f"copy_{token}"):
                            st.code(f'"{token}" = "{rep["nome"]}|{";".join(rep["regioes"])}"', language="toml")