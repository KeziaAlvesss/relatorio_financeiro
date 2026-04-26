import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import os
from datetime import datetime

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

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #f7f8fc; }

.page-header {
    background: linear-gradient(135deg, #0f2942 0%, #1a4a7a 60%, #1e6fbf 100%);
    border-radius: 16px;
    padding: 36px 40px;
    margin-bottom: 32px;
    display: flex;
    align-items: center;
    gap: 20px;
    box-shadow: 0 8px 32px rgba(15,41,66,0.18);
}
.page-header h1 {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0;
    letter-spacing: -0.5px;
}
.page-header p { color: #a8c8f0; margin: 4px 0 0 0; font-size: 0.88rem; font-weight: 300; }
.header-icon { font-size: 2.6rem; }

.upload-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #6b7a99;
    margin-bottom: 8px;
    display: block;
}

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 16px;
    margin: 24px 0;
}
.kpi-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 22px 20px 18px 20px;
    box-shadow: 0 2px 12px rgba(15,41,66,0.07);
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
}
.kpi-card.total::before     { background: #0f2942; }
.kpi-card.assist::before    { background: #e07b3a; }
.kpi-card.lojas::before     { background: #2ecc71; }
.kpi-card.avista::before    { background: #8e44ad; }
.kpi-card.boleto::before    { background: #2980b9; }
.kpi-card.comercial::before { background: #d4a017; }

.kpi-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: #8a94a6;
    margin-bottom: 8px;
}
.kpi-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.45rem;
    font-weight: 800;
    color: #0f2942;
    line-height: 1.1;
}
.kpi-badge {
    display: inline-block;
    margin-top: 8px;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 20px;
    background: #f0f4ff;
    color: #3a5bab;
}

.sec-title {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #0f2942;
    margin: 32px 0 12px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.sec-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #e2e8f0;
    margin-left: 8px;
}

.stDownloadButton > button {
    background: #0f2942 !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 24px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.5px !important;
}
.stDownloadButton > button:hover { background: #1a4a7a !important; }

[data-testid="stFileUploader"] {
    background: #ffffff;
    border-radius: 14px;
    padding: 8px;
    box-shadow: 0 2px 10px rgba(15,41,66,0.06);
}

.info-box {
    background: #eef4ff;
    border-left: 4px solid #2980b9;
    border-radius: 10px;
    padding: 16px 20px;
    color: #1a3a5c;
    font-size: 0.88rem;
    line-height: 1.8;
}

.saved-badge {
    background: #d4edda;
    color: #155724;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-block;
    margin-top: 8px;
}
.already-badge {
    background: #fff3cd;
    color: #856404;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-block;
    margin-top: 8px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <span class="header-icon">📊</span>
    <div>
        <h1>Relatório Financeiro da Produção</h1>
        <p>Análise automática gerada a partir do Cabeçalho da Nota — Sankhya</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Helpers ──────────────────────────────────────────────────────────────────
def format_brl(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def is_boleto(tipo):
    return "DIAS" in str(tipo).upper() if pd.notna(tipo) else False

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
        return pd.read_csv(HISTORICO_PATH, parse_dates=["data"])
    return pd.DataFrame(columns=["data", "total_geral", "total_assistencia",
                                  "total_lojas", "total_a_vista", "total_boleto",
                                  "total_comercial", "qtd_notas"])

def salvar_historico(data_ref, totais):
    hist = carregar_historico()
    data_str = data_ref.strftime("%Y-%m-%d")
    # Evita duplicata para o mesmo dia
    if data_str in hist["data"].astype(str).values:
        return False
    nova = pd.DataFrame([{"data": data_str, **{k: v for k, v in totais.items()}}])
    hist = pd.concat([hist, nova], ignore_index=True).sort_values("data")
    hist.to_csv(HISTORICO_PATH, index=False)
    return True

# ── Abas ─────────────────────────────────────────────────────────────────────
aba_hoje, aba_historico = st.tabs(["📋 Relatório do Dia", "📅 Histórico"])

# ════════════════════════════════════════════════════════════════════════════
# ABA 1 — RELATÓRIO DO DIA
# ════════════════════════════════════════════════════════════════════════════
with aba_hoje:
    st.markdown('<span class="upload-label">📂 Selecionar arquivo</span>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["xlsx", "xls"], label_visibility="collapsed")

    if uploaded_file:
        try:
            df_raw = load_data(uploaded_file)
            totais, df = calcular_totais(df_raw)

            t = totais
            pct = lambda v: f"{v/t['total_geral']*100:.1f}% do total" if t["total_geral"] else "—"

            # ── Data de referência ──
            col_data, col_salvar = st.columns([1, 2])
            with col_data:
                data_ref = st.date_input("📅 Data de referência deste relatório", value=datetime.today())
            with col_salvar:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("💾  Salvar no histórico"):
                    salvo = salvar_historico(data_ref, t)
                    if salvo:
                        st.markdown('<span class="saved-badge">✅ Salvo com sucesso!</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="already-badge">⚠️ Já existe um registro para essa data.</span>', unsafe_allow_html=True)

            # ── KPI Cards ──
            st.markdown(f"""
            <div class="kpi-grid">
                <div class="kpi-card total">
                    <div class="kpi-label">💰 Total Geral</div>
                    <div class="kpi-value">{format_brl(t['total_geral'])}</div>
                    <span class="kpi-badge">{t['qtd_notas']} notas</span>
                </div>
                <div class="kpi-card assist">
                    <div class="kpi-label">🔧 Assistência</div>
                    <div class="kpi-value">{format_brl(t['total_assistencia'])}</div>
                    <span class="kpi-badge">{pct(t['total_assistencia'])}</span>
                </div>
                <div class="kpi-card lojas">
                    <div class="kpi-label">🏪 Lojas</div>
                    <div class="kpi-value">{format_brl(t['total_lojas'])}</div>
                    <span class="kpi-badge">{pct(t['total_lojas'])}</span>
                </div>
                <div class="kpi-card avista">
                    <div class="kpi-label">💵 À Vista</div>
                    <div class="kpi-value">{format_brl(t['total_a_vista'])}</div>
                    <span class="kpi-badge">{pct(t['total_a_vista'])}</span>
                </div>
                <div class="kpi-card boleto">
                    <div class="kpi-label">📄 Boleto (dias)</div>
                    <div class="kpi-value">{format_brl(t['total_boleto'])}</div>
                    <span class="kpi-badge">{pct(t['total_boleto'])}</span>
                </div>
                <div class="kpi-card comercial">
                    <div class="kpi-label">🤝 Comercial</div>
                    <div class="kpi-value">{format_brl(t['total_comercial'])}</div>
                    <span class="kpi-badge">{pct(t['total_comercial'])}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Gráfico rosca — Mix de Faturamento ──
            st.markdown('<div class="sec-title">🥧 Mix de Faturamento</div>', unsafe_allow_html=True)

            # Cheque: qualquer tipo de negociação que contenha "CHEQUE"
            df["_is_cheque"] = df["Descrição (Tipo de Negociação)"].str.upper().str.contains("CHEQUE", na=False)
            total_cheque = df[df["_is_cheque"]]["Vlr. Nota"].sum()

            # Outros: o que não se encaixa em nenhuma categoria
            total_outros = t["total_geral"] - (
                t["total_assistencia"] + t["total_lojas"] +
                t["total_a_vista"] + t["total_boleto"] + total_cheque
            )
            # Monta o mix só com categorias > 0
            mix_labels = ["Boleto (dias)", "Lojas", "À Vista", "Assistência", "Cheque", "Outros"]
            mix_values = [t["total_boleto"], t["total_lojas"], t["total_a_vista"],
                          t["total_assistencia"], total_cheque, max(total_outros, 0)]
            mix_cores  = ["#2980b9", "#2ecc71", "#8e44ad", "#e07b3a", "#16a085", "#95a5a6"]

            mix_df = pd.DataFrame({"Categoria": mix_labels, "Valor": mix_values, "Cor": mix_cores})
            mix_df = mix_df[mix_df["Valor"] > 0].reset_index(drop=True)

            col_chart, col_table = st.columns([1.4, 1])
            with col_chart:
                fig_mix = go.Figure(go.Pie(
                    labels=mix_df["Categoria"],
                    values=mix_df["Valor"],
                    hole=0.52,
                    marker=dict(colors=mix_df["Cor"].tolist()),
                    textposition="outside",
                    textinfo="label+percent",
                    hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>",
                ))
                fig_mix.update_layout(
                    margin=dict(t=30, b=30, l=20, r=20), showlegend=False,
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="DM Sans, sans-serif", size=12), height=400,
                )
                st.plotly_chart(fig_mix, use_container_width=True)

            with col_table:
                mix_tbl = mix_df[["Categoria", "Valor"]].copy()
                mix_tbl["% do Total"] = (mix_tbl["Valor"] / t["total_geral"] * 100).map("{:.1f}%".format)
                mix_tbl["Valor"] = mix_tbl["Valor"].map(format_brl)
                st.dataframe(mix_tbl, use_container_width=True, hide_index=True, height=400)

            # Mantém resumo_neg_tbl para o export
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
            st.markdown('<div class="sec-title">🔧 Notas de Assistência</div>', unsafe_allow_html=True)
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

            # ── Notas Lojas ──
            st.markdown('<div class="sec-title">🏪 Notas de Lojas</div>', unsafe_allow_html=True)
            df_lojas = df[df["_is_loja"]][
                ["Nro. Nota", "Dt. Neg.", "Nome Parceiro (Parceiro)", "Vlr. Nota",
                 "Descrição (Tipo de Negociação)", "Apelido (Vendedor)", "Descrição (Centro de Resultado)"]
            ].copy()
            df_lojas["Vlr. Nota"] = df_lojas["Vlr. Nota"].map(format_brl)
            df_lojas["Dt. Neg."] = pd.to_datetime(df_lojas["Dt. Neg."], errors="coerce").dt.strftime("%d/%m/%Y")
            st.dataframe(df_lojas.rename(columns={
                "Nro. Nota": "Nota", "Dt. Neg.": "Data", "Nome Parceiro (Parceiro)": "Parceiro",
                "Descrição (Tipo de Negociação)": "Tipo Neg.", "Apelido (Vendedor)": "Vendedor",
                "Descrição (Centro de Resultado)": "Loja"
            }), use_container_width=True, hide_index=True)

            # ── Export ──
            st.markdown('<div class="sec-title">⬇️ Exportar</div>', unsafe_allow_html=True)
            resumo_export = pd.DataFrame({
                "Categoria": ["Total Geral", "Assistência", "Lojas", "À Vista", "Boleto (com dias)", "Comercial"],
                "Valor": [t["total_geral"], t["total_assistencia"], t["total_lojas"],
                          t["total_a_vista"], t["total_boleto"], t["total_comercial"]]
            })
            resumo_export["% do Total"] = (resumo_export["Valor"] / t["total_geral"] * 100).round(2)
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
            &nbsp;&nbsp;💰 <strong>Total Geral</strong> — soma de todas as notas<br>
            &nbsp;&nbsp;🔧 <strong>Assistência</strong> — notas do tipo "Pedido de Assistência"<br>
            &nbsp;&nbsp;🏪 <strong>Lojas</strong> — região de vendedor = LOJAS<br>
            &nbsp;&nbsp;💵 <strong>À Vista</strong> — tipo de negociação "À Vista"<br>
            &nbsp;&nbsp;📄 <strong>Boleto</strong> — tipos com prazo em dias (30/60/90…)<br>
            &nbsp;&nbsp;🤝 <strong>Comercial</strong> — regiões de vendedor (Região 1, 2, 3…)
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# ABA 2 — HISTÓRICO
# ════════════════════════════════════════════════════════════════════════════
with aba_historico:
    hist = carregar_historico()

    if hist.empty:
        st.info("Nenhum histórico ainda. Faça upload de relatórios e clique em **Salvar no histórico** na aba anterior.")
    else:
        hist["data"] = pd.to_datetime(hist["data"])
        hist_sorted = hist.sort_values("data")

        # ── Filtro de período ──
        st.markdown('<div class="sec-title">🗓️ Filtrar período</div>', unsafe_allow_html=True)
        col_de, col_ate = st.columns(2)
        with col_de:
            data_de = st.date_input("De", value=hist_sorted["data"].min().date())
        with col_ate:
            data_ate = st.date_input("Até", value=hist_sorted["data"].max().date())

        mask = (hist_sorted["data"].dt.date >= data_de) & (hist_sorted["data"].dt.date <= data_ate)
        h = hist_sorted[mask].copy()

        if h.empty:
            st.warning("Nenhum registro no período selecionado.")
        else:
            h["data_fmt"] = h["data"].dt.strftime("%d/%m/%Y")

            # ── Gráfico de barras comparativo ──
            st.markdown('<div class="sec-title">📊 Comparativo por Período</div>', unsafe_allow_html=True)

            categorias = {
                "Total Geral":   ("total_geral",       "#0f2942"),
                "Comercial":     ("total_comercial",   "#d4a017"),
                "Lojas":         ("total_lojas",        "#2ecc71"),
                "Boleto":        ("total_boleto",       "#2980b9"),
                "À Vista":       ("total_a_vista",      "#8e44ad"),
                "Assistência":   ("total_assistencia",  "#e07b3a"),
            }

            opcoes = st.multiselect(
                "Selecionar categorias para exibir:",
                options=list(categorias.keys()),
                default=["Total Geral", "Comercial", "Lojas", "Boleto"]
            )

            if opcoes:
                fig = go.Figure()
                for nome in opcoes:
                    col, cor = categorias[nome]
                    fig.add_trace(go.Bar(
                        name=nome,
                        x=h["data_fmt"],
                        y=h[col],
                        marker_color=cor,
                        hovertemplate=f"<b>{nome}</b><br>%{{x}}<br>R$ %{{y:,.2f}}<extra></extra>",
                    ))
                fig.update_layout(
                    barmode="group",
                    xaxis_title="Data",
                    yaxis_title="Valor (R$)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="DM Sans, sans-serif", size=12),
                    legend=dict(orientation="h", y=-0.2),
                    margin=dict(t=20, b=60, l=20, r=20),
                    height=420,
                    xaxis=dict(showgrid=False),
                    yaxis=dict(gridcolor="#e8edf5"),
                )
                st.plotly_chart(fig, use_container_width=True)

            # ── Tabela histórico ──
            st.markdown('<div class="sec-title">📋 Tabela de Registros</div>', unsafe_allow_html=True)
            tbl = h[["data_fmt", "total_geral", "total_assistencia", "total_lojas",
                      "total_a_vista", "total_boleto", "total_comercial", "qtd_notas"]].copy()
            for col in ["total_geral", "total_assistencia", "total_lojas",
                        "total_a_vista", "total_boleto", "total_comercial"]:
                tbl[col] = tbl[col].map(format_brl)
            tbl["qtd_notas"] = tbl["qtd_notas"].astype(int)
            st.dataframe(tbl.rename(columns={
                "data_fmt":          "Data",
                "total_geral":       "Total Geral",
                "total_assistencia": "Assistência",
                "total_lojas":       "Lojas",
                "total_a_vista":     "À Vista",
                "total_boleto":      "Boleto",
                "total_comercial":   "Comercial",
                "qtd_notas":         "Qtd. Notas",
            }), use_container_width=True, hide_index=True)

            # ── Export histórico ──
            st.markdown('<div class="sec-title">⬇️ Exportar Histórico</div>', unsafe_allow_html=True)
            buf_hist = io.BytesIO()
            tbl.to_excel(buf_hist, index=False, engine="openpyxl")
            st.download_button(
                label="⬇️  Baixar Histórico em Excel",
                data=buf_hist.getvalue(),
                file_name=f"historico_financeiro_{data_de}_{data_ate}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # ── Apagar registro ──
            with st.expander("🗑️ Remover um registro do histórico"):
                datas_disp = h["data_fmt"].tolist()
                data_del = st.selectbox("Selecione a data para remover:", datas_disp)
                if st.button("Remover"):
                    data_del_fmt = pd.to_datetime(data_del, format="%d/%m/%Y").strftime("%Y-%m-%d")
                    hist_full = carregar_historico()
                    hist_full = hist_full[hist_full["data"].astype(str) != data_del_fmt]
                    hist_full.to_csv(HISTORICO_PATH, index=False)
                    st.success(f"Registro de {data_del} removido.")
                    st.rerun()