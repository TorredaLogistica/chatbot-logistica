import os
import re
import calendar
import unicodedata
from pathlib import Path
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

METAS_CLARO_BRASIL = {
    "01/2025": 76.09, "02/2025": 74.38, "03/2025": 79.52, "04/2025": 72.28,
    "05/2025": 81.73, "06/2025": 88.07, "07/2025": 82.91, "08/2025": 89.19,
    "09/2025": 92.77, "10/2025": 88.68, "11/2025": 82.47, "12/2025": 85.94,
    "01/2026": 94.45, "02/2026": 94.65, "03/2026": 94.63, "04/2026": 94.93,
    "05/2026": 94.31, "06/2026": 94.21, "07/2026": 94.36, "08/2026": 95.80,
    "09/2026": 95.36, "10/2026": 95.47, "11/2026": 95.56, "12/2026": 95.47
}
METAS_NET = {"01/2026": 90.00, "02/2026": 90.00, "03/2026": 90.00, "04/2026": 90.00, "05/2026": 90.00, "06/2026": 90.00, "07/2026": 90.00, "08/2026": 92.00, "09/2026": 92.00, "10/2026": 92.00, "11/2026": 92.00, "12/2026": 92.00}
METAS_CLARO_TV = {"01/2026": 85.02, "02/2026": 85.11, "03/2026": 85.19, "04/2026": 85.04, "05/2026": 84.80, "06/2026": 84.90, "07/2026": 85.19, "08/2026": 84.77, "09/2026": 84.97, "10/2026": 84.97, "11/2026": 85.05, "12/2026": 84.97}
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
        overflow: hidden;
    }
    .metric-label { font-size: 12px; color: #667781; margin-bottom: 4px; }
    .metric-value { font-size: 22px; font-weight: 700; margin-bottom: 6px; }
    .metric-meta { font-size: 12px; font-weight: 700; color: #667781; margin-bottom: 8px; }
    .metric-list {
        margin-top: 10px; padding-top: 8px; border-top: 1px solid #e6e6e6; text-align: left;
        width: 100%; overflow: hidden;
    }
    .metric-list-title {
        font-size: 11px; color: #667781; font-weight: 700; margin-bottom: 6px;
        text-transform: uppercase; letter-spacing: 0.02em;
    }
    .metric-line {
        display: flex; justify-content: space-between; gap: 8px; font-size: 12px;
        padding: 2px 0; line-height: 1.45;
    }
    .metric-name { font-weight: 600; color: #1f2937; }
    .metric-pct { font-weight: 700; }

    /* Notebook: puxa SLA/META um pouco para dentro do card */
    .empresa-head,
    .empresa-row {
        display: grid;
        grid-template-columns: minmax(96px, 1fr) 40px 40px;
        column-gap: 2px;
        align-items: center;
        font-size: 12px;
        line-height: 1.45;
        width: calc(100% - 18px);
        max-width: calc(100% - 18px);
        padding-right: 2px;
        box-sizing: border-box;
        overflow: hidden;
    }
    .empresa-head {
        padding-top: 2px;
        padding-bottom: 4px;
        margin-bottom: 4px;
    }
    .empresa-head .col-emp {
        text-align: left;
        font-weight: 600;
        color: #1f2937;
        white-space: nowrap;
    }
    .empresa-head .col-sla,
    .empresa-head .col-meta {
        width: 60px;
        text-align: right;
        justify-self: end;
        font-weight: 700;
        color: #1f2937;
        white-space: nowrap;
    }
    .empresa-row .col-emp {
        text-align: left;
        font-weight: 600;
        color: #1f2937;
        white-space: nowrap !important;
        word-break: keep-all !important;
        overflow-wrap: normal !important;
        writing-mode: horizontal-tb !important;
        overflow: hidden;
        text-overflow: ellipsis;
        min-width: 0;
    }
    .empresa-row .col-sla,
    .empresa-row .col-meta {
        width: 60px;
        text-align: right;
        justify-self: end;
        font-weight: 700;
        white-space: nowrap;
    }

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


    .vol-table-card {
        background: #f7f7f7; border: 1px solid #e3e3e3; border-radius: 12px; padding: 12px;
    }
    .vol-header, .vol-line {
        display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; align-items: center;
    }
    .vol-header {
        font-size: 11px; color: #667781; font-weight: 800; margin-bottom: 6px;
        text-transform: uppercase; letter-spacing: 0.02em; padding-bottom: 8px; border-bottom: 1px solid #e6e6e6;
    }
    .vol-line { font-size: 13px; padding: 7px 0; border-bottom: 1px solid rgba(0,0,0,0.05); }
    .vol-line:last-child { border-bottom: none; }
    .vol-mes { font-weight: 700; color: #1f2937; }
    .vol-realizado { font-weight: 800; color: #075E54; text-align: right; }
    .vol-projetado { font-weight: 900; color: #0b6d62; text-align: right; }
    .vol-muted { color: #9ca3af; font-weight: 700; text-align: right; }
    .vol-note { font-size: 11px; color: #667781; margin-top: 8px; }

    .notranslate { white-space: nowrap; }

    @media (max-width: 768px) {
        .main .block-container { max-width: 100% !important; padding-left: 0.7rem; padding-right: 0.7rem; }
        .topbar { padding: 12px 14px; }
        .topbar-title { font-size: 16px; }
        .card-title, .month-list-title { font-size: 16px; }
        .month-header-offensores, .month-header { font-size: 10px; gap: 6px; }
        .month-line { font-size: 12px; gap: 6px; }
        .month-cd, .month-pct-cd, .month-header .col-cd, .month-header .col-pct-cd { padding: 4px 6px; }
        .empresa-head, .empresa-row {
            grid-template-columns: minmax(88px, 1fr) 60px 60px;
            column-gap: 4px;
            width: 100%;
            max-width: 100%;
            padding-right: 0;
        }
        .empresa-head .col-sla, .empresa-head .col-meta,
        .empresa-row .col-sla, .empresa-row .col-meta { width: 60px; }
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
    s = (s.fillna(valor_padrao).astype(str).str.replace('\u00A0', '', regex=False).str.strip())
    return s.replace({'': valor_padrao, 'nan': valor_padrao, 'NaN': valor_padrao, 'None': valor_padrao, '<NA>': valor_padrao, 'undefined': valor_padrao})




def normalizar_chave_texto(valor: str) -> str:
    valor = '' if valor is None else str(valor)
    valor = unicodedata.normalize('NFKD', valor).encode('ASCII', 'ignore').decode('ASCII')
    valor = re.sub(r'[^A-Z0-9]+', ' ', valor.upper()).strip()
    return valor


def converter_data_excel(serie: pd.Series) -> pd.Series:
    """Converte datas do Excel/.xlsb, tratando serial numérico e texto dd/mm/aaaa."""
    s = serie.copy()
    if pd.api.types.is_numeric_dtype(s):
        return pd.to_datetime(s, unit='D', origin='1899-12-30', errors='coerce')
    s_num = pd.to_numeric(s, errors='coerce')
    out = pd.to_datetime(s, errors='coerce', dayfirst=True)
    mask_num = s_num.notna() & out.isna()
    if mask_num.any():
        out.loc[mask_num] = pd.to_datetime(s_num.loc[mask_num], unit='D', origin='1899-12-30', errors='coerce')
    return out


def score_aba_corte(df_sheet: pd.DataFrame) -> float:
    """Critério igual ao dashboard_bi: identifica a aba de mapa de corte pelas 3 primeiras colunas."""
    if df_sheet is None or df_sheet.empty or df_sheet.shape[1] < 3:
        return -1.0
    tmp = df_sheet.iloc[:, :3].copy()
    d1 = converter_data_excel(tmp.iloc[:, 1])
    d2 = converter_data_excel(tmp.iloc[:, 2])
    taxa_d1 = float(d1.notna().mean()) if len(d1) else 0.0
    taxa_d2 = float(d2.notna().mean()) if len(d2) else 0.0
    labels = tmp.iloc[:, 0].astype(str).str.strip()
    tem_mes_ano = float(labels.str.contains(r'\d{1,2}/\d{2,4}|[a-zA-ZçÇ]{3,}\s*[-/]?\s*\d{2,4}', regex=True, na=False).mean()) if len(labels) else 0.0
    return taxa_d1 + taxa_d2 + tem_mes_ano


def aplicar_mapa_corte(df_base: pd.DataFrame, df_cortes: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    """Aplica o mapa de corte do dashboard: Data NF dentro do intervalo início/fim."""
    if df_cortes is None or df_cortes.empty or df_cortes.shape[1] < 3:
        return df_base, False

    mapa_corte = df_cortes.iloc[:, :3].copy()
    mapa_corte.columns = ['Mes_Corte_Original', 'Data_Inicio_Corte', 'Data_Fim_Corte']
    mapa_corte['Data_Inicio_Corte'] = converter_data_excel(mapa_corte['Data_Inicio_Corte'])
    mapa_corte['Data_Fim_Corte'] = converter_data_excel(mapa_corte['Data_Fim_Corte'])
    mapa_corte = mapa_corte.dropna(subset=['Data_Inicio_Corte', 'Data_Fim_Corte']).copy()
    if mapa_corte.empty or 'Data NF' not in df_base.columns:
        return df_base, False

    # Regra do dashboard_bi: o mês de corte é definido pela data final do corte.
    mapa_corte['Mes_Corte_Fatura'] = mapa_corte['Data_Fim_Corte'].dt.strftime('%m/%Y')
    mapa_corte = (
        mapa_corte[['Mes_Corte_Fatura', 'Data_Inicio_Corte', 'Data_Fim_Corte']]
        .drop_duplicates()
        .sort_values(['Data_Fim_Corte', 'Data_Inicio_Corte'])
        .reset_index(drop=True)
    )

    intervalos = pd.IntervalIndex.from_arrays(
        mapa_corte['Data_Inicio_Corte'],
        mapa_corte['Data_Fim_Corte'],
        closed='both'
    )
    idx = intervalos.get_indexer(df_base['Data NF'])
    mask_idx = idx >= 0
    if mask_idx.any():
        df_base.loc[mask_idx, 'Mes_Corte_Fatura'] = mapa_corte['Mes_Corte_Fatura'].to_numpy()[idx[mask_idx]]
        df_base.loc[mask_idx, 'Data_Inicio_Corte_Mapa'] = mapa_corte['Data_Inicio_Corte'].to_numpy()[idx[mask_idx]]
        df_base.loc[mask_idx, 'Data_Fim_Corte_Mapa'] = mapa_corte['Data_Fim_Corte'].to_numpy()[idx[mask_idx]]

    mapa_ordem = {mes: pos + 1 for pos, mes in enumerate(mapa_corte['Mes_Corte_Fatura'].tolist())}
    df_base['Mes_Corte_Fatura_Ordem'] = df_base['Mes_Corte_Fatura'].map(mapa_ordem)
    return df_base, bool(mask_idx.any())


def carregar_mapa_corte_fatura(df_base: pd.DataFrame, path_base: str) -> pd.DataFrame:
    """Traz para o app.py do chatbot o mesmo critério de corte usado no dashboard_bi.py."""
    df_base['Mes_Corte_Fatura'] = pd.NA
    df_base['Mes_Corte_Fatura_Ordem'] = pd.NA
    df_base['Data_Inicio_Corte_Mapa'] = pd.NaT
    df_base['Data_Fim_Corte_Mapa'] = pd.NaT

    # 1) Tenta detectar a aba interna de cortes no próprio XLSB.
    try:
        with pd.ExcelFile(path_base, engine='pyxlsb') as xls2:
            sheet_names = [str(s).strip() for s in xls2.sheet_names]
            aba_principal = sheet_names[0] if sheet_names else ''
            for candidato in ['planilha1', 'sheet1', 'base', 'dados']:
                achou = next((s for s in sheet_names if str(s).strip().lower().replace(' ', '') == candidato), None)
                if achou:
                    aba_principal = achou
                    break

            melhor_df_corte = None
            melhor_score = -1.0
            for s in sheet_names:
                if s == aba_principal:
                    continue
                try:
                    df_sheet = pd.read_excel(xls2, sheet_name=s)
                    score = score_aba_corte(df_sheet)
                    if score > melhor_score:
                        melhor_score = score
                        melhor_df_corte = df_sheet.copy()
                except Exception:
                    continue

            if melhor_df_corte is not None and melhor_score > 0.80:
                df_base, ok = aplicar_mapa_corte(df_base, melhor_df_corte)
                if ok:
                    return df_base
    except Exception:
        pass

    # 2) Fallback: arquivos auxiliares iguais aos previstos no dashboard_bi.py.
    for nome_aux in [
        'datas_corte_fatura.xlsx', 'datas_corte_fatura.xlsb',
        'corte_fatura.xlsx', 'corte_fatura.xlsb',
        'planilha2.xlsx', 'planilha2.xlsb'
    ]:
        if not df_base['Mes_Corte_Fatura'].isna().all():
            break
        p_aux = Path(nome_aux)
        if not p_aux.exists():
            continue
        try:
            df_aux = pd.read_excel(p_aux, engine='pyxlsb') if p_aux.suffix.lower() == '.xlsb' else pd.read_excel(p_aux)
            df_aux.columns = [str(c).strip() for c in df_aux.columns]
            df_base, ok = aplicar_mapa_corte(df_base, df_aux)
            if ok:
                break
        except Exception:
            continue

    return df_base


def fmt_int(valor: float | int) -> str:
    return f"{int(round(float(valor))):,}".replace(',', '.')


def contar_volume_pedidos(df_base: pd.DataFrame) -> int:
    """Alinha ao dashboard_bi: conta Pedido quando a coluna existe; senão conta linhas."""
    if 'Pedido' in df_base.columns:
        return int(df_base['Pedido'].notna().sum())
    return int(len(df_base))


def construir_volumetria_data_nf(df: pd.DataFrame, empresa: str | None = 'Geral') -> dict:
    base = df[df['Data NF'].notna()].copy()
    if empresa and empresa != 'Geral' and 'Empresa' in base.columns:
        empresa_norm = normalizar_chave_texto(empresa)
        base = base[base['Empresa'].astype(str).map(normalizar_chave_texto) == empresa_norm].copy()
    if base.empty:
        return {'erro': 'Não há dados para a seleção realizada.'}

    base['Mes_Vol'] = base['Data NF'].dt.strftime('%m/%Y')
    meses = sorted(base['Mes_Vol'].dropna().unique(), key=lambda x: datetime.strptime(x, '%m/%Y'))[-6:]
    mes_atual = meses[-1] if meses else None
    data_max = base.loc[base['Mes_Vol'] == mes_atual, 'Data NF'].max() if mes_atual else pd.NaT

    linhas = []
    for mes in meses:
        base_mes = base[base['Mes_Vol'] == mes]
        realizado = contar_volume_pedidos(base_mes)
        projetado = None
        if mes == mes_atual and pd.notna(data_max):
            ultimo_dia_mes = calendar.monthrange(int(data_max.year), int(data_max.month))[1]
            dia_base = max(int(data_max.day), 1)
            projetado = realizado if dia_base >= ultimo_dia_mes else realizado / dia_base * ultimo_dia_mes
        linhas.append({'mes': mes_br(mes), 'realizado': realizado, 'projetado': projetado})

    return {'erro': None, 'linhas': linhas[::-1], 'data_max': data_max, 'empresa': empresa or 'Geral'}


def construir_volumetria_corte_fatura(df: pd.DataFrame, empresa: str | None = 'Geral') -> dict:
    if 'Mes_Corte_Fatura' not in df.columns or df['Mes_Corte_Fatura'].dropna().empty:
        return {'erro': 'Não encontrei dados de corte de fatura. Verifique se a aba/arquivo auxiliar de corte está junto ao XLSB.'}

    base = df[df['Mes_Corte_Fatura'].notna()].copy()
    if empresa and empresa != 'Geral' and 'Empresa' in base.columns:
        empresa_norm = normalizar_chave_texto(empresa)
        base = base[base['Empresa'].astype(str).map(normalizar_chave_texto) == empresa_norm].copy()
    if base.empty:
        return {'erro': 'Não há dados para a seleção realizada.'}

    ordem = base[['Mes_Corte_Fatura', 'Mes_Corte_Fatura_Ordem']].drop_duplicates().copy()
    ordem['ordem_aux'] = pd.to_numeric(ordem['Mes_Corte_Fatura_Ordem'], errors='coerce')
    if ordem['ordem_aux'].notna().any():
        meses = ordem.sort_values('ordem_aux')['Mes_Corte_Fatura'].tolist()[-6:]
    else:
        meses = sorted(base['Mes_Corte_Fatura'].dropna().unique(), key=lambda x: datetime.strptime(x, '%m/%Y'))[-6:]

    mes_atual = meses[-1] if meses else None
    linhas = []
    data_max_ref = pd.NaT
    for mes in meses:
        base_mes = base[base['Mes_Corte_Fatura'] == mes]
        realizado = contar_volume_pedidos(base_mes)
        projetado = None
        if mes == mes_atual:
            data_max = base_mes['Data NF'].max() if 'Data NF' in base_mes.columns else pd.NaT
            data_ini = base_mes['Data_Inicio_Corte_Mapa'].dropna().min() if 'Data_Inicio_Corte_Mapa' in base_mes.columns else pd.NaT
            data_fim = base_mes['Data_Fim_Corte_Mapa'].dropna().max() if 'Data_Fim_Corte_Mapa' in base_mes.columns else pd.NaT
            data_max_ref = data_max
            if pd.notna(data_max) and pd.notna(data_ini) and pd.notna(data_fim):
                total_dias_corte = max((data_fim - data_ini).days + 1, 1)
                dias_realizados = max((min(data_max, data_fim) - data_ini).days + 1, 1)
                projetado = realizado if data_max >= data_fim else realizado / dias_realizados * total_dias_corte
        linhas.append({'mes': mes_br(mes), 'realizado': realizado, 'projetado': projetado})

    return {'erro': None, 'linhas': linhas[::-1], 'data_max': data_max_ref, 'empresa': empresa or 'Geral'}


def render_volumetria_resultado(resultado: dict, titulo_data: str):
    linhas_html = ''.join([
        '<div class="vol-line">'
        f'<span class="vol-mes notranslate" translate="no">{linha["mes"]}</span>'
        f'<span class="vol-realizado notranslate" translate="no">{fmt_int(linha["realizado"])}</span>'
        f'<span class="{("vol-projetado" if linha["projetado"] is not None else "vol-muted")} notranslate" translate="no">{fmt_int(linha["projetado"]) if linha["projetado"] is not None else "-"}</span>'
        '</div>'
        for linha in resultado['linhas']
    ])
    data_max = resultado.get('data_max')
    nota = ''
    if pd.notna(data_max):
        nota = f"Projeção calculada com base no realizado até {data_max.strftime('%d/%m/%Y')} dentro do mês atual da base."

    html = (
        '<div class="month-list-box">'
        '<div class="month-list-title">Volumetria de Pedidos</div>'
        f'<div class="month-list-subtitle">Base: {titulo_data} | Visão: {resultado["empresa"]} | Últimos 6 meses.</div>'
        f'<div class="month-highlight notranslate" translate="no">{resultado["empresa"]}</div>'
        '<div class="vol-table-card">'
        '<div class="vol-header"><span>Mês</span><span style="text-align:right;">Realizado</span><span style="text-align:right;">Projetado</span></div>'
        f'{linhas_html}'
        '</div>'
        f'<div class="vol-note">{nota}</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_volumetria_pedidos(df: pd.DataFrame, tipo_data: str, empresa: str | None = 'Geral'):
    if tipo_data == 'nf':
        resultado = construir_volumetria_data_nf(df, empresa)
        titulo_data = 'Data da NF'
    else:
        resultado = construir_volumetria_corte_fatura(df, empresa)
        titulo_data = 'Data Corte da Fatura'

    if resultado.get('erro'):
        st.warning(resultado['erro'])
        return
    render_volumetria_resultado(resultado, titulo_data)

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

    df['Data NF'] = converter_data_excel(df['Data NF'])
    df = df[df['Data NF'].notna()].copy()
    df['Mes_Ano'] = df['Data NF'].dt.strftime('%m/%Y')
    df = carregar_mapa_corte_fatura(df, path)
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
        meta_mes = meta_empresa_mes(mes)
        mes_label = mes_br(mes)
        linhas.append((mes_label, fmt_pct(metrica['D+1']), pior_cd, pior_cd_pct, meta_mes))
    return linhas


def construir_visao_grupo(df: pd.DataFrame, coluna: str) -> dict:
    meses = sorted(df['Mes_Ano'].dropna().unique(), key=lambda x: datetime.strptime(x, '%m/%Y'))
    mes_atual = meses[-1] if meses else None
    base = df[df['Mes_Ano'] == mes_atual].copy() if mes_atual else df.head(0).copy()
    metrica_base = calc_metrica(base)
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
        resultado[chave] = {
            'geral': fmt_pct(metrica_base[chave]),
            'itens': itens,
            'meta_atual': meta_atual,
            'mes_atual': mes_atual
        }
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
        if coluna == 'Empresa' and label == 'D+1':
            linhas_html = (
                '<div class="empresa-head">'
                '<span class="col-emp"></span>'
                '<span class="col-sla">SLA</span>'
                '<span class="col-meta">Meta</span>'
                '</div>'
            )
            for nome, pct, meta_item in value_dict['itens']:
                meta_ref = meta_item if meta_item is not None else meta_atual
                meta_txt = fmt_pct(meta_ref)
                cor = cor_percentual_card(label, pct, meta_ref)
                linhas_html += (
                    '<div class="empresa-row">'
                    f'<span class="col-emp">{nome}</span>'
                    f'<span class="col-sla" style="color:{cor};font-weight:700;">{pct}</span>'
                    f'<span class="col-meta" style="font-weight:700;">{meta_txt}</span>'
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
if 'sf_vol_tipo_data' not in st.session_state:
    st.session_state.sf_vol_tipo_data = None
if 'sf_vol_empresa' not in st.session_state:
    st.session_state.sf_vol_empresa = 'Geral'

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
        st.session_state.sf_vol_tipo_data = None
        st.session_state.sf_vol_empresa = 'Geral'
        st.session_state.step = 2
        st.rerun()
    if c2.button('Pedidos para LPs', use_container_width=True):
        st.warning('No momento o fluxo de Pedidos para LPs está em construção.')
    if c3.button('Resultado do DRE', use_container_width=True):
        st.warning('No momento o fluxo de Resultado do DRE está em construção.')
    if c4.button('Valores dos EAs', use_container_width=True):
        st.warning('No momento o fluxo de Valores dos EAs está em construção.')

elif st.session_state.step == 2 and st.session_state.indicador == 'sf':
    st.markdown('<div class="menu-info"><strong>Opções disponíveis:</strong><br>Visão Geral | Visão por CDs | Visão por Empresas | Volumetria de Pedidos</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    if c1.button('Visão Geral', use_container_width=True):
        st.session_state.sf_visao = 'geral'
        st.session_state.sf_vol_tipo_data = None
        st.rerun()
    if c2.button('Visão por CDs', use_container_width=True):
        st.session_state.sf_visao = 'cds'
        st.session_state.sf_vol_tipo_data = None
        st.rerun()
    if c3.button('Visão por Empresas', use_container_width=True):
        st.session_state.sf_visao = 'empresas'
        st.session_state.sf_vol_tipo_data = None
        st.rerun()
    if c4.button('Volumetria de Pedidos', use_container_width=True):
        st.session_state.sf_visao = 'volumetria'
        st.session_state.sf_vol_tipo_data = None
        st.session_state.sf_vol_empresa = 'Geral'
        st.rerun()

    if base_real is not None:
        if st.session_state.sf_visao == 'geral':
            render_visao_geral_meses(construir_visao_geral(base_real))
        elif st.session_state.sf_visao == 'cds':
            render_card_titulo('Separação e Faturamento | Visão por CDs | SLA do mês atual', 'Dados reais da base Faturamento SLA 2026.xlsb.')
            render_metricas_sla(construir_visao_grupo(base_real, 'CD Origem'), 'CDs', 'CD Origem')
        elif st.session_state.sf_visao == 'empresas':
            render_card_titulo('Separação e Faturamento | Visão por Empresas | SLA do mês atual', 'Dados reais da base Faturamento SLA 2026.xlsb.')
            render_metricas_sla(construir_visao_grupo(base_real, 'Empresa'), 'Empresas', 'Empresa')
        elif st.session_state.sf_visao == 'volumetria':
            render_card_titulo('Volumetria de Pedidos', 'Selecione a referência da data e, se necessário, filtre por empresa.')
            dt1, dt2 = st.columns(2)
            if dt1.button('Data da NF', use_container_width=True):
                st.session_state.sf_vol_tipo_data = 'nf'
                st.session_state.sf_vol_empresa = 'Geral'
                st.rerun()
            if dt2.button('Data Corte da Fatura', use_container_width=True):
                st.session_state.sf_vol_tipo_data = 'corte'
                st.session_state.sf_vol_empresa = 'Geral'
                st.rerun()

            if st.session_state.sf_vol_tipo_data:
                st.markdown('<div class="menu-info"><strong>Empresa:</strong><br>Geral | Claro Fixo | Claro Móvel | Claro TV | Embratel | NET</div>', unsafe_allow_html=True)
                empresas = ['Geral', 'Claro Fixo', 'Claro Móvel', 'Claro TV', 'Embratel', 'NET']
                cols_emp = st.columns(3)
                for idx, empresa in enumerate(empresas):
                    with cols_emp[idx % 3]:
                        if st.button(empresa, key=f'btn_vol_empresa_{empresa}', use_container_width=True):
                            st.session_state.sf_vol_empresa = empresa
                            st.rerun()
                render_volumetria_pedidos(base_real, st.session_state.sf_vol_tipo_data, st.session_state.sf_vol_empresa)
            else:
                st.info('Clique em Data da NF ou Data Corte da Fatura para abrir a volumetria dos últimos 6 meses.')
    else:
        st.error('Não foi possível carregar a base real. Verifique se o arquivo .xlsb está na raiz do repositório e se o requirements contém pyxlsb.')

    c1, c2 = st.columns(2)
    if c1.button('Voltar aos indicadores', use_container_width=True):
        st.session_state.step = 1
        st.session_state.indicador = None
        st.session_state.sf_visao = None
        st.session_state.sf_vol_tipo_data = None
        st.session_state.sf_vol_empresa = 'Geral'
        st.rerun()
    if c2.button('Reiniciar conversa', use_container_width=True):
        st.session_state.step = 0
        st.session_state.nome = ''
        st.session_state.indicador = None
        st.session_state.sf_visao = None
        st.session_state.sf_vol_tipo_data = None
        st.session_state.sf_vol_empresa = 'Geral'
        st.rerun()
