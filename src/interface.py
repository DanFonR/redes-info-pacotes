import streamlit as st
import pandas as pd
import altair as alt
import os
from streamlit_autorefresh import st_autorefresh
from ip import get_local_ip

# Atualiza automaticamente a cada 5 segundos
st_autorefresh(interval=5000, key="auto_refresh")

st.title("Relatório de captura de pacotes")
st.subheader("Resumo por IP")

# Mostra a URL para o usuário
try:
    ip_local = get_local_ip()
    url = f"http://{ip_local}:8000"
    st.markdown(f"📡 **Acesse a API/serviço no:** [{url}]({url})")
except Exception as e:
    st.error(f"Não foi possível obter o IP local: {e}")

@st.cache_data(ttl=5)
def carregar_dados():
    caminho_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "netlog.csv"))
    try:
        df = pd.read_csv(caminho_csv)
    except Exception as e:
        st.error(f"Erro ao ler o arquivo CSV: {e}")
        return pd.DataFrame()

    return df

# Containers para tabela e gráfico
tabela_container = st.empty()
grafico_container = st.empty()

df = carregar_dados()

if df.empty:
    st.warning("Arquivo CSV está vazio. Nenhum dado para exibir.")
else:
    df["bytes_enviados"] = pd.to_numeric(df["bytes_enviados"], errors='coerce').fillna(0)
    df["bytes_recebidos"] = pd.to_numeric(df["bytes_recebidos"], errors='coerce').fillna(0)

    agrupado = df.groupby("ip").agg({
        "bytes_enviados": "sum",
        "bytes_recebidos": "sum"
    }).reset_index()

    agrupado.columns = ['IP', 'Total Bytes Enviados', 'Total Bytes Recebidos']

    if agrupado.empty:
        st.warning("Não há dados suficientes para agrupar por IP.")
    else:
        tabela_container.dataframe(agrupado)

        dados_chart = agrupado.melt(
            id_vars='IP',
            value_vars=['Total Bytes Recebidos', 'Total Bytes Enviados'],
            var_name='Tipo',
            value_name='Bytes'
        )

        dados_chart = dados_chart[dados_chart["Tipo"].isin(["Total Bytes Recebidos", "Total Bytes Enviados"])]

        dados_chart["Bytes"] = pd.to_numeric(dados_chart["Bytes"], errors='coerce').fillna(0)

        grafico = alt.Chart(dados_chart).mark_bar().encode(
            x=alt.X('IP:N', title='IP'),
            y=alt.Y('Bytes:Q', title='Bytes', stack='zero'),
            color=alt.Color('Tipo:N', title='Tipo', scale=alt.Scale(
                domain=['Total Bytes Recebidos', 'Total Bytes Enviados'],
                range=['skyblue', 'dodgerblue']
            )),
            tooltip=['IP', 'Tipo', 'Bytes']
        ).properties(
            width='container',
            height=400,
            title='Total de Bytes Enviados e Recebidos por IP'
        )

        grafico_container.altair_chart(grafico, use_container_width=True)
