import streamlit as st
def filtra_df(df, filtri):
    df = df.copy()
    if not filtri["DATA"]:  # lista vuota → nessun filtro applicato
        return df
    df = df[df["DATA"].isin(filtri["DATA"])]
    return df