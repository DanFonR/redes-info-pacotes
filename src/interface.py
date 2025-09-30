import streamlit as st
import pandas as pd
import altair as alt
import os
from streamlit_autorefresh import st_autorefresh
from ip import get_local_ip

st.set_page_config(page_title="Relatório de Pacotes", layout="wide")

st.title("Relatório de captura de pacotes")
st.subheader("Resumo por IP")

# Atualização automática a cada 5 segundos (sem piscar a tela inteira)
st_autorefresh(interval=5000, key="refresh")

# Mostra a URL
try:
    ip_local = get_local_ip()
    url = f"http://{ip_local}:8000"
    st.markdown(f"📡 **Acesse a API/serviço no:** [{url}]({url})")
except Exception as e:
    st.error(f"Não foi possível obter o IP local: {e}")


@st.cache_data(ttl=5)
def carregar_dados():
    """Carrega o CSV e devolve como DataFrame."""
    caminho_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "netlog.csv"))
    try:
        df = pd.read_csv(caminho_csv)
    except Exception:
        return pd.DataFrame()
    return df


# Estado para guardar IP selecionado
if "ip_escolhido" not in st.session_state:
    st.session_state.ip_escolhido = "(Todos)"

df = carregar_dados()

if df.empty:
    st.warning("Arquivo CSV está vazio. Nenhum dado para exibir.")
else:
    # Garantir tipos numéricos
    df["bytes_enviados"] = pd.to_numeric(df["bytes_enviados"], errors="coerce").fillna(0)
    df["bytes_recebidos"] = pd.to_numeric(df["bytes_recebidos"], errors="coerce").fillna(0)

    # Resumo geral por IP
    resumo_ip = df.groupby("ip").agg({
        "bytes_enviados": "sum",
        "bytes_recebidos": "sum"
    }).reset_index()
    resumo_ip.columns = ["IP", "Total Bytes Enviados", "Total Bytes Recebidos"]

    # --- seletor de IP (com chave única e persistência) ---
    ip_escolhido = st.selectbox(
        "🔍 Escolha um IP (ou deixe vazio para ver todos):",
        ["(Todos)"] + resumo_ip["IP"].unique().tolist(),
        index=(["(Todos)"] + resumo_ip["IP"].unique().tolist()).index(st.session_state.ip_escolhido),
        key="select_ip"
    )
    st.session_state.ip_escolhido = ip_escolhido

    # --- Se nenhum IP foi escolhido → gráfico por IP ---
    if ip_escolhido == "(Todos)":
        st.dataframe(resumo_ip, use_container_width=True)

        dados_chart = resumo_ip.melt(
            id_vars="IP",
            value_vars=["Total Bytes Recebidos", "Total Bytes Enviados"],
            var_name="Tipo",
            value_name="Bytes"
        )
        grafico = alt.Chart(dados_chart).mark_bar().encode(
            x="IP:N",
            y="Bytes:Q",
            color=alt.Color("Tipo:N", title="Tipo",
                            scale=alt.Scale(
                                domain=["Total Bytes Recebidos", "Total Bytes Enviados"],
                                range=["skyblue", "dodgerblue"]
                            )),
            tooltip=["IP", "Tipo", "Bytes"]
        ).properties(
            height=400,
            title="Total de Bytes Enviados e Recebidos por IP"
        )
        st.altair_chart(grafico, use_container_width=True)

    # --- Se um IP foi escolhido → gráfico por protocolo ---
    else:
        df_ip = df[df["ip"] == ip_escolhido]
        resumo_proto = df_ip.groupby("protocolo").agg({
            "bytes_enviados": "sum",
            "bytes_recebidos": "sum"
        }).reset_index()
        resumo_proto.columns = ["Protocolo", "Total Bytes Enviados", "Total Bytes Recebidos"]

        st.dataframe(resumo_proto, use_container_width=True)

        dados_chart = resumo_proto.melt(
            id_vars="Protocolo",
            value_vars=["Total Bytes Recebidos", "Total Bytes Enviados"],
            var_name="Tipo",
            value_name="Bytes"
        )
        grafico = alt.Chart(dados_chart).mark_bar().encode(
            x="Protocolo:N",
            y="Bytes:Q",
            color=alt.Color("Tipo:N", title="Tipo",
                            scale=alt.Scale(
                                domain=["Total Bytes Recebidos", "Total Bytes Enviados"],
                                range=["skyblue", "dodgerblue"]
                            )),
            tooltip=["Protocolo", "Tipo", "Bytes"]
        ).properties(
            height=400,
            title=f"Total de Bytes Enviados e Recebidos por Protocolo ({ip_escolhido})"
        )
        st.altair_chart(grafico, use_container_width=True)
