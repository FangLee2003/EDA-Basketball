import pandas as pd
import streamlit as st
import altair as alt
import base64
import matplotlib.pyplot as plt
import seaborn as sb
import numpy as np

st.title("NBA Player Stats Explorer")

st.markdown(
"""
This app perform  simple webscrapping  of NBA player stats data!
* **Python libraries:** streamlit, base64, pandas, altair, seaborn, matplotlib*
* **Data source:** [Basketball-reference.com](https://www.basketball-reference.com/).
"""
)

st.sidebar.header("User Input Features")
selected_year = st.sidebar.selectbox("Year", list(reversed(range(1950, 2022))))

# Web scrapping of NBA player stats
@st.cache
def load_data(year):
    url = (
        "https://www.basketball-reference.com/leagues/NBA_"
        + str(year)
        + "_per_game.html"
    )
    html = pd.read_html(url, header=0)
    df = html[0]
    # df = data frame
    raw = df.drop(
        df[df.Age == "Age"].index
    )  # Drop repeating headers in data frame with df[filter]
    raw = raw.fillna(0)  # Fill number 0 in cells with value NaN
    player_stats = raw.drop(["Rk"], axis=1)
    return player_stats


player_stats = load_data(selected_year)

# Sidebar - Team selection
sorted_unique_team = sorted(player_stats.Tm.unique())
# Tm: Team
selected_team = st.sidebar.multiselect("Team", sorted_unique_team, None)

# Sidebar - Position selection
unique_pos = ("C", "PF", "SF", "PG", "SG")
selected_pos = st.sidebar.multiselect("Position", unique_pos, None)

# Filtering data
df_selected_team_pos = player_stats[
    (player_stats.Tm.isin(selected_team)) & (player_stats.Pos.isin(selected_pos))
]
# isin: is in? - selecting rows with having selected_team in player_stats.Tm column

st.header('Player Stats of Selected Teams')
st.write('Data dimension: ' + str(df_selected_team_pos.shape[0]) + ' rows and ' + str(df_selected_team_pos.shape[1]) + ' columns')
#shape() return number of elements in each dimension.
st.dataframe(df_selected_team_pos)

def download(df):
    csv = df.to_csv(index = False)
    b64 = base64.b64encode(csv.encode()).decode() 
    # String -> encoded string -> encoded byte -> byte
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV file</a>'
    return href

st.markdown(download(df_selected_team_pos), unsafe_allow_html=True)

#Heatmap
st.header('Intercorrelation Matrix Heatmap')

df_selected_team_pos.to_csv('output.csv',index=False)
df = pd.read_csv('output.csv')
""" Dataframe -> csv -> Dataframe: The original dataframe has all of its columns as object, you will need to cast to int/float accordingly. 
So the workaround, export then import as csv, actually casts the data to the correct datatype.
"""
corr = df.corr()
#Create a correlation matrix

mask = np.zeros_like(corr)
#Create a mask from an array of zeros and have the same shape as the correlation matrix

mask[np.triu_indices_from(mask)] = True
# We only want to hide the upper triangle of the heat map, so we only take the upper triangle of the mask

#https://viblo.asia/p/gioi-thieu-ve-matplotlib-mot-thu-vien-rat-huu-ich-cua-python-dung-de-ve-do-thi-yMnKMN6gZ7P
with sb.axes_style("white"): #Background of axe
    figure, axes = plt.subplots(figsize=(7, 5))
    axes = sb.heatmap(corr, mask=mask, vmax=1, square=True)
st.pyplot(figure)
