import streamlit as st
import pandas as pd
import time
from streamlit_js_eval import streamlit_js_eval
from google.oauth2 import service_account
from gsheetsdb import connect


# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)
conn = connect(credentials=credentials)


# Perform SQL query on the Google Sheet.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def run_query(query):
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    return rows

sheet_url = st.secrets["private_gsheets_url"]
rows = run_query(f'SELECT * FROM "{sheet_url}"')

# Print results.
for row in rows:
    st.write(f"{row.name} has elo of :{row.pet}:")

# Read the CSV data
#ranking = pd.read_csv(csv_url)




if "player1" not in st.session_state:
    st.session_state["player1"] = False

if "player2" not in st.session_state:
    st.session_state["player2"] = False

if "newplayer" not in st.session_state:
    st.session_state["newplayer"] = False



st.title("Fremtind Bordtennis Ranking")

st.write("Her kan du se rankingen til Fremtind Bordtennis")

@st.cache_data(ttl=600)
def load_data(sheets_url):
    return pd.read_csv(sheets_url)

ranking = load_data(st.secrets["public_gsheets_url"])

#order rows by elo
#ranking = ranking.sort_values(by="Elo", ascending=False)

st.write(ranking)



if st.button("Er du ikke på ranking? Klikk her for å legge deg til"):
    st.session_state["newplayer"] = True

if st.session_state["newplayer"]:
    name_new_player = st.text_input("Skriv inn navnet ditt")
    if st.button("Legg til " + name_new_player):
        ranking.loc[len(ranking)] = [name_new_player, 0]
        
        ranking.to_csv("bordtennis.csv", index=False)
        streamlit_js_eval(js_expressions="parent.window.location.reload()")

    

st.write("Skriv inn navn på spillerne som har spilt mot hverandre, og trykk på knappen til den som vant")

name_p1 = st.text_input("Navn på spiller 1")
name_p2 = st.text_input("Navn på spiller 2")

if not name_p1 and name_p2:
    st.write("Skriv inn navn på begge spillerne")

if name_p1 and  name_p2:
#get elo from "Juan"
    st.write("du valgt " + name_p1 + " og " + name_p2)
    try:
        elo_p1 = ranking.loc[ranking["Player"] == name_p1, "Elo"].iloc[0]
        elo_p2 = ranking.loc[ranking["Player"] == name_p2, "Elo"].iloc[0]
    except:
        st.write("En av spillerne er ikke på rankingen")
        
        st.write("**Siden oppdateres om 3 sek**")
        time.sleep(3)
        streamlit_js_eval(js_expressions="parent.window.location.reload()")


    if elo_p1 >= elo_p2:
        elo_multiplier = elo_p1 / elo_p2
        if elo_multiplier > 1.5:
            elo_multiplier = 2
        else:
            elo_multiplier = elo_multiplier
    else:
        elo_multiplier = elo_p2 / elo_p1
        if elo_multiplier > 1.5:
            elo_multiplier = 2
        else:
            elo_multiplier = elo_multiplier


    st.write("Spiller 1 Elo: " + str(elo_p1))
    st.write("Spiller 2 Elo : " + str(elo_p2))

    elo_winner = 50 *1/elo_multiplier
    elo_loser = -50 *1/elo_multiplier

    if st.button(name_p1 + " vant"):
        st.session_state["player1"] = True

    if st.button(name_p2 + " vant"):
        st.session_state["player2"] = True


    if st.session_state["player1"]:
        st.write(name_p1 + " vant")
        ranking.loc[ranking["Player"] == name_p1, "Elo"] += elo_winner
        ranking.loc[ranking["Player"] == name_p2, "Elo"] += elo_loser
        ranking.to_csv("bordtennis.csv", index=False)
        st.write(ranking)
        
        st.write("Reload siden for å se oppdatert ranking, siden oppdateres automatisk om 5 sekunder")
        time.sleep(5)
        streamlit_js_eval(js_expressions="parent.window.location.reload()")
        st.session_state["player2"] = False
        


    if st.session_state["player2"]:
        st.write(name_p2 + " vant")
        ranking.loc[ranking["Player"] == name_p2, "Elo"] += elo_winner
        ranking.loc[ranking["Player"] == name_p1, "Elo"] += elo_loser
        ranking.to_csv("bordtennis.csv", index=False)
        st.write(ranking)
        
        st.write("Reload siden for å se oppdatert ranking, siden oppdateres automatisk om 5 sekunder")
        time.sleep(5)
        streamlit_js_eval(js_expressions="parent.window.location.reload()")
        st.session_state["player2"] = False

