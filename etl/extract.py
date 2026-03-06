
def extract_google_sheet(client, sheet_name):

    # Apri il Google Sheet (per nome o per ID)
    sheet = client.open(sheet_name).sheet1   # prima tabella

    # Leggi tutti i dati
    tabella = sheet.get_all_values()

    return tabella, sheet

