import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
import os
from fpdf import FPDF
from datetime import datetime, date
import base64
import hashlib
import re
import json
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

REPRESENTANTES_DB = "representantes.csv"

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
    # Exclui cheques e à vista
    if "CHEQUE" in t or "À VISTA" in t or "A VISTA" in t or "PIX" in t or "CARTÃO" in t:
        return False
    return bool("DIAS" in t or "GRANDES REDES" in t or re.search(r'\d+/\d+', t))

def is_a_vista(tipo):
    t = str(tipo).upper()
    return ("À VISTA" in t or "A VISTA" in t) if pd.notna(tipo) else False

def load_data(file):
    df = pd.read_excel(file, header=2)
    
    # Remove linhas onde "Nro. Único" é NaN ou vazio (linhas de total/cabeçalho)
    df = df[df["Nro. Único"].notna()].copy()
    df = df[df["Nro. Único"] != ""].copy()
    
    # Remove linhas que parecem ser totais (onde "Nro. Único" é numérico mas muito grande ou texto de total)
    df = df[~df["Nro. Único"].astype(str).str.contains("TOTAL|total|Total", na=False)].copy()
    
    # Converte valor da nota para numérico
    df["Vlr. Nota"] = pd.to_numeric(df["Vlr. Nota"], errors="coerce").fillna(0)
    
    # Remove linhas com valor zero ou negativo (linhas de formatação)
    df = df[df["Vlr. Nota"] > 0].copy()
    
    return df

