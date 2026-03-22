def filtra_df(df, filtri):
    df = df.copy()

    df = df[df["MESE"] == filtri["MESE"]]

    return df