import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import time
from streamlit_js_eval import streamlit_js_eval

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
]

skey = st.secrets["gcp_service_account"]
credentials = Credentials.from_service_account_info(
    skey,
    scopes=scopes,
)
client = gspread.authorize(credentials)


if "player1" not in st.session_state:
    st.session_state["player1"] = False

if "player2" not in st.session_state:
    st.session_state["player2"] = False

if "newplayer" not in st.session_state:
    st.session_state["newplayer"] = False



# Perform SQL query on the Google Sheet.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=4)
def load_data(url, sheet_name="Sheet1"):
    sh = client.open_by_url(url)
    df = pd.DataFrame(sh.worksheet(sheet_name).get_all_records())
    return df

def update_data(df, url, sheet_name="Sheet1"):
    sh = client.open_by_url(url)
    worksheet = sh.worksheet(sheet_name)
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

ranking = load_data(st.secrets["private_gsheets_url"])


st.title("Fremtind Bordtennis Ranking")

st.write("Her kan du se rankingen til Fremtind Bordtennis")

#Order by elo
ranking = ranking.sort_values(by=['Elo'], ascending=False)

st.write(ranking)

if st.button("Er du ikke på ranking? Klikk her for å legge deg til"):
    st.session_state["newplayer"] = True

if st.session_state["newplayer"]:
    name_new_player = st.text_input("Skriv inn navnet ditt")
    if st.button("Legg til " + name_new_player):
        ranking.loc[len(ranking)] = [name_new_player, 1, 0 ,0, 0]
        
        update_data(ranking, st.secrets["private_gsheets_url"])
        st.write("**Siden oppdateres om 4 sek**")
        time.sleep(4)
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

    higher_elo_p1 = False
    higher_elo_p2 = False

    if elo_p1 >= elo_p2:
        higher_elo_p1 = True
        elo_multiplier = elo_p1 / elo_p2
        
        if elo_multiplier > 1.5:
            elo_multiplier = 2
        else:
            elo_multiplier = elo_multiplier
    else:
        higher_elo_p2 = True
        elo_multiplier = elo_p2 / elo_p1
        if elo_multiplier > 1.5:
            elo_multiplier = 2
        else:
            elo_multiplier = elo_multiplier


    st.write("Spiller 1 Elo: " + str(elo_p1))
    st.write("Spiller 2 Elo : " + str(elo_p2))

    elo_winner = 50 *1/elo_multiplier
    elo_loser = -30 *1/elo_multiplier

    if st.button(name_p1 + " vant"):
        st.session_state["player1"] = True

    if st.button(name_p2 + " vant"):
        st.session_state["player2"] = True


    if st.session_state["player1"]:
        st.write(name_p1 + " vant")
        ranking.loc[ranking["Player"] == name_p1, "Wins"] += 1
        ranking.loc[ranking["Player"] == name_p2, "Losses"] += 1
        if higher_elo_p1==True:
            ranking.loc[ranking["Player"] == name_p1, "Elo"] += 50*1/elo_multiplier
            elo_loser = elo_p2 -30*1/elo_multiplier
            
            if elo_loser < 1:
                ranking.loc[ranking["Player"] == name_p2, "Elo"] = 1
            else:
                ranking.loc[ranking["Player"] == name_p2, "Elo"] = elo_loser
        else:
            ranking.loc[ranking["Player"] == name_p1, "Elo"] += 50*elo_multiplier
            elo_loser = elo_p2 -30*elo_multiplier
            
            if elo_loser < 1:
                ranking.loc[ranking["Player"] == name_p2, "Elo"] = 1
            else:
                ranking.loc[ranking["Player"] == name_p2, "Elo"] = elo_loser
        update_data(ranking, st.secrets["private_gsheets_url"])
        st.write(ranking)
        
        st.write("Reload siden for å se oppdatert ranking, siden oppdateres automatisk om 5 sekunder")
        time.sleep(5)
        streamlit_js_eval(js_expressions="parent.window.location.reload()")
        st.session_state["player2"] = False
        


    if st.session_state["player2"]:
        st.write(name_p2 + " vant")
        ranking.loc[ranking["Player"] == name_p2, "Wins"] += 1
        ranking.loc[ranking["Player"] == name_p1, "Losses"] += 1
        if higher_elo_p2==True:
            ranking.loc[ranking["Player"] == name_p2, "Elo"] += 50*1/elo_multiplier
            elo_loser = elo_p1 -30*1/elo_multiplier
            
            if elo_loser < 1:
                ranking.loc[ranking["Player"] == name_p1, "Elo"] = 1
            else:
                ranking.loc[ranking["Player"] == name_p1, "Elo"] = elo_loser
        else:
            ranking.loc[ranking["Player"] == name_p2, "Elo"] += 50*elo_multiplier
            elo_loser = elo_p1 -30*elo_multiplier
            
            if elo_loser < 1:
                ranking.loc[ranking["Player"] == name_p1, "Elo"] = 1
            else:
                ranking.loc[ranking["Player"] == name_p1, "Elo"] = elo_loser
        update_data(ranking, st.secrets["private_gsheets_url"])
        st.write(ranking)
        
        st.write("Reload siden for å se oppdatert ranking, siden oppdateres automatisk om 5 sekunder")
        time.sleep(5)
        streamlit_js_eval(js_expressions="parent.window.location.reload()")
        st.session_state["player2"] = False