def calcular_totais(df):
    # Flags de identificação
    df["_is_assistencia"] = df["Descrição (Tipo de Operação)"].str.upper().str.contains("ASSISTENCIA", na=False)
    df["_is_loja"]        = df["Regiao Vendedor"].str.upper().str.strip() == "LOJAS"
    df["_is_a_vista"]     = df["Descrição (Tipo de Negociação)"].apply(is_a_vista)
    df["_is_boleto"]      = df["Descrição (Tipo de Negociação)"].apply(is_boleto)
    
    # ✅ Comercial agora inclui: REGIAO *qualquer* + DIRETORIA
    df["_is_comercial"] = (
        df["Regiao Vendedor"].str.upper().str.contains("REGIAO", na=False) | 
        df["Regiao Vendedor"].str.upper().str.strip() == "DIRETORIA"
    )
    
    # ✅ À Vista APENAS do Comercial específico (Regiões 1, 2, 3 e Diretoria)
    regioes_comercial_avista = ["REGIAO 1", "REGIAO 2", "REGIAO 3", "DIRETORIA"]
    df["_is_comercial_avista"] = (
        df["_is_a_vista"] & 
        df["Regiao Vendedor"].str.upper().str.strip().isin(regioes_comercial_avista)
    )
    
    return {
        "total_geral":         df["Vlr. Nota"].sum(),
        "total_assistencia":   df[df["_is_assistencia"]]["Vlr. Nota"].sum(),
        "total_lojas":         df[df["_is_loja"]]["Vlr. Nota"].sum(),
        
        # ✅ À Vista filtrado por regiões comerciais específicas
        "total_a_vista":       df[df["_is_comercial_avista"]]["Vlr. Nota"].sum(),
        
        "total_boleto":        df[df["_is_boleto"]]["Vlr. Nota"].sum(),
        
        # ✅ Comercial: Regiões + Diretoria + Assistência
        "total_comercial":     df[(df["_is_comercial"]) | (df["_is_assistencia"])]["Vlr. Nota"].sum(),
        
        "qtd_notas":           len(df),
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
        response = supabase.table("historico_financeiro").select("*").order("data").execute()
        if not response.data:
            return pd.DataFrame()
        df = pd.DataFrame(response.data)
        if "data" in df.columns:
            df["data"] = pd.to_datetime(df["data"], errors="coerce").dt.strftime("%Y-%m-%d")
        df = df.fillna(0)
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar histórico: {e}")
        return pd.DataFrame()

def salvar_historico(data_ref, totais, extras_por_cat=None, total_cheque=0):
    """Salva histórico no Supabase incluindo total_cheque"""
    if supabase is None:
        st.error("❌ Supabase não conectado")
        return False
    try:
        data_str = data_ref.strftime("%Y-%m-%d")
        existing = supabase.table("historico_financeiro").select("data").eq("data", data_str).execute()
        if existing.data:
            supabase.table("historico_financeiro").delete().eq("data", data_str).execute()
        novo_registro = {"data": data_str, **totais, "total_cheque": float(total_cheque)}
        if extras_por_cat:
            for cat, val in extras_por_cat.items():
                col_name = _normalize_col_name(cat)
                novo_registro[col_name] = float(val)
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

# ── FUNÇÃO PARA GERAR PDF DOS PEDIDOS ─────────────────────────────────────────
def gerar_pdf_pedidos(df_pedidos, data_referencia):
    """Gera PDF dos pedidos centralizado com Logo"""
    pdf = FPDF()
    pdf.add_page()
    
    # --- 1. ADICIONAR LOGO ---
    try:
        logo_path = "logo-bonsono.png"
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=85, y=10, w=40) 
            pdf.ln(25)
        else:
            pdf.ln(10)
    except Exception:
        pdf.ln(10)

    # --- 2. TÍTULO ---
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Pedidos na produção de - {data_referencia.strftime('%d/%m/%Y')}", ln=True, align='C')
    pdf.ln(5)
    
    # --- 3. INFORMAÇÕES GERAIS ---
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 8, f"Total de pedidos: {len(df_pedidos)}", ln=True, align='C')
    pdf.ln(5)
    
    # --- 4. CONFIGURAÇÃO DA TABELA ---
    pdf.set_font("Arial", 'B', 8)
    
    cols = ["Nro. Único", "Previsão de entrega", "Nome Parceiro (Parceiro)", 
            "Vlr. Nota", "Apelido (Vendedor)", "Regiao Vendedor"]
    cols_existentes = [c for c in cols if c in df_pedidos.columns]
    
    larguras = [22, 25, 65, 28, 35, 25]
    larguras = [l for i, l in enumerate(larguras) if i < len(cols_existentes)]
    largura_total_tabela = sum(larguras)
    
    headers = {"Nro. Único": "Nº", "Previsão de entrega": "Data de produção", 
               "Nome Parceiro (Parceiro)": "Parceiro", "Vlr. Nota": "Valor",
               "Apelido (Vendedor)": "Vendedor", "Regiao Vendedor": "Região"}
    
    # --- 5. DESENHAR TABELA CENTRALIZADA ---
    x_inicio = (210 - largura_total_tabela) / 2
    
    pdf.set_xy(x_inicio, pdf.get_y())
    pdf.set_fill_color(230, 240, 250)
    
    # Cabeçalho
    for i, col in enumerate(cols_existentes):
        pdf.cell(larguras[i], 8, headers.get(col, col), border=1, align='C', fill=True)
    pdf.ln()
    
    # Dados
    pdf.set_font("Arial", size=7)
    for _, row in df_pedidos.iterrows():
        pdf.set_x(x_inicio)
        
        for i, col in enumerate(cols_existentes):
            valor = row[col] if pd.notna(row[col]) else ""
            
            if col == "Previsão de entrega":
                try:
                    valor = pd.to_datetime(valor).strftime("%d/%m/%Y")
                except:
                    valor = ""
            elif col == "Vlr. Nota":
                try:
                    valor = f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                except:
                    valor = "R$ 0,00"
            
            # Truncar e normalizar texto
            valor_str = str(valor)[:30] if len(str(valor)) > 30 else str(valor)
            
            # Normalizar caracteres especiais para ASCII
            try:
                valor_str = valor_str.encode('latin-1', 'replace').decode('latin-1')
            except:
                pass
            
            pdf.cell(larguras[i], 6, valor_str, border=1, align='L')
        pdf.ln()
    
    # --- 6. RODAPÉ ---
    pdf.ln(5)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 6, f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')} - Sistema Bonsono", ln=True, align='C')
    
    # --- 7. RETORNAR PDF CORRETAMENTE ---
    pdf_bytes = pdf.output(dest='S')
    
    if isinstance(pdf_bytes, (bytes, bytearray)):
        return bytes(pdf_bytes)
    else:
        return pdf_bytes.encode('latin-1', errors='replace')
    
