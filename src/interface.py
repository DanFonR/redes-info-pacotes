"""
Interface web para visualização de estatísticas de pacotes de rede.

Funcionalidades:
- Atualização automática a cada 5 segundos.
- Seleção de IP para filtrar dados.
- Exibição de tabelas e gráficos (Altair) de bytes enviados/recebidos.
- Baseado no CSV gerado pelo NetLogger.
"""

import os

import altair as alt
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from ip import get_local_ip

st.set_page_config(page_title="Relatório de Pacotes", layout="wide")

st.title("Relatório de captura de pacotes")

# Atualização automática a cada 5 segundos
st_autorefresh(interval=5000, key="refresh")

# Mostra a URL
try:
    ip_local: str = get_local_ip()
    url:str = f"http://{ip_local}:8000"
    st.markdown(f"##### 📡 **Acesse a API/serviço no:** [{url}]({url})")
except Exception as e:
    st.error(f"Não foi possível obter o IP local: {e}")


@st.cache_data(ttl=5)
def carregar_dados() -> pd.DataFrame:
    """Carrega o CSV de pacotes e retorna como DataFrame."""
    caminho_csv: str = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "netlog.csv")
    )
    try:
        df: pd.DataFrame = pd.read_csv(caminho_csv)
    except Exception:
        return pd.DataFrame()
    return df


# Estado para guardar IP selecionado
if "ip_escolhido" not in st.session_state:
    st.session_state.ip_escolhido = "(Todos)"

df: pd.DataFrame = carregar_dados()

if df.empty:
    st.warning("Arquivo CSV está vazio. Nenhum dado para exibir.")
else:
    df["bytes_enviados"] = pd.to_numeric(df["bytes_enviados"], errors="coerce").fillna(
        0
    )
    df["bytes_recebidos"] = pd.to_numeric(
        df["bytes_recebidos"], errors="coerce"
    ).fillna(0)

    resumo_ip: pd.DataFrame = (
        df.groupby("ip")
        .agg({"bytes_enviados": "sum", "bytes_recebidos": "sum"})
        .reset_index()
    )
    resumo_ip.columns = ["IP", "Total Bytes Enviados", "Total Bytes Recebidos"]

    # Seletor de IP
    ip_escolhido: str = st.selectbox(
        "🔍 Escolha um IP (ou deixe vazio para ver todos):",
        ["(Todos)"] + resumo_ip["IP"].unique().tolist(),
        index=(["(Todos)"] + resumo_ip["IP"].unique().tolist()).index(
            st.session_state.ip_escolhido
        ),
        key="select_ip",
    )
    st.session_state.ip_escolhido = ip_escolhido

    # Gráfico por IP
    if ip_escolhido == "(Todos)":
        st.dataframe(resumo_ip)

        dados_chart: pd.DataFrame = resumo_ip.melt(
            id_vars="IP",
            value_vars=["Total Bytes Recebidos", "Total Bytes Enviados"],
            var_name="Tipo",
            value_name="Bytes",
        )
        grafico: alt.Chart = (
            alt.Chart(dados_chart)
            .mark_bar()
            .encode(
                x=alt.X(
                    "IP:N",
                    title="IP",
                    axis=alt.Axis(labelAngle=0),
                    scale=alt.Scale(paddingInner=0.1, paddingOuter=0.05),
                ),
                y="Bytes:Q",
                color=alt.Color(
                    "Tipo:N",
                    title="Tipo",
                    scale=alt.Scale(
                        domain=[
                            "Total Bytes Recebidos",
                            "Total Bytes Enviados",
                        ],
                        range=["skyblue", "dodgerblue"],
                    ),
                ),
                tooltip=["IP", "Tipo", "Bytes"],
            )
            .properties(height=400, title="Total de Bytes Enviados e Recebidos por IP")
        )
        st.altair_chart(grafico)

    # Gráfico por protocolo
    else:
        df_ip: pd.DataFrame = df[df["ip"] == ip_escolhido]
        resumo_proto: pd.DataFrame = (
            df_ip.groupby("protocolo")
            .agg({"bytes_enviados": "sum", "bytes_recebidos": "sum"})
            .reset_index()
        )
        resumo_proto.columns = [
            "Protocolo",
            "Total Bytes Enviados",
            "Total Bytes Recebidos",
        ]

        st.dataframe(resumo_proto)

        dados_chart: pd.DataFrame = resumo_proto.melt(
            id_vars="Protocolo",
            value_vars=["Total Bytes Recebidos", "Total Bytes Enviados"],
            var_name="Tipo",
            value_name="Bytes",
        )
        grafico: alt.Chart = (
            alt.Chart(dados_chart)
            .mark_bar()
            .encode(
                x=alt.X(
                    "Protocolo:N",
                    title="Protocolo",
                    axis=alt.Axis(labelAngle=0),
                    scale=alt.Scale(paddingInner=0.1, paddingOuter=0.05),
                ),
                y="Bytes:Q",
                color=alt.Color(
                    "Tipo:N",
                    title="Tipo",
                    scale=alt.Scale(
                        domain=[
                            "Total Bytes Recebidos",
                            "Total Bytes Enviados",
                        ],
                        range=["skyblue", "dodgerblue"],
                    ),
                ),
                tooltip=["Protocolo", "Tipo", "Bytes"],
            )
            .properties(
                height=400,
                title=f"Total de Bytes Enviados e Recebidos por Protocolo ({ip_escolhido})",
            )
        )
        st.altair_chart(grafico)
