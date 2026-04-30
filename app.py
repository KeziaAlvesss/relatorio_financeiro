import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
import os
from datetime import datetime
import base64

def get_image_base64(path):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, path)
    with open(full_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

st.set_page_config(
    page_title="Financeiro PCP | Bonsono",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="collapsed"
)

HISTORICO_PATH = "historico_financeiro.csv"

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
.kpi-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 16px; margin: 24px 0; }
.kpi-card { background: #fff; border-radius: 14px; padding: 22px 20px 18px 20px; box-shadow: 0 2px 12px rgba(15,41,66,0.07); position: relative; overflow: hidden; }
.kpi-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; }
.kpi-card.total::before     { background: #0f2942; }
.kpi-card.assist::before    { background: #e07b3a; }
.kpi-card.lojas::before     { background: #2ecc71; }
.kpi-card.avista::before    { background: #8e44ad; }
.kpi-card.boleto::before    { background: #2980b9; }
.kpi-card.comercial::before { background: #d4a017; }
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
</style>
""", unsafe_allow_html=True)

logo_b64 = get_image_base64("logo-bonsono.png")

st.markdown(f"""
<div class="page-header">
    <img class="header-logo" src="data:image/png;base64,{logo_b64}" />
    <div>
        <h1>Relatório Financeiro da Produção</h1>
        <p class="subtitle">📡 Análise automática gerada a partir do Portal de Vendas — Sankhya</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def format_brl(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

import re

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

def carregar_historico():
    if os.path.exists(HISTORICO_PATH):
        df = pd.read_csv(HISTORICO_PATH, dtype={"data": str})
        df["data"] = pd.to_datetime(df["data"]).dt.strftime("%Y-%m-%d")
        return df
    return pd.DataFrame(columns=["data", "total_geral", "total_assistencia",
                                  "total_lojas", "total_a_vista", "total_boleto",
                                  "total_comercial", "qtd_notas"])

def salvar_historico(data_ref, totais):
    hist = carregar_historico()
    data_str = data_ref.strftime("%Y-%m-%d")
    if data_str in hist["data"].values:
        return False
    nova = pd.DataFrame([{"data": data_str, **totais}])
    hist = pd.concat([hist, nova], ignore_index=True).sort_values("data")
    hist.to_csv(HISTORICO_PATH, index=False)
    return True


# ── Abas ──────────────────────────────────────────────────────────────────────
aba_hoje, aba_historico = st.tabs(["📋 Relatório do Dia", "📅 Histórico"])

# ═════════════════════════════════════════════════════════════════════════════
# ABA 1 — RELATÓRIO DO DIA
# ═════════════════════════════════════════════════════════════════════════════
with aba_hoje:
    st.markdown('<span class="upload-label">&#128194; Selecionar arquivo</span>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["xlsx", "xls"], label_visibility="collapsed")

    if uploaded_file:
        try:
            df_raw = load_data(uploaded_file)
            totais, df = calcular_totais(df_raw)
            t = totais

            CATEGORIAS_EXTRA = ["Atacado", "Credimoveis", "Carajás", "Outro"]
            CORES_EXTRA = {"Atacado": "#1abc9c", "Credimoveis": "#e74c3c",
                           "Carajás": "#f39c12", "Outro": "#7f8c8d"}

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
                    salvo = salvar_historico(data_ref, t_salvar)
                    if salvo:
                        st.markdown('<span class="saved-badge">&#9989; Salvo com sucesso!</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="already-badge">&#9888; Já existe um registro para essa data.</span>', unsafe_allow_html=True)

            # ── KPI Cards ──
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
                '<div class="kpi-grid">'
                '<div class="kpi-card total">'
                '<div class="kpi-label">&#128176; Total Geral</div>'
                f'<div class="kpi-value">{format_brl(total_geral_ajustado)}</div>'
                f'<span class="kpi-badge">{t["qtd_notas"]} notas</span>'
                '</div>'
                '<div class="kpi-card assist">'
                '<div class="kpi-label">&#128296; Assist\u00eancia</div>'
                f'<div class="kpi-value">{format_brl(t["total_assistencia"])}</div>'
                f'<span class="kpi-badge">{pct(t["total_assistencia"])}</span>'
                '</div>'
                '<div class="kpi-card lojas">'
                '<div class="kpi-label">&#127978; Lojas</div>'
                f'<div class="kpi-value">{format_brl(t["total_lojas"])}</div>'
                f'<span class="kpi-badge">{pct(t["total_lojas"])}</span>'
                '</div>'
                '<div class="kpi-card avista">'
                '<div class="kpi-label">&#128181; \u00c0 Vista</div>'
                f'<div class="kpi-value">{format_brl(t["total_a_vista"])}</div>'
                f'<span class="kpi-badge">{pct(t["total_a_vista"])}</span>'
                '</div>'
                '<div class="kpi-card boleto">'
                '<div class="kpi-label">&#128196; Boleto (dias)</div>'
                f'<div class="kpi-value">{format_brl(t["total_boleto"])}</div>'
                f'<span class="kpi-badge">{pct(t["total_boleto"])}</span>'
                '</div>'
                '<div class="kpi-card comercial">'
                '<div class="kpi-label">&#129309; Comercial</div>'
                f'<div class="kpi-value">{format_brl(t["total_comercial"])}</div>'
                f'<span class="kpi-badge">{pct(t["total_comercial"])}</span>'
                '</div>'
                + cards_extras_html +
                '</div>',
                unsafe_allow_html=True
            )

            # ── Mix de Faturamento ──
            st.markdown('<div class="sec-title">&#129383; Mix de Faturamento</div>', unsafe_allow_html=True)

            df["_is_cheque"] = df["Descrição (Tipo de Negociação)"].str.upper().str.contains("CHEQUE", na=False)
            total_cheque = df[df["_is_cheque"]]["Vlr. Nota"].sum()
            total_outros = max(t["total_geral"] - (
                t["total_assistencia"] + t["total_lojas"] +
                t["total_a_vista"] + t["total_boleto"] + total_cheque
            ), 0)

            mix_labels = ["Boleto (dias)", "Lojas", "\u00c0 Vista", "Assist\u00eancia", "Cheque", "Outros"]
            mix_values = [t["total_boleto"], t["total_lojas"], t["total_a_vista"],
                          t["total_assistencia"], total_cheque, total_outros]
            mix_cores  = ["#2980b9", "#2ecc71", "#8e44ad", "#e07b3a", "#16a085", "#95a5a6"]

            for cat, val in extras_por_cat.items():
                mix_labels.append(cat)
                mix_values.append(val)
                mix_cores.append(CORES_EXTRA.get(cat, "#7f8c8d"))

            mix_df = pd.DataFrame({"Categoria": mix_labels, "Valor": mix_values, "Cor": mix_cores})
            mix_df = mix_df[mix_df["Valor"] > 0].reset_index(drop=True)

            col_chart, col_table = st.columns([1.4, 1])
            with col_chart:
                fig_mix = go.Figure(go.Pie(
                    labels=mix_df["Categoria"], values=mix_df["Valor"], hole=0.52,
                    marker=dict(colors=mix_df["Cor"].tolist()),
                    textposition="outside", textinfo="label+percent",
                    hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>",
                ))
                fig_mix.update_layout(
                    margin=dict(t=30, b=30, l=20, r=20), showlegend=False,
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter, sans-serif", size=12), height=400,
                )
                st.plotly_chart(fig_mix, use_container_width=True)
            with col_table:
                mix_tbl = mix_df[["Categoria", "Valor"]].copy()
                mix_tbl["% do Total"] = (mix_tbl["Valor"] / total_geral_ajustado * 100).map("{:.1f}%".format)
                mix_tbl["Valor"] = mix_tbl["Valor"].map(format_brl)
                st.dataframe(mix_tbl, use_container_width=True, hide_index=True, height=400)

            resumo_neg = (
                df.groupby("Descrição (Tipo de Negociação)")["Vlr. Nota"]
                .agg(Qtd="count", Total="sum")
                .sort_values("Total", ascending=False)
                .reset_index()
            )
            resumo_neg_tbl = resumo_neg.copy()
            resumo_neg_tbl["% do Total"] = (resumo_neg_tbl["Total"] / t["total_geral"] * 100).map("{:.1f}%".format)
            resumo_neg_tbl["Total"] = resumo_neg_tbl["Total"].map(format_brl)

            # ── Notas Assistência ──
            st.markdown('<div class="sec-title">&#128296; Notas de Assist\u00eancia</div>', unsafe_allow_html=True)
            df_assist = df[df["_is_assistencia"]][
                ["Nro. Nota", "Dt. Neg.", "Nome Parceiro (Parceiro)", "Vlr. Nota",
                 "Descrição (Tipo de Negociação)", "Apelido (Vendedor)"]
            ].copy()
            df_assist["Vlr. Nota"] = df_assist["Vlr. Nota"].map(format_brl)
            df_assist["Dt. Neg."] = pd.to_datetime(df_assist["Dt. Neg."], errors="coerce").dt.strftime("%d/%m/%Y")
            st.dataframe(df_assist.rename(columns={
                "Nro. Nota": "Nota", "Dt. Neg.": "Data", "Nome Parceiro (Parceiro)": "Parceiro",
                "Descrição (Tipo de Negociação)": "Tipo Neg.", "Apelido (Vendedor)": "Vendedor"
            }), use_container_width=True, hide_index=True)

            # ── Tabela Completa de Pedidos ──
            st.markdown('<div class="sec-title">&#128203; Todos os Pedidos da Produção</div>', unsafe_allow_html=True)

            col_f1, col_f2, col_f3, col_f4 = st.columns([2, 2, 2, 2])
            with col_f1:
                busca = st.text_input("🔍 Buscar parceiro / nota", placeholder="Ex: Magazine, 64761...")
            with col_f2:
                regioes = ["Todas"] + sorted(df["Regiao Vendedor"].dropna().unique().tolist())
                filtro_regiao = st.selectbox("Região", regioes)
            with col_f3:
                operacoes = ["Todas"] + sorted(df["Descrição (Tipo de Operação)"].dropna().unique().tolist())
                filtro_op = st.selectbox("Tipo de Operação", operacoes)
            with col_f4:
                negociacoes = ["Todas"] + sorted(df["Descrição (Tipo de Negociação)"].dropna().unique().tolist())
                filtro_neg = st.selectbox("Tipo de Negociação", negociacoes)

            # Aplicar filtros
            df_tabela = df.copy()

            if busca:                                                          # ← CORREÇÃO: df_tabela filtrado DENTRO do if
                mask_busca = (
                    df_tabela["Nome Parceiro (Parceiro)"].str.contains(busca, case=False, na=False) |
                    df_tabela["Nro. Nota"].astype(str).str.contains(busca, case=False, na=False) |
                    df_tabela["Ordem de Compra"].astype(str).str.contains(busca, case=False, na=False)
                )
                df_tabela = df_tabela[mask_busca]                              # ← estava fora do if, causando o erro

            if filtro_regiao != "Todas":
                df_tabela = df_tabela[df_tabela["Regiao Vendedor"] == filtro_regiao]

            if filtro_op != "Todas":
                df_tabela = df_tabela[df_tabela["Descrição (Tipo de Operação)"] == filtro_op]

            if filtro_neg != "Todas":
                df_tabela = df_tabela[df_tabela["Descrição (Tipo de Negociação)"] == filtro_neg]

            # Montar tabela final
            df_exibir = df_tabela[[
                "Nro. Nota",
                "Dt. Neg.",
                "Nome Parceiro (Parceiro)",
                "Vlr. Nota",
                "Descrição (Tipo de Negociação)",
                "Descrição (Tipo de Operação)",
                "Apelido (Vendedor)",
                "Regiao Vendedor",
                "Ordem de Compra",
                "Previsão de entrega",
                "Análise Financeira",
                "Status NF-e",
            ]].copy()

            df_exibir["Dt. Neg."] = pd.to_datetime(df_exibir["Dt. Neg."], errors="coerce").dt.strftime("%d/%m/%Y")
            df_exibir["Previsão de entrega"] = pd.to_datetime(df_exibir["Previsão de entrega"], errors="coerce").dt.strftime("%d/%m/%Y")
            df_exibir["Vlr. Nota"] = df_exibir["Vlr. Nota"].map(format_brl)

            st.caption(f"Exibindo **{len(df_exibir)}** pedido(s) de **{len(df)}** no total")

            st.dataframe(
                df_exibir.rename(columns={
                    "Nro. Nota": "Nota",
                    "Dt. Neg.": "Data",
                    "Nome Parceiro (Parceiro)": "Parceiro",
                    "Vlr. Nota": "Valor",
                    "Descrição (Tipo de Negociação)": "Negociação",
                    "Descrição (Tipo de Operação)": "Operação",
                    "Apelido (Vendedor)": "Vendedor",
                    "Regiao Vendedor": "Região",
                    "Ordem de Compra": "OC",
                    "Previsão de entrega": "Prev. Entrega",
                    "Análise Financeira": "Fin.",
                    "Status NF-e": "NF-e",
                }),
                use_container_width=True,
                hide_index=True,
                height=420,
            )

            # ── Export ──
            st.markdown('<div class="sec-title">&#11015;&#65039; Exportar</div>', unsafe_allow_html=True)
            categorias_export = ["Total Geral", "Assist\u00eancia", "Lojas", "\u00c0 Vista", "Boleto (com dias)", "Comercial"]
            valores_export    = [total_geral_ajustado, t["total_assistencia"], t["total_lojas"],
                                 t["total_a_vista"], t["total_boleto"], t["total_comercial"]]
            for cat, val in extras_por_cat.items():
                categorias_export.append(cat)
                valores_export.append(val)
            resumo_export = pd.DataFrame({"Categoria": categorias_export, "Valor": valores_export})
            resumo_export["% do Total"] = (resumo_export["Valor"] / total_geral_ajustado * 100).round(2)
            resumo_export["Valor"] = resumo_export["Valor"].map(format_brl)
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                resumo_export.to_excel(writer, sheet_name="Resumo", index=False)
                resumo_neg_tbl.to_excel(writer, sheet_name="Por Negociação", index=False)
            st.download_button(
                label="⬇️  Baixar Resumo em Excel",
                data=buffer.getvalue(),
                file_name=f"resumo_financeiro_{data_ref.strftime('%d-%m-%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")
    else:
        st.markdown("""
        <div class="info-box">
            <strong>Como usar:</strong> faça o upload do arquivo <code>.xlsx</code> exportado do Sankhya (Cabeçalho da Nota) e clique em <strong>Salvar no histórico</strong> para acumular os dados diários.<br><br>
            O app calcula automaticamente:<br>
            &nbsp;&nbsp;&#128176; <strong>Total Geral</strong> — soma de todas as notas<br>
            &nbsp;&nbsp;&#128296; <strong>Assistência</strong> — notas do tipo "Pedido de Assistência"<br>
            &nbsp;&nbsp;&#127978; <strong>Lojas</strong> — região de vendedor = LOJAS<br>
            &nbsp;&nbsp;&#128181; <strong>À Vista</strong> — tipo de negociação "À Vista"<br>
            &nbsp;&nbsp;&#128196; <strong>Boleto</strong> — tipos com prazo em dias (30/60/90…)<br>
            &nbsp;&nbsp;&#129309; <strong>Comercial</strong> — regiões de vendedor (Região 1, 2, 3…)
        </div>
        """, unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# ABA 2 — HISTÓRICO
# ═════════════════════════════════════════════════════════════════════════════
with aba_historico:
    hist = carregar_historico()

    if hist.empty:
        st.info("Nenhum histórico ainda. Faça upload de relatórios e clique em **Salvar no histórico** na aba anterior.")
    else:
        hist["data_dt"] = pd.to_datetime(hist["data"], format="%Y-%m-%d")
        hist_sorted = hist.sort_values("data_dt")

        st.markdown('<div class="sec-title">&#128197; Filtrar período</div>', unsafe_allow_html=True)
        col_de, col_ate = st.columns(2)
        with col_de:
            data_de = st.date_input("De", value=hist_sorted["data_dt"].min().date())
        with col_ate:
            data_ate = st.date_input("Até", value=hist_sorted["data_dt"].max().date())

        mask = (hist_sorted["data_dt"].dt.date >= data_de) & (hist_sorted["data_dt"].dt.date <= data_ate)
        h = hist_sorted[mask].copy()

        if h.empty:
            st.warning("Nenhum registro no período selecionado.")
        else:
            h["data_fmt"] = h["data_dt"].dt.strftime("%d/%m/%Y")

            st.markdown('<div class="sec-title">&#128202; Comparativo por Período</div>', unsafe_allow_html=True)
            categorias_hist = {
                "Total Geral":  ("total_geral",       "#0f2942"),
                "Comercial":    ("total_comercial",   "#d4a017"),
                "Lojas":        ("total_lojas",        "#2ecc71"),
                "Boleto":       ("total_boleto",       "#2980b9"),
                "À Vista":      ("total_a_vista",      "#8e44ad"),
                "Assistência":  ("total_assistencia",  "#e07b3a"),
            }
            opcoes = st.multiselect(
                "Selecionar categorias para exibir:",
                options=list(categorias_hist.keys()),
                default=["Total Geral", "Comercial", "Lojas", "Boleto"]
            )
            if opcoes:
                fig = go.Figure()
                for nome in opcoes:
                    col_key, cor = categorias_hist[nome]
                    fig.add_trace(go.Bar(
                        name=nome, x=h["data_fmt"], y=h[col_key], marker_color=cor,
                        hovertemplate=f"<b>{nome}</b><br>%{{x}}<br>R$ %{{y:,.2f}}<extra></extra>",
                    ))
                fig.update_layout(
                    barmode="group", xaxis_title="Data", yaxis_title="Valor (R$)",
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter, sans-serif", size=12),
                    legend=dict(orientation="h", y=-0.2),
                    margin=dict(t=20, b=60, l=20, r=20), height=420,
                    xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#e8edf5"),
                )
                st.plotly_chart(fig, use_container_width=True)

            st.markdown('<div class="sec-title">&#128203; Tabela de Registros</div>', unsafe_allow_html=True)
            tbl = h[["data_fmt", "total_geral", "total_assistencia", "total_lojas",
                      "total_a_vista", "total_boleto", "total_comercial", "qtd_notas"]].copy()
            for c in ["total_geral", "total_assistencia", "total_lojas",
                      "total_a_vista", "total_boleto", "total_comercial"]:
                tbl[c] = pd.to_numeric(tbl[c], errors="coerce").map(format_brl)
            tbl["qtd_notas"] = pd.to_numeric(tbl["qtd_notas"], errors="coerce").fillna(0).astype(int)
            st.dataframe(tbl.rename(columns={
                "data_fmt": "Data", "total_geral": "Total Geral",
                "total_assistencia": "Assistência", "total_lojas": "Lojas",
                "total_a_vista": "À Vista", "total_boleto": "Boleto",
                "total_comercial": "Comercial", "qtd_notas": "Qtd. Notas",
            }), use_container_width=True, hide_index=True)

            st.markdown('<div class="sec-title">&#11015;&#65039; Exportar Histórico</div>', unsafe_allow_html=True)
            buf_hist = io.BytesIO()
            tbl.to_excel(buf_hist, index=False, engine="openpyxl")
            st.download_button(
                label="⬇️  Baixar Histórico em Excel",
                data=buf_hist.getvalue(),
                file_name=f"historico_financeiro_{data_de}_{data_ate}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            with st.expander("🗑️ Remover um registro do histórico"):
                datas_disp = h["data_fmt"].tolist()
                data_del = st.selectbox("Selecione a data para remover:", datas_disp)
                if st.button("Remover"):
                    data_del_iso = pd.to_datetime(data_del, format="%d/%m/%Y").strftime("%Y-%m-%d")
                    hist_full = carregar_historico()
                    hist_full = hist_full[hist_full["data"] != data_del_iso]
                    hist_full.to_csv(HISTORICO_PATH, index=False)
                    st.success(f"Registro de {data_del} removido.")
                    st.rerun()