# ── NOVAS FUNÇÕES: PEDIDOS DETALHADOS ─────────────────────────────────────────
def salvar_pedidos_detalhados(data_ref, df_pedidos):
    """Salva os pedidos detalhados no Supabase como JSON"""
    if supabase is None:
        return False
    
    try:
        cols_temp = [c for c in df_pedidos.columns if c.startswith("_is_")]
        df_clean = df_pedidos.drop(columns=cols_temp, errors="ignore")
        pedidos_json = df_clean.to_json(orient="records", force_ascii=False, date_format="iso")
        
        existing = supabase.table("historico_pedidos").select("id").eq("data_referencia", data_ref.strftime("%Y-%m-%d")).execute()
        if existing.data:
            supabase.table("historico_pedidos").delete().eq("data_referencia", data_ref.strftime("%Y-%m-%d")).execute()
        
        supabase.table("historico_pedidos").insert({
            "data_referencia": data_ref.strftime("%Y-%m-%d"),
            "pedido_json": pedidos_json
        }).execute()
        return True
    except Exception as e:
        st.error(f"❌ Erro ao salvar pedidos: {e}")
        return False

def carregar_pedidos_historico(data_ref):
    """Carrega os pedidos de uma data específica do histórico"""
    if supabase is None:
        return pd.DataFrame()
    
    try:
        response = supabase.table("historico_pedidos").select("pedido_json").eq("data_referencia", data_ref.strftime("%Y-%m-%d")).execute()
        
        if not response.data:
            return pd.DataFrame()
        
        pedidos_list = json.loads(response.data[0]["pedido_json"])
        return pd.DataFrame(pedidos_list)
    except Exception as e:
        st.error(f"❌ Erro ao carregar pedidos: {e}")
        return pd.DataFrame()

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
    <img class="header-logo" src="data:image/png;base64,{logo_b64}" />
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
    5. No SQL Editor do Supabase, execute o script de criação das tabelas:
    ```sql
    CREATE TABLE IF NOT EXISTS historico_financeiro (
        data DATE PRIMARY KEY,
        total_geral FLOAT,
        total_assistencia FLOAT,
        total_lojas FLOAT,
        total_a_vista FLOAT,
        total_boleto FLOAT,
        total_comercial FLOAT,
        total_cheque FLOAT,
        qtd_notas INTEGER
    );
    
    CREATE TABLE IF NOT EXISTS historico_pedidos (
        id BIGSERIAL PRIMARY KEY,
        data_referencia DATE NOT NULL,
        pedido_json JSONB NOT NULL,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    CREATE INDEX idx_data_pedidos ON historico_pedidos (data_referencia);
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
# ABA 1 — RELATÓRIO DO DIA (COM CONSULTA DE PEDIDOS DO HISTÓRICO)
# ═════════════════════════════════════════════════════════════════════════════
uploaded_file = None 
with aba_hoje:
    # Lógica para representantes logados
    if representante_logado and not uploaded_file:
        st.info("📁 Faça upload do arquivo do dia para visualizar seus pedidos.")
        uploaded_file = st.file_uploader("Selecionar arquivo .xlsx do Sankhya", type=["xlsx", "xls"], key="upload_rep")
        if uploaded_file:
            try:
                df_raw = load_data(uploaded_file)
                totais, df = calcular_totais(df_raw)
                visualizar_view_representante(df, representante_logado, data_filtro_url)
            except Exception as e:
                st.error(f"Erro ao processar arquivo: {e}")
        st.stop()
    
    # Upload para usuários normais
    st.markdown('<span class="upload-label">&#128194; Selecionar arquivo do dia</span>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["xlsx", "xls"], label_visibility="collapsed", key="upload_normal")

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
                    extra_cat = st.selectbox("Categoria", CATEGORIAS_EXTRA, key="extra_cat_dia")
                with col_e2:
                    extra_val = st.number_input("Valor (R$)", min_value=0.0, step=100.0, format="%.2f", key="extra_val_dia")
                with col_e3:
                    extra_obs = st.text_input("Observação (opcional)", key="extra_obs_dia")
                with col_e4:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Adicionar", key="btn_add_extra"):
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
                            if st.button("🗑️", key=f"del_extra_dia_{i}"):
                                st.session_state.extras.pop(i)
                                st.rerun()
                    if st.button("🗑️ Limpar todos", key="btn_limpar_extras"):
                        st.session_state.extras = []
                        st.rerun()

            extras_por_cat = {}
            for ex in st.session_state.extras:
                extras_por_cat[ex["categoria"]] = extras_por_cat.get(ex["categoria"], 0) + ex["valor"]
            total_extras = sum(extras_por_cat.values())
            total_geral_ajustado = t["total_geral"] + total_extras
            pct = lambda v: f"{v/total_geral_ajustado*100:.1f}% do total" if total_geral_ajustado else "—"

            df["_is_cheque"] = df["Descrição (Tipo de Negociação)"].str.upper().str.contains("CHEQUE", na=False)
            total_cheque = df[df["_is_cheque"]]["Vlr. Nota"].sum()

            col_data, col_salvar = st.columns([1, 2])
            with col_data:
                data_ref = st.date_input("📅 Data de referência deste relatório", value=datetime.today(), key="data_ref_dia")
            with col_salvar:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("💾  Salvar no histórico", key="btn_salvar_hist"):
                    t_salvar = {**t, "total_geral": total_geral_ajustado}
                    salvo = salvar_historico(data_ref, t_salvar, extras_por_cat, total_cheque)
                    pedidos_salvos = salvar_pedidos_detalhados(data_ref, df)
                    
                    if salvo and pedidos_salvos:
                        st.markdown(f'<div class="success-box"><strong>✅ Salvo com sucesso no Supabase!</strong><br>• Totais agregados<br>• <strong>{len(df)} pedidos detalhados</strong></div>', unsafe_allow_html=True)
                    elif salvo:
                        st.markdown('<span class="already-badge">⚠️ Totais salvos, mas houve erro ao salvar os detalhes dos pedidos.</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="already-badge">⚠️ Já existe um registro para essa data ou erro ao salvar.</span>', unsafe_allow_html=True)

            # KPI Cards
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

            # Mix de Faturamento
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

            # Notas de Assistência
            st.markdown('<div class="sec-title">&#128296; Notas de Assistência</div>', unsafe_allow_html=True)
            df_assist = df[df["_is_assistencia"]][["Nro. Nota", "Dt. Neg.", "Nome Parceiro (Parceiro)", "Vlr. Nota", "Descrição (Tipo de Negociação)", "Apelido (Vendedor)"]].copy()
            df_assist["Vlr. Nota"] = df_assist["Vlr. Nota"].map(format_brl)
            df_assist["Dt. Neg."] = pd.to_datetime(df_assist["Dt. Neg."], errors="coerce").dt.strftime("%d/%m/%Y")
            st.dataframe(df_assist.rename(columns={"Nro. Nota": "Nota", "Dt. Neg.": "Data", "Nome Parceiro (Parceiro)": "Parceiro", "Descrição (Tipo de Negociação)": "Tipo Neg.", "Apelido (Vendedor)": "Vendedor"}), use_container_width=True, hide_index=True)

            # Tabela Completa de Pedidos
            st.markdown('<div class="sec-title">&#128203; Todos os Pedidos da Produção</div>', unsafe_allow_html=True)
            col_f1, col_f2, col_f3 = st.columns([2, 2, 2])
            with col_f1:
                busca = st.text_input("🔍 Buscar parceiro ou nº único", placeholder="Ex: Magazine, 12345...", key="busca_dia")
            with col_f2:
                regioes_disponiveis = sorted(df["Regiao Vendedor"].dropna().unique().tolist())
                filtro_regioes = st.multiselect("Região", options=regioes_disponiveis, default=regioes_disponiveis, placeholder="Selecione...", key="filtro_reg_dia")
            with col_f3:
                operacoes = ["Todas"] + sorted(df["Descrição (Tipo de Operação)"].dropna().unique().tolist())
                filtro_op = st.selectbox("Operação", operacoes, key="filtro_op_dia")

            df_tabela = df.copy()
            if busca:
                mask_busca = df_tabela["Nome Parceiro (Parceiro)"].str.contains(busca, case=False, na=False) | df_tabela["Nro. Único"].astype(str).str.contains(busca, case=False, na=False)
                df_tabela = df_tabela[mask_busca]
            if filtro_regioes:
                df_tabela = df_tabela[df_tabela["Regiao Vendedor"].isin(filtro_regioes)]
            if filtro_op != "Todas":
                df_tabela = df_tabela[df_tabela["Descrição (Tipo de Operação)"] == filtro_op]

            df_exibir = df_tabela[["Nro. Único", "Previsão de entrega", "Nome Parceiro (Parceiro)", "Vlr. Nota", "Descrição (Tipo de Negociação)", "Descrição (Tipo de Operação)", "Apelido (Vendedor)", "Regiao Vendedor"]].copy()
            df_exibir["Previsão de entrega"] = pd.to_datetime(df_exibir["Previsão de entrega"], errors="coerce").dt.strftime("%d/%m/%Y")
            df_exibir["Vlr. Nota"] = df_exibir["Vlr. Nota"].map(format_brl)
            st.caption(f"Exibindo **{len(df_exibir)}** pedido(s)")
            st.dataframe(df_exibir.rename(columns={"Nro. Único": "Nº Único", "Previsão de entrega": "Prev. Entrega", "Nome Parceiro (Parceiro)": "Parceiro", "Vlr. Nota": "Valor", "Descrição (Tipo de Negociação)": "Negociação", "Descrição (Tipo de Operação)": "Operação", "Apelido (Vendedor)": "Vendedor", "Regiao Vendedor": "Região"}), use_container_width=True, hide_index=True, height=420)

            # Exportar Resumo do Dia
            st.markdown('<div class="sec-title">&#11015;&#65039; Exportar Resumo do Dia</div>', unsafe_allow_html=True)
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
            st.download_button(label="⬇️ Baixar Resumo em Excel", data=buffer.getvalue(), file_name=f"resumo_financeiro_{data_ref.strftime('%d-%m-%Y')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="btn_export_dia")

        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")
    else:
        st.markdown("""
        <div class="info-box"><strong>Como usar:</strong> faça o upload do arquivo <code>.xlsx</code> exportado do Sankhya e clique em <strong>Salvar no histórico</strong>.<br><br>
        💾 <strong>Os dados são salvos no Supabase</strong> e permanecem disponíveis permanentemente!</div>
        """, unsafe_allow_html=True)
    
    # ──────────────────────────────────────────────────────────────────────
    # NOVA SEÇÃO: CONSULTAR PEDIDOS DO HISTÓRICO (na tela inicial)
    # ──────────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="sec-title">📅 Consultar Pedidos do Histórico</div>', unsafe_allow_html=True)
    
    # Seleção de Datas com Range
    hoje_date = datetime.today().date()
    datas_selecionadas = st.date_input(
        "Selecione o período (Início e Fim)", 
        value=(hoje_date, hoje_date),
        key="datas_range_home"
    )

    # Extrair datas corretamente
    if isinstance(datas_selecionadas, (tuple, list)) and len(datas_selecionadas) == 2:
        data_inicio, data_fim = datas_selecionadas
    else:
        data_inicio = data_fim = datas_selecionadas if isinstance(datas_selecionadas, (date, datetime)) else hoje_date

    col_btn, col_spacer = st.columns([1, 4])
    with col_btn:
        if st.button("🔎 Carregar Pedidos", key="btn_carregar_home", type="primary"):
            if data_inicio > data_fim:
                st.error("❌ A data de início não pode ser maior que a data de fim.")
            else:
                with st.spinner("⏳ Buscando pedidos..."):
                    try:
                        data_inicio_str = data_inicio.strftime("%Y-%m-%d")
                        data_fim_str = data_fim.strftime("%Y-%m-%d")
                        
                        response = supabase.table("historico_pedidos")\
                            .select("data_referencia, pedido_json")\
                            .gte("data_referencia", data_inicio_str)\
                            .lte("data_referencia", data_fim_str)\
                            .execute()
                        
                        if response.data:
                            df_geral = pd.DataFrame()
                            total_pedidos = 0
                            
                            for registro in response.data:
                                try:
                                    lista_pedidos = json.loads(registro["pedido_json"])
                                    df_dia = pd.DataFrame(lista_pedidos)
                                    df_geral = pd.concat([df_geral, df_dia], ignore_index=True)
                                    total_pedidos += len(df_dia)
                                except:
                                    pass 
                            
                            if not df_geral.empty:
                                if data_inicio == data_fim:
                                    msg_sucesso = f"✅ {total_pedidos} pedidos encontrados para {data_inicio.strftime('%d/%m/%Y')}!"
                                else:
                                    msg_sucesso = f"✅ {total_pedidos} pedidos encontrados entre {data_inicio.strftime('%d/%m')} e {data_fim.strftime('%d/%m')}!"
                                
                                st.success(msg_sucesso)
                                
                                st.session_state["df_pedidos_home"] = df_geral
                                st.session_state["range_label_home"] = f"{data_inicio.strftime('%d-%m')}_{data_fim.strftime('%d-%m')}"
                                st.session_state["data_ref_pdf_home"] = data_fim
                                
                            else:
                                st.warning("⚠️ Nenhum pedido detalhado encontrado.")
                                st.session_state["df_pedidos_home"] = None
                                
                        else:
                            st.warning("⚠️ Nenhum registro encontrado no banco de dados para este período.")
                            st.session_state["df_pedidos_home"] = None
                            
                    except Exception as e:
                        st.error(f"❌ Erro ao conectar com banco: {e}")

    # Exibição e Exportação dos pedidos consultados
    if st.session_state.get("df_pedidos_home") is not None:
        df_range = st.session_state["df_pedidos_home"]
        
        # Filtros rápidos
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            busca_range = st.text_input("🔍 Buscar parceiro ou nº único", key="busca_home")
        with col_f2:
            if "Regiao Vendedor" in df_range.columns:
                regioes_range = sorted(df_range["Regiao Vendedor"].dropna().unique().tolist())
                filtro_reg_range = st.multiselect("Região", options=regioes_range, default=regioes_range, key="filtro_reg_home")
        
        df_filtrado_range = df_range.copy()
        if busca_range:
            mask = df_filtrado_range["Nome Parceiro (Parceiro)"].str.contains(busca_range, case=False, na=False) | \
                   df_filtrado_range["Nro. Único"].astype(str).str.contains(busca_range, case=False, na=False)
            df_filtrado_range = df_filtrado_range[mask]
        if filtro_reg_range and "Regiao Vendedor" in df_filtrado_range.columns:
            df_filtrado_range = df_filtrado_range[df_filtrado_range["Regiao Vendedor"].isin(filtro_reg_range)]
        
        # Exibir tabela
        cols_exibir = ["Nro. Único", "Previsão de entrega", "Nome Parceiro (Parceiro)", "Vlr. Nota", "Apelido (Vendedor)", "Regiao Vendedor"]
        cols_disponiveis = [c for c in cols_exibir if c in df_filtrado_range.columns]
        df_exibir_range = df_filtrado_range[cols_disponiveis].copy()
        
        if "Previsão de entrega" in df_exibir_range.columns:
            df_exibir_range["Previsão de entrega"] = pd.to_datetime(df_exibir_range["Previsão de entrega"], errors="coerce").dt.strftime("%d/%m/%Y")
        if "Vlr. Nota" in df_exibir_range.columns:
            df_exibir_range["Vlr. Nota"] = df_exibir_range["Vlr. Nota"].map(format_brl)
        
        rename = {"Nro. Único": "Nº Único", "Previsão de entrega": "Prev. Entrega", "Nome Parceiro (Parceiro)": "Parceiro", 
                  "Vlr. Nota": "Valor", "Apelido (Vendedor)": "Vendedor", "Regiao Vendedor": "Região"}
        df_exibir_range = df_exibir_range.rename(columns={k: v for k, v in rename.items() if k in df_exibir_range.columns})
        
        st.dataframe(df_exibir_range, use_container_width=True, hide_index=True, height=400)
        
        # Exportação
        st.markdown('<div class="sec-title">📥 Exportar Pedidos Consultados</div>', unsafe_allow_html=True)
        col_pdf, col_excel = st.columns(2)
        
        with col_pdf:
            try:
                pdf_bytes = gerar_pdf_pedidos(df_filtrado_range, st.session_state.get("data_ref_pdf_home", hoje_date))
                st.download_button(
                    label="📄 Exportar Pedidos (PDF)", 
                    data=pdf_bytes, 
                    file_name=f"pedidos_{st.session_state['range_label_home']}.pdf",
                    mime="application/pdf",
                    key="btn_pdf_home"
                )
            except Exception as e:
                st.error(f"Erro ao gerar PDF: {e}")
                
        with col_excel:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df_filtrado_range.to_excel(writer, sheet_name="Pedidos", index=False)
            st.download_button(
                label="⬇️ Exportar Pedidos (Excel)", 
                data=buffer.getvalue(), 
                file_name=f"pedidos_{st.session_state['range_label_home']}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="btn_excel_home"
            )

# ═════════════════════════════════════════════════════════════════════════════
# ABA 2 — HISTÓRICO
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
            categorias_hist = {"Total Geral": ("total_geral", "#0f2942"), "Comercial": ("total_comercial", "#d4a017"), "Lojas": ("total_lojas", "#2ecc71"), "Boleto": ("total_boleto", "#2980b9"), "À Vista": ("total_a_vista", "#8e44ad"), "Assistência": ("total_assistencia", "#e07b3a"), "Cheque": ("total_cheque", "#e74c3c")}
            opcoes = st.multiselect("Selecionar categorias:", options=list(categorias_hist.keys()), default=["Total Geral", "Comercial", "Lojas", "Boleto", "Cheque"])
            if opcoes:
                fig = go.Figure()
                for nome in opcoes:
                    col_key, cor = categorias_hist[nome]
                    if col_key in h.columns:
                        fig.add_trace(go.Bar(name=nome, x=h["data_fmt"], y=h[col_key], marker_color=cor, hovertemplate=f"<b>{nome}</b><br>%{{x}}<br>R$ %{{y:,.2f}}<extra></extra>"))
                fig.update_layout(barmode="group", xaxis_title="Data", yaxis_title="Valor (R$)", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter, sans-serif", size=12), legend=dict(orientation="h", y=-0.2), margin=dict(t=20, b=60, l=20, r=20), height=420)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('<div class="sec-title">&#128203; Tabela de Registros</div>', unsafe_allow_html=True)
            
            cols_base = ["data_fmt", "total_geral", "total_assistencia", "total_lojas", "total_a_vista", "total_boleto", "total_comercial", "total_cheque"]
            cols_extras = [c for c in h.columns if c.startswith("extra_")]
            cols_tabela = [c for c in cols_base if c in h.columns] + cols_extras
            
            tbl = h[cols_tabela].copy()
            
            for c in ["total_geral", "total_assistencia", "total_lojas", "total_a_vista", "total_boleto", "total_comercial", "total_cheque"] + cols_extras:
                if c in tbl.columns:
                    tbl[c] = pd.to_numeric(tbl[c], errors="coerce").map(format_brl)
            
            rename_map = {
                "data_fmt": "Data", 
                "total_geral": "Total Geral", 
                "total_assistencia": "Assistência", 
                "total_lojas": "Lojas", 
                "total_a_vista": "À Vista", 
                "total_boleto": "Boleto", 
                "total_comercial": "Comercial",
                "total_cheque": "Cheque"
            }
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
            
            # ── CONSULTAR PEDIDOS POR PERÍODO (OU DIA ÚNICO) ──
            st.markdown('<div class="sec-title">📅 Consultar Pedidos</div>', unsafe_allow_html=True)

            # Seleção de Datas com Range
            hoje_date = datetime.today().date()
            datas_selecionadas = st.date_input(
                "Selecione o período (Início e Fim)", 
                value=(hoje_date, hoje_date),
                key="datas_range_picker"
            )

            # Extrair datas corretamente
            if isinstance(datas_selecionadas, (tuple, list)) and len(datas_selecionadas) == 2:
                data_inicio, data_fim = datas_selecionadas
            else:
                data_inicio = data_fim = datas_selecionadas if isinstance(datas_selecionadas, (date, datetime)) else hoje_date

            col_btn, col_spacer = st.columns([1, 4])
            with col_btn:
                if st.button("🔎 Carregar Pedidos", key="btn_carregar_periodo", type="primary"):
                    if data_inicio > data_fim:
                        st.error("❌ A data de início não pode ser maior que a data de fim.")
                    else:
                        with st.spinner("⏳ Buscando pedidos..."):
                            try:
                                data_inicio_str = data_inicio.strftime("%Y-%m-%d")
                                data_fim_str = data_fim.strftime("%Y-%m-%d")
                                
                                response = supabase.table("historico_pedidos")\
                                    .select("data_referencia, pedido_json")\
                                    .gte("data_referencia", data_inicio_str)\
                                    .lte("data_referencia", data_fim_str)\
                                    .execute()
                                
                                if response.data:
                                    df_geral = pd.DataFrame()
                                    total_pedidos = 0
                                    
                                    for registro in response.data:
                                        try:
                                            lista_pedidos = json.loads(registro["pedido_json"])
                                            df_dia = pd.DataFrame(lista_pedidos)
                                            df_geral = pd.concat([df_geral, df_dia], ignore_index=True)
                                            total_pedidos += len(df_dia)
                                        except:
                                            pass 
                                    
                                    if not df_geral.empty:
                                        if data_inicio == data_fim:
                                            msg_sucesso = f"✅ {total_pedidos} pedidos encontrados para {data_inicio.strftime('%d/%m/%Y')}!"
                                        else:
                                            msg_sucesso = f"✅ {total_pedidos} pedidos encontrados entre {data_inicio.strftime('%d/%m')} e {data_fim.strftime('%d/%m')}!"
                                        
                                        st.success(msg_sucesso)
                                        
                                        st.session_state["df_pedidos_range"] = df_geral
                                        st.session_state["range_label"] = f"{data_inicio.strftime('%d-%m')}_{data_fim.strftime('%d-%m')}"
                                        st.session_state["data_ref_pdf"] = data_fim
                                        
                                    else:
                                        st.warning("⚠️ Nenhum pedido detalhado encontrado.")
                                        st.session_state["df_pedidos_range"] = None
                                        
                                else:
                                    st.warning("⚠️ Nenhum registro encontrado no banco de dados para este período.")
                                    st.session_state["df_pedidos_range"] = None
                                    
                            except Exception as e:
                                st.error(f"❌ Erro ao conectar com banco: {e}")

            # Exibição e Exportação
            if st.session_state.get("df_pedidos_range") is not None:
                df_range = st.session_state["df_pedidos_range"]
                
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    busca_range = st.text_input("🔍 Buscar parceiro ou nº único", key="busca_range")
                with col_f2:
                    if "Regiao Vendedor" in df_range.columns:
                        regioes_range = sorted(df_range["Regiao Vendedor"].dropna().unique().tolist())
                        filtro_reg_range = st.multiselect("Região", options=regioes_range, default=regioes_range, key="filtro_reg_range")
                
                df_filtrado_range = df_range.copy()
                if busca_range:
                    mask = df_filtrado_range["Nome Parceiro (Parceiro)"].str.contains(busca_range, case=False, na=False) | \
                           df_filtrado_range["Nro. Único"].astype(str).str.contains(busca_range, case=False, na=False)
                    df_filtrado_range = df_filtrado_range[mask]
                if filtro_reg_range and "Regiao Vendedor" in df_filtrado_range.columns:
                    df_filtrado_range = df_filtrado_range[df_filtrado_range["Regiao Vendedor"].isin(filtro_reg_range)]
                
                cols_exibir = ["Nro. Único", "Previsão de entrega", "Nome Parceiro (Parceiro)", "Vlr. Nota", "Apelido (Vendedor)", "Regiao Vendedor"]
                cols_disponiveis = [c for c in cols_exibir if c in df_filtrado_range.columns]
                df_exibir_range = df_filtrado_range[cols_disponiveis].copy()
                
                if "Previsão de entrega" in df_exibir_range.columns:
                    df_exibir_range["Previsão de entrega"] = pd.to_datetime(df_exibir_range["Previsão de entrega"], errors="coerce").dt.strftime("%d/%m/%Y")
                if "Vlr. Nota" in df_exibir_range.columns:
                    df_exibir_range["Vlr. Nota"] = df_exibir_range["Vlr. Nota"].map(format_brl)
                
                rename = {"Nro. Único": "Nº Único", "Previsão de entrega": "Prev. Entrega", "Nome Parceiro (Parceiro)": "Parceiro", 
                          "Vlr. Nota": "Valor", "Apelido (Vendedor)": "Vendedor", "Regiao Vendedor": "Região"}
                df_exibir_range = df_exibir_range.rename(columns={k: v for k, v in rename.items() if k in df_exibir_range.columns})
                
                st.dataframe(df_exibir_range, use_container_width=True, hide_index=True, height=400)
                
                st.markdown('<div class="sec-title">📥 Exportar</div>', unsafe_allow_html=True)
                col_pdf, col_excel = st.columns(2)
                
                with col_pdf:
                    try:
                        pdf_bytes = gerar_pdf_pedidos(df_filtrado_range, st.session_state.get("data_ref_pdf", hoje_date))
                        st.download_button(
                            label="📄 Exportar Pedidos (PDF)", 
                            data=pdf_bytes, 
                            file_name=f"pedidos_{st.session_state['range_label']}.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"Erro ao gerar PDF: {e}")
                        
                with col_excel:
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                        df_filtrado_range.to_excel(writer, sheet_name="Pedidos", index=False)
                    st.download_button(
                        label="⬇️ Exportar Pedidos (Excel)", 
                        data=buffer.getvalue(), 
                        file_name=f"pedidos_{st.session_state['range_label']}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

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