import os
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Portal Torre Logística", layout="centered")

META_ATUAL = 94.1
ARQUIVO_BASE = "Faturamento SLA 2026.xlsb"
COR_NEUTRA = "#1f2937"
MESES_BR = {
    '01': 'Jan', '02': 'Fev', '03': 'Mar', '04': 'Abr', '05': 'Mai', '06': 'Jun',
    '07': 'Jul', '08': 'Ago', '09': 'Set', '10': 'Out', '11': 'Nov', '12': 'Dez'
}

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

    .month-card {
        background: #ffffff; border-radius: 14px; padding: 16px; margin-top: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08); border: 1px solid #e6e6e6;
    }
    .month-title { font-size: 18px; font-weight: 700; color: #075E54; margin-bottom: 6px; }
    .month-subtitle { font-size: 12px; color: #667781; margin-bottom: 14px; }
    .month-highlight {
        background: linear-gradient(90deg, #075E54 0%, #0b6d62 100%); color: white; border-radius: 12px;
        padding: 12px 14px; font-weight: 700; font-size: 16px; margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.12);
    }
    .ofensores-label { color: #c62828; font-weight: 900; text-align: center; font-size: 12px; margin-bottom: 6px; }
    .header-pill {
        background: rgba(7, 94, 84, 0.06); color: #075E54; border-radius: 8px; padding: 6px 8px;
        text-align: center; font-weight: 800; font-size: 11px; text-transform: uppercase;
    }
    .header-cell { color: #667781; font-weight: 700; font-size: 11px; text-transform: uppercase; padding: 6px 2px; }
    .cell-month { font-weight: 700; color: #1f2937; padding-top: 10px; }
    .cell-sla { font-weight: 800; padding-top: 10px; }
    .pill-neutro {
        background: rgba(7, 94, 84, 0.06); border-radius: 8px; padding: 8px 10px; text-align: center;
        font-weight: 700; color: #1f2937; margin-top: 4px;
    }
    .row-sep { border-top: 1px solid #ececec; margin-top: 8px; padding-top: 8px; }
    .notranslate { white-space: nowrap; }

    div.stButton > button {
        border-radius: 10px !important; border: 1px solid #d0d7de !important; min-height: 38px !important;
        font-weight: 700 !important; background: rgba(7, 94, 84, 0.06) !important; color: #1f2937 !important;
        width: 100% !important;
    }
    div.stButton > button:hover { border-color: #25D366 !important; color: #075E54 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


def mes_br(mm_yyyy: str) -> str:
    mm, yyyy = mm_yyyy.split('/')
    return f"{MESES_BR.get(mm, mm)}/{yyyy[-2:]}"


def cor_por_meta(valor_pct: str) -> str:
    valor = float(str(valor_pct).replace('%', '').replace(',', '.'))
    return '#1b5e20' if valor >= META_ATUAL else '#9c1c1c'


def fmt_pct(valor: float) -> str:
    return f"{valor:.2f}%".replace('.', ',')


def normalizar_categoria(s: pd.Series, valor_padrao='Não informado') -> pd.Series:
    s = (s.fillna(valor_padrao).astype(str).str.replace('\u00A0', '', regex=False).str.strip())
    return s.replace({'': valor_padrao, 'nan': valor_padrao, 'NaN': valor_padrao, 'None': valor_padrao, '<NA>': valor_padrao, 'undefined': valor_padrao})


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
        metrica_mes = calc_metrica(base)
        if 'CD Origem' in base.columns:
            grp_cd = base.groupby('CD Origem').apply(lambda g: calc_metrica(g)['D+1']).sort_values()
            if len(grp_cd):
                pior_cd = grp_cd.index[0]
                pior_cd_pct = fmt_pct(float(grp_cd.iloc[0]))
            else:
                pior_cd = 'Não informado'
                pior_cd_pct = '0,00%'
        else:
            pior_cd = 'Não informado'
            pior_cd_pct = '0,00%'
        linhas.append((mes_br(mes), fmt_pct(metrica_mes['D+1']), pior_cd, pior_cd_pct, mes))
    return linhas


def construir_visao_grupo(df: pd.DataFrame, coluna: str, filtro_cd: str | None = None, mes_ref: str | None = None) -> dict:
    if mes_ref:
        base = df[df['Mes_Ano'] == mes_ref].copy()
    else:
        meses = sorted(df['Mes_Ano'].dropna().unique(), key=lambda x: datetime.strptime(x, '%m/%Y'))
        mes_atual = meses[-1] if meses else None
        base = df[df['Mes_Ano'] == mes_atual].copy() if mes_atual else df.head(0).copy()
    if filtro_cd and 'CD Origem' in base.columns:
        base = base[base['CD Origem'] == filtro_cd].copy()

    geral = calc_metrica(base)
    resultado = {}
    for chave in ['D+0', 'D+1', 'D+2']:
        itens = []
        if coluna in base.columns:
            for nome, grp in base.groupby(coluna):
                m = calc_metrica(grp)[chave]
                itens.append((str(nome), fmt_pct(m)))
            itens = sorted(itens, key=lambda x: float(x[1].replace('%', '').replace(',', '.')))
        resultado[chave] = {'geral': fmt_pct(geral[chave]), 'itens': itens}
    return resultado


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
        linhas_html = ''.join([
            '<div class="metric-line">'
            f'<span class="metric-name">{nome}</span>'
            f'<span class="metric-pct" style="color:{cor_por_meta(pct) if label == "D+1" else COR_NEUTRA};">{pct}</span>'
            '</div>'
            for nome, pct in value_dict['itens']
        ])
        meta_html = '<div class="metric-meta">Meta atual: 94,1%</div>' if label == 'D+1' else ''
        geral_cor = cor_por_meta(value_dict['geral']) if label == 'D+1' else COR_NEUTRA
        with col:
            st.markdown(
                '<div class="metric-box">'
                f'<div class="metric-label">{label}</div>'
                f'<div class="metric-value" style="color:{geral_cor};">{value_dict["geral"]}</div>'
                f'{meta_html}'
                '<div class="metric-list">'
                f'<div class="metric-list-title">{lista_titulo}</div>'
                f'{linhas_html}'
                '</div>'
                '</div>',
                unsafe_allow_html=True,
            )


def render_visao_geral_interativa(linhas: list):
    with st.container(border=True):
        st.markdown('<div class="month-title">Separação e Faturamento | Visão Geral</div>', unsafe_allow_html=True)
        st.markdown('<div class="month-subtitle">Últimos 12 meses do mais atual para o mais antigo.</div>', unsafe_allow_html=True)
        st.markdown('<div class="month-highlight">Claro Brasil</div>', unsafe_allow_html=True)

        h1, h2, h3, h4 = st.columns([1.15, 0.85, 1, 1])
        with h1:
            st.markdown('<div class="header-cell">Mês</div>', unsafe_allow_html=True)
        with h2:
            st.markdown('<div class="header-cell">SLA</div>', unsafe_allow_html=True)
        with h3:
            st.markdown('<div class="ofensores-label">OFENSORES</div><div class="header-pill">CD</div>', unsafe_allow_html=True)
        with h4:
            st.markdown('<div class="ofensores-label">&nbsp;</div><div class="header-pill">% CD Ofensor</div>', unsafe_allow_html=True)

        for idx, (mes_label, sla, cd, pct_cd, mes_original) in enumerate(linhas):
            c1, c2, c3, c4 = st.columns([1.15, 0.85, 1, 1])
            with c1:
                st.markdown(f'<div class="cell-month">{mes_label}</div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="cell-sla" style="color:{cor_por_meta(sla)};">{sla}</div>', unsafe_allow_html=True)
            with c3:
                if st.button(cd, key=f'cd_ofensor_{idx}_{mes_original}', use_container_width=True):
                    st.session_state.cd_ofensor_selecionado = cd
                    st.session_state.cd_ofensor_mes = mes_original
                    st.rerun()
            with c4:
                st.markdown(f'<div class="pill-neutro">{pct_cd}</div>', unsafe_allow_html=True)
            st.markdown('<div class="row-sep"></div>', unsafe_allow_html=True)


if 'step' not in st.session_state:
    st.session_state.step = 0
if 'nome' not in st.session_state:
    st.session_state.nome = ''
if 'indicador' not in st.session_state:
    st.session_state.indicador = None
if 'sf_visao' not in st.session_state:
    st.session_state.sf_visao = None
if 'cd_ofensor_selecionado' not in st.session_state:
    st.session_state.cd_ofensor_selecionado = None
if 'cd_ofensor_mes' not in st.session_state:
    st.session_state.cd_ofensor_mes = None

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
        st.rerun()
    if c2.button('Pedidos para LPs', use_container_width=True):
        st.warning('No momento o fluxo de Pedidos para LPs está em construção.')
    if c3.button('Resultado do DRE', use_container_width=True):
        st.warning('No momento o fluxo de Resultado do DRE está em construção.')
    if c4.button('Valores dos EAs', use_container_width=True):
        st.warning('No momento o fluxo de Valores dos EAs está em construção.')

if st.session_state.indicador == 'sf':
    st.markdown('<div class="menu-info"><strong>Opções disponíveis:</strong><br>Visão Geral | Visão por CDs | Visão por Empresas</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button('Visão Geral', use_container_width=True):
        st.session_state.sf_visao = 'geral'
        st.rerun()
    if c2.button('Visão por CDs', use_container_width=True):
        st.session_state.sf_visao = 'cds'
        st.session_state.cd_ofensor_selecionado = None
        st.rerun()
    if c3.button('Visão por Empresas', use_container_width=True):
        st.session_state.sf_visao = 'empresas'
        st.session_state.cd_ofensor_selecionado = None
        st.rerun()

    if base_real is not None:
        if st.session_state.sf_visao == 'geral':
            linhas = construir_visao_geral(base_real)
            render_visao_geral_interativa(linhas)
            if st.session_state.cd_ofensor_selecionado:
                cd_sel = st.session_state.cd_ofensor_selecionado
                mes_sel = st.session_state.cd_ofensor_mes
                render_card_titulo(
                    f'Separação e Faturamento | Detalhe por Empresa do CD {cd_sel}',
                    f'Dados reais do mês {mes_br(mes_sel)} para o CD ofensor selecionado.' if mes_sel else 'Dados reais do CD ofensor selecionado.'
                )
                render_metricas_sla(construir_visao_grupo(base_real, 'Empresa', filtro_cd=cd_sel, mes_ref=mes_sel), 'Empresas')
        elif st.session_state.sf_visao == 'cds':
            render_card_titulo('Separação e Faturamento | Visão por CDs | SLA do mês atual', 'Dados reais da base Faturamento SLA 2026.xlsb.')
            render_metricas_sla(construir_visao_grupo(base_real, 'CD Origem'), 'CDs')
        elif st.session_state.sf_visao == 'empresas':
            render_card_titulo('Separação e Faturamento | Visão por Empresas | SLA do mês atual', 'Dados reais da base Faturamento SLA 2026.xlsb.')
            render_metricas_sla(construir_visao_grupo(base_real, 'Empresa'), 'Empresas')
    else:
        st.error('Não foi possível carregar a base real. Verifique se o arquivo .xlsb está na raiz do repositório e se o requirements contém pyxlsb.')

    c1, c2 = st.columns(2)
    if c1.button('Voltar aos indicadores', use_container_width=True):
        st.session_state.indicador = None
        st.session_state.sf_visao = None
        st.session_state.cd_ofensor_selecionado = None
        st.session_state.cd_ofensor_mes = None
        st.rerun()
    if c2.button('Reiniciar conversa', use_container_width=True):
        st.session_state.step = 0
        st.session_state.nome = ''
        st.session_state.indicador = None
        st.session_state.sf_visao = None
        st.session_state.cd_ofensor_selecionado = None
        st.session_state.cd_ofensor_mes = None
        st.rerun()
