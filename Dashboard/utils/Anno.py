def filtra_df(df, filtri):
    df = df.copy()

    df = df[df["ANNO"] == filtri["ANNO"]]

    return df