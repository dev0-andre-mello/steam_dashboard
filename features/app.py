import requests
import pandas as pd
import streamlit as st
import plotly.express as px

TOP_GAMES_URL = (
    "https://api.steampowered.com/ISteamChartsService/GetMostPlayedGames/v1/"
)

st.set_page_config(page_title="Steam Dashboard", layout="wide")
st.title("🎮 Steam Games Dashboard")
st.write("Top jogos mais jogados na Steam (dados públicos).")


@st.cache_data
def get_game_name(appid):
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        if str(appid) in data and data[str(appid)]["success"]:
            return data[str(appid)]["data"]["name"]
    return str(appid)


response = requests.get(TOP_GAMES_URL)
if response.status_code != 200:
    st.error("Erro ao obter dados da Steam API")
else:
    data = response.json()["response"]["ranks"]

    df = pd.DataFrame(data)

    df.rename(
        columns={
            "rank": "Ranking",
            "appid": "AppID",
            "peak_in_game": "Jogadores Ativos",
        },
        inplace=True,
    )

    top_n = st.slider("Quantidade de jogos", min_value=5,
                      max_value=25, value=10)
    df_top = df.head(top_n).copy()

    df_top["Nome"] = df_top["AppID"].apply(get_game_name)

    df_top["Nome"] = df_top["AppID"].apply(get_game_name)

    fig = px.bar(
        df_top,
        x="Nome",
        y="Jogadores Ativos",
        text="Jogadores Ativos",
        title=f"Top {top_n} Jogos Mais Jogados Agora",
        labels={"Nome": "Jogo", "Jogadores Ativos": "Jogadores Ativos"},
    )
    fig.update_traces(textposition="outside")

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df_top)
