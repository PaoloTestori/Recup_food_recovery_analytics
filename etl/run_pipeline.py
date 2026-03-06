import json
import os
import sys
import gspread
from google.oauth2 import service_account
from etl.extract import extract_google_sheet
from etl.transform import transform_food_data
from etl.load import load_food_data
import streamlit as st

def run():
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    def resource_path(relative_path):
        """Supporta PyInstaller"""
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    # path del json
    sa_path = resource_path(st.secrets["gcp_service_account"])

    if not os.path.isfile(sa_path):
        raise FileNotFoundError(f"File credenziali non trovato: {sa_path}")

    with open(sa_path, "r", encoding="utf-8") as f:
        info = json.load(f)

    creds = service_account.Credentials.from_service_account_info(
        info,
        scopes=SCOPES
    )

    client = gspread.authorize(creds)

    raw_df_report, sheet_report  = extract_google_sheet(client, "REPORT🍌 MERCATI MILANO (Risposte)")
    raw_df_mercati, sheet_mercati = extract_google_sheet(client, "Mercati Milano")

    cleaned_df = transform_food_data(raw_df_report, raw_df_mercati)

    load_food_data(cleaned_df, sheet_mercati)


if __name__ == "__main__":
    run()