import os
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Portal Torre Logística", layout="centered")

ARQUIVO_BASE = "Faturamento SLA 2026.xlsb"
COR_NEUTRA = "#1f2937"
MESES_BR = {
    '01': 'Jan', '02': 'Fev', '03': 'Mar', '04': 'Abr', '05': 'Mai', '06': 'Jun',
    '07': 'Jul', '08': 'Ago', '09': 'Set', '10': 'Out', '11': 'Nov', '12': 'Dez'
}

# Metas trazidas do dashboard_bi.py
METAS_CLARO_BRASIL = {
    "01/2025": 76.09, "02/2025": 74.38, "03/2025": 79.52, "04/2025": 72.28,
    "05/2025": 81.73, "06/2025": 88.07, "07/2025": 82.91, "08/2025": 89.19,
    "09/2025": 92.77, "10/2025": 88.68, "11/2025": 82.47, "12/2025": 85.94,
    "01/2026": 94.45, "02/2026": 94.65, "03/2026": 94.63, "04/2026": 94.93,
    "05/2026": 94.31, "06/2026": 94.21, "07/2026": 94.36, "08/2026": 95.80,
    "09/2026": 95.36, "10/2026": 95.47, "11/2026": 95.56, "12/2026": 95.47
}
METAS_CLARO_BRASIL = {"01/2025": 76.09, "02/2025": 74.38, "03/2025": 79.52, "04/2025": 72.28, "05/2025": 81.73, "06/2025": 88.07, "07/2025": 82.91, "08/2025": 89.19, "09/2025": 92.77, "10/2025": 88.68, "11/2025": 82.47, "12/2025": 85.94, "01/2026": 94.45, "02/2026": 94.65, "03/2026": 94.63, "04/2026": 94.93, "05/2026": 94.31, "06/2026": 94.21, "07/2026": 94.36, "08/2026": 95.80, "09/2026": 95.36, "10/2026": 95.47, "11/2026": 95.56, "12/2026": 95.47}
METAS_NET = {"01/2026": 90.00, "02/2026": 90.00, "03/2026": 90.00, "04/2026": 90.00, "05/2026": 90.00, "06/2026": 90.00, "07/2026": 90.00, "08/2026": 92.00, "09/2026": 92.00, "10/2026": 92.00, "11/2026": 92.00, "12/2026": 92.00}
METAS_CLARO_TV = {"01/2026": 85.02, "02/2026": 85.11, "03/2026": 85.19,  "04/2026": 85.04, "05/2026": 84.80, "06/2026": 84.90, "07/2026": 85.19, "08/2026": 84.77, "09/2026": 84.97, "10/2026": 84.97, "11/2026": 85.05, "12/2026": 84.97}
METAS_EMBRATEL = {"01/2026": 80.00, "02/2026": 80.00, "03/2026": 80.01, "04/2026": 80.02, "05/2026": 80.01, "06/2026": 79.99, "07/2026": 79.99, "08/2026": 82.00, "09/2026": 81.98, "10/2026": 82.01, "11/2026": 82.00, "12/2026": 82.00}
METAS_CLARO_MOVEL = {"01/2026": 99.50, "02/2026": 99.50, "03/2026": 99.50, "04/2026": 99.50, "05/2026": 99.50, "06/2026": 99.50, "07/2026": 99.50, "08/2026": 99.50, "09/2026": 99.50, "10/2026": 99.50, "11/2026": 99.50, "12/2026": 99.50}

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
    .metric-list { margin-top: 10px; padding-top: 8px; border-top: 1px solid #e6e6e6; text-align: left; }
    .metric-list-title { font-size: 11px; color: #667781; font-weight: 700; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.02em; }
    .metric-line { display: flex; justify-content: space-between; gap: 8px; font-size: 12px; padding: 2px 0; line-height: 1.45; }
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
    .month-header .col-cd, .month-header .col-pct-cd {
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
    .month-cd, .month-pct-cd {
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
        .month-cd, .month-pct-cd, .month-header .col-cd, .month-header .col-pct-cd { padding: 4px 6px; }
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


def mes_br(mm_yyyy: str) -> str:
    mm, yyyy = mm_yyyy.split('/')
    return f"{MESES_BR.get(mm, mm)}/{yyyy[-2:]}"


def cor_por_meta(valor_pct: str, meta: float) -> str:
    valor = float(str(valor_pct).replace('%', '').replace(',', '.'))
    return '#1b5e20' if valor >= meta else '#9c1c1c'


def fmt_pct(valor: float) -> str:
    return f"{valor:.2f}%".replace('.', ',')


def normalizar_categoria(s: pd.Series, valor_padrao='Não informado') -> pd.Series:
    s = (s.fillna(valor_padrao)
           .astype(str)
           .str.replace('\u00A0', '', regex=False)
           .str.strip())
    return s.replace({'': valor_padrao, 'nan': valor_padrao, 'NaN': valor_padrao, 'None': valor_padrao, '<NA>': valor_padrao, 'undefined': valor_padrao})


def meta_empresa_mes(mes: str, empresa: str | None = None) -> float:
    if empresa == 'NET':
        return METAS_NET.get(mes, METAS_CLARO_BRASIL.get(mes, 85.0))
    if empresa == 'Claro TV':
        return METAS_CLARO_TV.get(mes, METAS_CLARO_BRASIL.get(mes, 85.0))
    if empresa == 'Embratel':
        return METAS_EMBRATEL.get(mes, METAS_CLARO_BRASIL.get(mes, 85.0))
    if empresa == 'Claro Movel':
        return METAS_CLARO_MOVEL.get(mes, METAS_CLARO_BRASIL.get(mes, 85.0))
    return METAS_CLARO_BRASIL.get(mes, 85.0)


@st.cache_data(show_spinner=False)
def carregar_base_real(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Arquivo {path} não encontrado na raiz do repositório.")
    df = pd.read_excel(path, engine='pyxlsb')
    df.columns = df.columns.str.strip()
    if 'Pedido' not in df.columns and 'Pedidos' in df.columns:
        df['Pedido'] = df['Pedidos']
    for col in ['CD Origem', 'Empresa', 'Canal de Atuacao', 'Canal', 'Operador', 'Unidade de Negocio']:
        if col in df.columns:
            df[col] = normalizar_categoria(df[col])
    if 'Data NF' not in df.columns:
        raise KeyError("Coluna 'Data NF' não encontrada na base.")
    if 'Aging_Ajustado_D+' not in df.columns:
        raise KeyError("Coluna 'Aging_Ajustado_D+' não encontrada na base.")

    def _converter_data_excel(serie: pd.Series) -> pd.Series:
        s = serie.copy()
        if pd.api.types.is_numeric_dtype(s):
            return pd.to_datetime(s, unit='D', origin='1899-12-30', errors='coerce')
        s_num = pd.to_numeric(s, errors='coerce')
        out = pd.to_datetime(s, errors='coerce', dayfirst=True)
        mask_num = s_num.notna() & out.isna()
        if mask_num.any():
            out.loc[mask_num] = pd.to_datetime(s_num.loc[mask_num], unit='D', origin='1899-12-30', errors='coerce')
        return out

    df['Data NF'] = _converter_data_excel(df['Data NF'])
    df = df[df['Data NF'].notna()].copy()
    df['Mes_Ano'] = df['Data NF'].dt.strftime('%m/%Y')
    aging = df['Aging_Ajustado_D+'].astype(str).str.extract(r'D\+(\d+)')[0]
    df['aging_num'] = pd.to_numeric(aging, errors='coerce')
    df = df[df['aging_num'].notna()].copy()
    df['aging_num'] = df['aging_num'].astype(int)
    df['flag_d0'] = df['aging_num'] == 0
    df['flag_d1'] = df['aging_num'] == 1
    df['flag_d2'] = df['aging_num'] == 2
    return df


def calc_metrica(df_base: pd.DataFrame) -> dict:
    total = len(df_base)
    if total == 0:
        return {'D+0': 0.0, 'D+1': 0.0, 'D+2': 0.0}
    d0 = df_base['flag_d0'].sum() / total * 100
    d1 = (df_base['flag_d0'] | df_base['flag_d1']).sum() / total * 100
    d2 = (df_base['flag_d0'] | df_base['flag_d1'] | df_base['flag_d2']).sum() / total * 100
    return {'D+0': d0, 'D+1': d1, 'D+2': d2}


def construir_visao_geral(df: pd.DataFrame) -> list:
    meses = sorted(df['Mes_Ano'].dropna().unique(), key=lambda x: datetime.strptime(x, '%m/%Y'), reverse=True)[:12]
    linhas = []
    for mes in meses:
        base = df[df['Mes_Ano'] == mes].copy()
        metrica = calc_metrica(base)
        if 'CD Origem' in base.columns:
            grp_cd = base.groupby('CD Origem').apply(lambda g: calc_metrica(g)['D+1']).sort_values()
            pior_cd = grp_cd.index[0] if len(grp_cd) else 'Não informado'
            pior_cd_pct = fmt_pct(float(grp_cd.iloc[0])) if len(grp_cd) else '0,00%'
        else:
            pior_cd = 'Não informado'
            pior_cd_pct = '0,00%'
        mes_label = mes_br(mes)
        meta_mes = meta_empresa_mes(mes)
        linhas.append((mes_label, fmt_pct(metrica['D+1']), pior_cd, pior_cd_pct, meta_mes))
    return linhas


def construir_visao_grupo(df: pd.DataFrame, coluna: str) -> dict:
    meses = sorted(df['Mes_Ano'].dropna().unique(), key=lambda x: datetime.strptime(x, '%m/%Y'))
    mes_atual = meses[-1] if meses else None
    base = df[df['Mes_Ano'] == mes_atual].copy() if mes_atual else df.head(0).copy()
    meta_atual = meta_empresa_mes(mes_atual) if mes_atual else 85.0
    resultado = {}
    for chave in ['D+0', 'D+1', 'D+2']:
        itens = []
        if coluna in base.columns:
            for nome, grp in base.groupby(coluna):
                m = calc_metrica(grp)[chave]
                meta_item = meta_empresa_mes(mes_atual, str(nome)) if (coluna == 'Empresa' and mes_atual and chave == 'D+1') else None
                itens.append((str(nome), fmt_pct(m), meta_item))
            itens = sorted(itens, key=lambda x: float(x[1].replace('%', '').replace(',', '.')))
        resultado[chave] = {'geral': fmt_pct(calc_metrica(base)[chave]), 'itens': itens, 'meta_atual': meta_atual, 'mes_atual': mes_atual}
    return resultado


def render_card_titulo(titulo: str, subtitulo: str = ""):
    st.markdown(
        '<div class="card-wrap">'
        f'<div class="card-title">{titulo}</div>'
        f'<div class="card-subtitle">{subtitulo}</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def cor_percentual_card(label: str, pct: str, meta: float) -> str:
    return cor_por_meta(pct, meta) if label == 'D+1' else COR_NEUTRA


def render_metricas_sla(sla_dict: dict, lista_titulo: str, coluna: str):
    c1, c2, c3 = st.columns(3)
    for col, (label, value_dict) in zip([c1, c2, c3], sla_dict.items()):
        meta_atual = value_dict.get('meta_atual', 85.0)
        mes_atual = value_dict.get('mes_atual')
        linhas_html = ''
        if coluna == 'Empresa' and label == 'D+1':
            linhas_html += '<div class="metric-line" style="font-weight:800;border-bottom:1px solid #e6e6e6;padding-bottom:4px;margin-bottom:4px;"><span class="metric-name">Empresa</span><span class="metric-pct">SLA</span><span class="metric-pct">Meta</span></div>'
            for nome, pct, meta_item in value_dict['itens']:
                meta_txt = fmt_pct(meta_item if meta_item is not None else meta_atual)
                cor = cor_percentual_card(label, pct, meta_item if meta_item is not None else meta_atual)
                linhas_html += (
                    '<div class="metric-line">'
                    f'<span class="metric-name">{nome}</span>'
                    f'<span class="metric-pct" style="color:{cor};">{pct}</span>'
                    f'<span class="metric-pct">{meta_txt}</span>'
                    '</div>'
                )
        else:
            linhas_html = ''.join([
                '<div class="metric-line">'
                f'<span class="metric-name">{nome}</span>'
                f'<span class="metric-pct notranslate" translate="no" style="color:{cor_percentual_card(label, pct, meta_atual)};">{pct}</span>'
                '</div>'
                for nome, pct, _meta in value_dict['itens']
            ])

        meta_html = f'<div class="metric-meta notranslate" translate="no">Meta atual: {fmt_pct(meta_atual)} ({mes_br(mes_atual)})</div>' if (label == 'D+1' and mes_atual) else ''
        geral_cor = cor_percentual_card(label, value_dict['geral'], meta_atual)
        with col:
            st.markdown(
                '<div class="metric-box">'
                f'<div class="metric-label notranslate" translate="no">{label}</div>'
                f'<div class="metric-value notranslate" translate="no" style="color:{geral_cor};">{value_dict["geral"]}</div>'
                f'{meta_html}'
                '<div class="metric-list">'
                f'<div class="metric-list-title notranslate" translate="no">{lista_titulo}</div>'
                f'{linhas_html}'
                '</div>'
                '</div>',
                unsafe_allow_html=True,
            )


def render_visao_geral_meses(linhas: list):
    linhas_html = ''.join(
        [
            '<div class="month-line">'
            f'<span class="month-name notranslate" translate="no">{mes}</span>'
            f'<span class="month-pct notranslate" translate="no" style="color:{cor_por_meta(sla, meta_mes)};">{sla}</span>'
            f'<span class="month-cd">{cd}</span>'
            f'<span class="month-pct-cd notranslate" translate="no">{pct_cd}</span>'
            '</div>'
            for mes, sla, cd, pct_cd, meta_mes in linhas
        ]
    )
    html = (
        '<div class="month-list-box">'
        '<div class="month-list-title">Separação e Faturamento | Visão Geral</div>'
        '<div class="month-list-subtitle">Últimos 12 meses do mais atual para o mais antigo.</div>'
        '<div class="month-highlight notranslate" translate="no">Claro Brasil</div>'
        '<div class="month-table-card">'
        '<div class="month-header-offensores"><span></span><span></span><span class="off-label notranslate" translate="no">OFENSORES</span></div>'
        '<div class="month-header"><span class="notranslate" translate="no">Mês</span><span class="notranslate" translate="no">SLA</span><span class="col-cd notranslate" translate="no">CD</span><span class="col-pct-cd notranslate" translate="no">% CD Ofensor</span></div>'
        '<div class="month-list">'
        f'{linhas_html}'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


if 'step' not in st.session_state:
    st.session_state.step = 0
if 'nome' not in st.session_state:
    st.session_state.nome = ''
if 'indicador' not in st.session_state:
    st.session_state.indicador = None
if 'sf_visao' not in st.session_state:
    st.session_state.sf_visao = None

base_real = None
erro_base = None
try:
    base_real = carregar_base_real(ARQUIVO_BASE)
except Exception as e:
    erro_base = str(e)

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

if erro_base:
    st.warning(f"Base real não carregada: {erro_base}")
else:
    st.caption(f"Base real carregada: {ARQUIVO_BASE}")

if st.session_state.step == 0:
    st.info('Para iniciar, informe o seu nome.')
    nome = st.text_input('Nome')
    if st.button('Continuar', use_container_width=True):
        st.session_state.nome = nome.strip() if nome else 'Usuário'
        st.session_state.step = 1
        st.rerun()

elif st.session_state.step == 1:
    st.success(f"Prazer, {st.session_state.nome}!")
    st.markdown('<div class="menu-info"><strong>Opções disponíveis:</strong><br>Separação e Faturamento | Pedidos para LPs | Resultado do DRE | Valores dos EAs</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    if c1.button('Separação e Faturamento', use_container_width=True):
        st.session_state.indicador = 'sf'
        st.session_state.sf_visao = None
        st.session_state.step = 2
        st.rerun()
    if c2.button('Pedidos para LPs', use_container_width=True):
        st.warning('No momento o fluxo de Pedidos para LPs está em construção.')
    if c3.button('Resultado do DRE', use_container_width=True):
        st.warning('No momento o fluxo de Resultado do DRE está em construção.')
    if c4.button('Valores dos EAs', use_container_width=True):
        st.warning('No momento o fluxo de Valores dos EAs está em construção.')

elif st.session_state.step == 2 and st.session_state.indicador == 'sf':
    st.markdown('<div class="menu-info"><strong>Opções disponíveis:</strong><br>Visão Geral | Visão por CDs | Visão por Empresas</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button('Visão Geral', use_container_width=True):
        st.session_state.sf_visao = 'geral'
        st.rerun()
    if c2.button('Visão por CDs', use_container_width=True):
        st.session_state.sf_visao = 'cds'
        st.rerun()
    if c3.button('Visão por Empresas', use_container_width=True):
        st.session_state.sf_visao = 'empresas'
        st.rerun()

    if base_real is not None:
        if st.session_state.sf_visao == 'geral':
            render_visao_geral_meses(construir_visao_geral(base_real))
        elif st.session_state.sf_visao == 'cds':
            render_card_titulo('Separação e Faturamento | Visão por CDs | SLA do mês atual', 'Dados reais da base Faturamento SLA 2026.xlsb.')
            render_metricas_sla(construir_visao_grupo(base_real, 'CD Origem'), 'CDs', 'CD Origem')
        elif st.session_state.sf_visao == 'empresas':
            render_card_titulo('Separação e Faturamento | Visão por Empresas | SLA do mês atual', 'Dados reais da base Faturamento SLA 2026.xlsb.')
            render_metricas_sla(construir_visao_grupo(base_real, 'EMPRESA'), 'Empresas', 'Empresa')
    else:
        st.error('Não foi possível carregar a base real. Verifique se o arquivo .xlsb está na raiz do repositório e se o requirements contém pyxlsb.')

    c1, c2 = st.columns(2)
    if c1.button('Voltar aos indicadores', use_container_width=True):
        st.session_state.step = 1
        st.session_state.indicador = None
        st.session_state.sf_visao = None
        st.rerun()
    if c2.button('Reiniciar conversa', use_container_width=True):
        st.session_state.step = 0
        st.session_state.nome = ''
        st.session_state.indicador = None
        st.session_state.sf_visao = None
        st.rerun()
