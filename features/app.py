import requests
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

TOP_GAMES_URL = (
    "https://api.steampowered.com/ISteamChartsService/GetMostPlayedGames/v1/"
)

st.set_page_config(page_title="Steam Dashboard", layout="wide")
st.title("🎮 Steam Games Dashboard")
st.write("Top jogos mais jogados na Steam (dados públicos).")


@st.cache_data
def get_game_details(appid):
    """Busca nome, imagem e gênero do jogo a partir do AppID usando a API da Steam."""
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        if str(appid) in data and data[str(appid)]["success"]:
            game_data = data[str(appid)]["data"]
            name = game_data.get("name", str(appid))
            header_image = game_data.get("header_image", "")
            genres = (
                ", ".join([g["description"] for g in game_data.get("genres", [])])
                if "genres" in game_data
                else ""
            )
            return name, header_image, genres
    return str(appid), "", ""


with st.spinner("Carregando dados da Steam..."):
    response = requests.get(TOP_GAMES_URL)
    if response.status_code != 200:
        st.error("Erro ao obter dados da Steam API")
        st.stop()

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


df[["Nome", "Imagem", "Gênero"]] = df["AppID"].apply(
    lambda appid: pd.Series(get_game_details(appid))
)


ultima_atualizacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.caption(f"📅 Última atualização: {ultima_atualizacao}")


selected_games = st.multiselect(
    "Selecione os jogos que deseja visualizar:",
    options=df["Nome"].tolist(),
    default=df["Nome"].head(10).tolist(),
)

df_filtrado = df[df["Nome"].isin(selected_games)]


fig = px.bar(
    df_filtrado,
    x="Nome",
    y="Jogadores Ativos",
    text="Jogadores Ativos",
    title="Jogos Selecionados - Jogadores Ativos Agora",
    labels={"Nome": "Jogo", "Jogadores Ativos": "Jogadores Ativos"},
)
fig.update_traces(textposition="outside")

st.plotly_chart(fig, use_container_width=True)


st.write("📊 Catálogo de jogos selecionados:")


col_in_lines = 3
cols = st.columns(col_in_lines)

for idx, (_, row) in enumerate(df_filtrado.iterrows()):
    with cols[idx % col_in_lines]:
        st.image(row["Imagem"], use_container_width=True)
        st.markdown(f"**{row['Nome']}**")
        st.caption(row["Gênero"])
        st.write(f"👥 Jogadores Ativos: {row['Jogadores Ativos']:,}")
        st.markdown("---")
