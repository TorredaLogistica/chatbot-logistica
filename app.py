
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Portal Torre Logística", layout="centered")

META_ATUAL = 94.1

st.markdown(
    """
    <style>
    .stApp { background: #efeae2; }
    .main .block-container { max-width: 1120px; padding-top: 1rem; padding-bottom: 1rem; }

    .topbar {
        background: linear-gradient(90deg, #075E54 0%, #0b6d62 100%);
        color: white; padding: 14px 16px; border-radius: 14px; margin-bottom: 14px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15); display: flex; align-items: center; gap: 12px;
    }
    .topbar-avatar {
        width: 42px; height: 42px; border-radius: 50%; background: rgba(255,255,255,0.18);
        display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: 700; flex-shrink: 0;
    }
    .topbar-title { font-size: 18px; font-weight: 700; line-height: 1.2; margin: 0; }
    .topbar-subtitle { font-size: 12px; opacity: 0.92; margin-top: 2px; }

    .menu-info {
        background: #ffffff; padding: 10px 12px; border-radius: 10px; margin: 8px 0 14px 0;
        border-left: 4px solid #25D366; box-shadow: 0 1px 2px rgba(0,0,0,0.06);
    }

    .card-wrap {
        background: #ffffff; border-radius: 14px; padding: 16px; margin-top: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08); border: 1px solid #e6e6e6;
    }
    .card-title { font-size: 18px; font-weight: 700; color: #075E54; margin-bottom: 6px; }
    .card-subtitle { font-size: 12px; color: #667781; margin-bottom: 14px; }

    .metric-box {
        background: #f7f7f7; border: 1px solid #e3e3e3; border-radius: 12px; padding: 12px;
        text-align: center; min-height: 290px; display: flex; flex-direction: column; justify-content: flex-start;
    }
    .metric-label { font-size: 12px; color: #667781; margin-bottom: 4px; }
    .metric-value { font-size: 22px; font-weight: 700; margin-bottom: 6px; }
    .metric-meta { font-size: 12px; font-weight: 700; color: #667781; margin-bottom: 8px; }
    .metric-list {
        margin-top: 10px; padding-top: 8px; border-top: 1px solid #e6e6e6; text-align: left;
    }
    .metric-list-title {
        font-size: 11px; color: #667781; font-weight: 700; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.02em;
    }
    .metric-line {
        display: flex; justify-content: space-between; gap: 8px; font-size: 12px; padding: 2px 0; line-height: 1.45;
    }
    .metric-name { font-weight: 600; color: #1f2937; }
    .metric-pct { font-weight: 700; }

    .month-list-box {
        background: #ffffff; border-radius: 14px; padding: 16px; margin-top: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08); border: 1px solid #e6e6e6;
    }
    .month-list-title { font-size: 18px; font-weight: 700; color: #075E54; margin-bottom: 6px; }
    .month-list-subtitle { font-size: 12px; color: #667781; margin-bottom: 14px; }
    .month-highlight {
        background: linear-gradient(90deg, #075E54 0%, #0b6d62 100%); color: white; border-radius: 12px;
        padding: 12px 14px; font-weight: 700; font-size: 16px; margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.12);
    }
    .month-table-card {
        background: #f7f7f7; border: 1px solid #e3e3e3; border-radius: 12px; padding: 12px;
    }
    .month-header-offensores {
        display: grid; grid-template-columns: 1.15fr 0.85fr 1fr 1fr; gap: 8px;
        font-size: 11px; color: #667781; font-weight: 700; margin-bottom: 4px;
        text-transform: uppercase; letter-spacing: 0.02em; align-items: center;
    }
    .month-header-offensores .off-label {
        grid-column: 3 / 5;
        display: flex; justify-content: center; align-items: center;
        text-align: center; color: #c62828; font-weight: 900; font-size: 12px; line-height: 1; width: 100%;
    }
    .month-header {
        display: grid; grid-template-columns: 1.15fr 0.85fr 1fr 1fr; gap: 8px;
        font-size: 11px; color: #667781; font-weight: 700; margin-bottom: 6px;
        text-transform: uppercase; letter-spacing: 0.02em; padding-bottom: 8px; border-bottom: 1px solid #e6e6e6;
        align-items: center;
    }
    .month-header .col-cd, .month-header .col-empresa {
        text-align: center; color: #075E54; font-weight: 800;
        background: rgba(7, 94, 84, 0.06); border-radius: 8px; padding: 4px 8px;
    }
    .month-list { margin-top: 6px; }
    .month-line {
        display: grid; grid-template-columns: 1.15fr 0.85fr 1fr 1fr; gap: 8px; font-size: 12px;
        padding: 6px 0; line-height: 1.45; border-bottom: 1px solid #ececec; align-items: center;
    }
    .month-line:last-child { border-bottom: none; }
    .month-name { font-weight: 600; color: #1f2937; }
    .month-pct { font-weight: 700; }
    .month-cd, .month-empresa {
        font-weight: 700; color: #1f2937; text-align: center;
        background: rgba(7, 94, 84, 0.06); border-radius: 8px; padding: 4px 8px;
    }
    .notranslate { white-space: nowrap; }

    @media (max-width: 768px) {
        .main .block-container { max-width: 100% !important; padding-left: 0.7rem; padding-right: 0.7rem; }
        .topbar { padding: 12px 14px; }
        .topbar-title { font-size: 16px; }
        .card-title, .month-list-title { font-size: 16px; }
        .month-header-offensores, .month-header { font-size: 10px; gap: 6px; }
        .month-line { font-size: 12px; gap: 6px; }
        .month-cd, .month-empresa, .month-header .col-cd, .month-header .col-empresa {
            padding: 4px 6px;
        }
    }

    div.stButton > button {
        border-radius: 10px !important; border: 1px solid #d0d7de !important; min-height: 42px !important;
        font-weight: 600 !important; background: white !important;
    }
    div.stButton > button:hover { border-color: #25D366 !important; color: #075E54 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


def cor_por_meta(valor_pct: str) -> str:
    valor = float(valor_pct.replace('%', '').replace(',', '.'))
    return '#1b5e20' if valor >= META_ATUAL else '#9c1c1c'


def sf_get_visao_geral_meses():
    return [
        ("Jun/26", "97,8%", "Barueri", "Net"),
        ("Mai/26", "95,3%", "Jaboatão", "Embratel"),
        ("Abr/26", "94,2%", "Rio de Janeiro", "Claro Fixo"),
        ("Mar/26", "96,1%", "Salvador", "Net"),
        ("Fev/26", "95,8%", "Manaus", "Claro TV"),
        ("Jan/26", "94,7%", "Barueri", "Embratel"),
        ("Dez/25", "93,9%", "Brasília", "Net"),
        ("Nov/25", "95,0%", "Palhoça", "Claro Fixo"),
        ("Out/25", "94,4%", "Campinas", "Net"),
        ("Set/25", "93,6%", "Contagem", "Embratel"),
        ("Ago/25", "92,9%", "Rio de Janeiro", "Claro TV"),
        ("Jul/25", "94,0%", "Jaboatão", "Net"),
    ]


def sf_get_sla_cds():
    return {
        "D+0": {"geral": "92,4%", "itens": [("Rio de Janeiro", "89,4%"), ("Jaboatão", "90,1%"), ("Salvador", "90,9%"), ("Manaus", "91,0%"), ("Barueri", "91,7%"), ("Brasília", "92,4%"), ("Palhoça", "93,0%"), ("Campinas", "93,2%"), ("Contagem", "93,5%")]},
        "D+1": {"geral": "97,8%", "itens": [("Salvador", "94,5%"), ("Manaus", "95,0%"), ("Jaboatão", "95,2%"), ("Rio de Janeiro", "95,9%"), ("Barueri", "96,8%"), ("Brasília", "97,1%"), ("Palhoça", "97,4%"), ("Contagem", "97,9%"), ("Campinas", "98,4%")]},
        "D+2": {"geral": "99,1%", "itens": [("Salvador", "98,2%"), ("Manaus", "98,4%"), ("Jaboatão", "98,6%"), ("Rio de Janeiro", "98,8%"), ("Barueri", "98,9%"), ("Brasília", "99,0%"), ("Palhoça", "99,1%"), ("Contagem", "99,3%"), ("Campinas", "99,4%")]},
    }


def sf_get_sla_empresas():
    return {
        "D+0": {"geral": "92,4%", "itens": [("Net", "90,8%"), ("Embratel", "91,3%"), ("Claro Fixo", "91,7%"), ("Claro TV", "92,6%"), ("Claro Móvel", "93,4%")]},
        "D+1": {"geral": "97,8%", "itens": [("Net", "94,6%"), ("Embratel", "95,8%"), ("Claro Fixo", "96,9%"), ("Claro TV", "97,6%"), ("Claro Móvel", "98,3%")]},
        "D+2": {"geral": "99,1%", "itens": [("Net", "98,4%"), ("Embratel", "98,8%"), ("Claro Fixo", "99,0%"), ("Claro TV", "99,2%"), ("Claro Móvel", "99,5%")]},
    }


def render_card_titulo(titulo: str, subtitulo: str = ""):
    st.markdown(
        '<div class="card-wrap">'
        f'<div class="card-title">{titulo}</div>'
        f'<div class="card-subtitle">{subtitulo}</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_metricas_sla(sla_dict: dict, lista_titulo: str):
    c1, c2, c3 = st.columns(3)
    for col, (label, value_dict) in zip([c1, c2, c3], sla_dict.items()):
        linhas_html = ''.join(
            [
                '<div class="metric-line">'
                f'<span class="metric-name">{nome}</span>'
                f'<span class="metric-pct notranslate" translate="no" style="color:{cor_por_meta(pct)};">{pct}</span>'
                '</div>'
                for nome, pct in value_dict["itens"]
            ]
        )
        meta_html = '<div class="metric-meta notranslate" translate="no">Meta atual: 94,1%</div>' if label == 'D+1' else ''
        with col:
            st.markdown(
                '<div class="metric-box">'
                f'<div class="metric-label notranslate" translate="no">{label}</div>'
                f'<div class="metric-value notranslate" translate="no" style="color:{cor_por_meta(value_dict["geral"])};">{value_dict["geral"]}</div>'
                f'{meta_html}'
                '<div class="metric-list">'
                f'<div class="metric-list-title notranslate" translate="no">{lista_titulo}</div>'
                f'{linhas_html}'
                '</div>'
                '</div>',
                unsafe_allow_html=True,
            )


def render_visao_geral_meses():
    meses = sf_get_visao_geral_meses()
    linhas_html = ''.join(
        [
            '<div class="month-line">'
            f'<span class="month-name notranslate" translate="no">{mes}</span>'
            f'<span class="month-pct notranslate" translate="no" style="color:{cor_por_meta(sla)};">{sla}</span>'
            f'<span class="month-cd notranslate" translate="no">{cd}</span>'
            f'<span class="month-empresa notranslate" translate="no">{empresa}</span>'
            '</div>'
            for mes, sla, cd, empresa in meses
        ]
    )
    html = (
        '<div class="month-list-box">'
        '<div class="month-list-title">Separação e Faturamento | Visão Geral</div>'
        '<div class="month-list-subtitle">Últimos 12 meses do mais atual para o mais antigo.</div>'
        '<div class="month-highlight notranslate" translate="no">Claro Brasil</div>'
        '<div class="month-table-card">'
        '<div class="month-header-offensores"><span></span><span></span><span class="off-label notranslate" translate="no">OFENSORES</span></div>'
        '<div class="month-header"><span class="notranslate" translate="no">Mês</span><span class="notranslate" translate="no">SLA</span><span class="col-cd notranslate" translate="no">CD</span><span class="col-empresa notranslate" translate="no">Empresa</span></div>'
        '<div class="month-list">'
        f'{linhas_html}'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


if "step" not in st.session_state:
    st.session_state.step = 0
if "nome" not in st.session_state:
    st.session_state.nome = ""
if "indicador" not in st.session_state:
    st.session_state.indicador = None
if "sf_visao" not in st.session_state:
    st.session_state.sf_visao = None

html_topbar = (
    '<div class="topbar">'
    '<div class="topbar-avatar">TL</div>'
    '<div>'
    '<div class="topbar-title">Portal Torre Logística</div>'
    '<div class="topbar-subtitle">Assistente para navegação dos indicadores</div>'
    '</div>'
    '</div>'
)
st.markdown(html_topbar, unsafe_allow_html=True)

if st.session_state.step == 0:
    st.info("Para iniciar, informe o seu nome.")
    nome = st.text_input("Nome")
    if st.button("Continuar", use_container_width=True):
        st.session_state.nome = nome.strip() if nome else "Usuário"
        st.session_state.step = 1
        st.rerun()

elif st.session_state.step == 1:
    st.success(f"Prazer, {st.session_state.nome}!")
    st.markdown('<div class="menu-info"><strong>Opções disponíveis:</strong><br>Separação e Faturamento | Pedidos para LPs | Resultado do DRE | Valores dos EAs</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("Separação e Faturamento", use_container_width=True):
        st.session_state.indicador = "sf"
        st.session_state.sf_visao = None
        st.session_state.step = 2
        st.rerun()
    if c2.button("Pedidos para LPs", use_container_width=True):
        st.warning("No momento o fluxo de Pedidos para LPs está em construção.")
    if c3.button("Resultado do DRE", use_container_width=True):
        st.warning("No momento o fluxo de Resultado do DRE está em construção.")
    if c4.button("Valores dos EAs", use_container_width=True):
        st.warning("No momento o fluxo de Valores dos EAs está em construção.")

elif st.session_state.step == 2 and st.session_state.indicador == "sf":
    st.markdown('<div class="menu-info"><strong>Opções disponíveis:</strong><br>Visão Geral | Visão por CDs | Visão por Empresas</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)

    if c1.button("Visão Geral", use_container_width=True):
        st.session_state.sf_visao = "geral"
        st.rerun()
    if c2.button("Visão por CDs", use_container_width=True):
        st.session_state.sf_visao = "cds"
        st.rerun()
    if c3.button("Visão por Empresas", use_container_width=True):
        st.session_state.sf_visao = "empresas"
        st.rerun()

    if st.session_state.sf_visao == "geral":
        render_visao_geral_meses()
    elif st.session_state.sf_visao == "cds":
        render_card_titulo(
            "Separação e Faturamento | Visão por CDs | SLA do mês atual",
            "Dados de exemplo / placeholders. Depois basta conectar à lógica real do seu indicador.",
        )
        render_metricas_sla(sf_get_sla_cds(), "CDs")
    elif st.session_state.sf_visao == "empresas":
        render_card_titulo(
            "Separação e Faturamento | Visão por Empresas | SLA do mês atual",
            "Dados de exemplo / placeholders. Depois basta conectar à lógica real do seu indicador.",
        )
        render_metricas_sla(sf_get_sla_empresas(), "Empresas")

    c1, c2 = st.columns(2)
    if c1.button("Voltar aos indicadores", use_container_width=True):
        st.session_state.step = 1
        st.session_state.indicador = None
        st.session_state.sf_visao = None
        st.rerun()
    if c2.button("Reiniciar conversa", use_container_width=True):
        st.session_state.step = 0
        st.session_state.nome = ""
        st.session_state.indicador = None
        st.session_state.sf_visao = None
        st.rerun()
