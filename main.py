import streamlit as st
from google.oauth2 import service_account
from shillelagh.backends.apsw.db import connect

sheet_url = st.secrets["private_gsheets_url"]

def create_connection():
     
    credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], 
    scopes=["https://www.googleapis.com/auth/spreadsheets",],)
    connection = connect(":memory:", adapter_kwargs={
            "gsheetsapi" : { 
            "service_account_info" : {
                "type" : st.secrets["gcp_service_account"]["type"],
                "project_id" : st.secrets["gcp_service_account"]["project_id"],
                "private_key_id" : st.secrets["gcp_service_account"]["private_key_id"],
                "private_key" : st.secrets["gcp_service_account"]["private_key"],
                "client_email" : st.secrets["gcp_service_account"]["client_email"],
                "client_id" : st.secrets["gcp_service_account"]["client_id"],
                "auth_uri" : st.secrets["gcp_service_account"]["auth_uri"],
                "token_uri" : st.secrets["gcp_service_account"]["token_uri"],
                "auth_provider_x509_cert_url" : st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
                "client_x509_cert_url" : st.secrets["gcp_service_account"]["client_x509_cert_url"],
                }
            },
        })
    return connection.cursor()

#ff


def execute_query(query):
     cursor = create_connection()
     rows = cursor.execute(query)
     rows = rows.fetchall()
     return rows
     

rows = execute_query(f"SELECT * FROM '{sheet_url}'")
for row in rows:
    st.write(row)