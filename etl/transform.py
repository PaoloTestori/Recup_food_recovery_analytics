from src.food_parser import food_string_parser

def transform_food_data(tabellaMercati, tabellaReport):

    pattern = r"([A-Za-zÀ-ÿ\s]+?)\s+([0-9]+(?:[.,][0-9]+)?)"
    patternInverso = r"^(?:\s*\d+(?:[.,]\d+)?\s+[A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+)*)(?:\s*,\s*\d+(?:[.,]\d+)?\s+[A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+)*)*$"
    misto = r"/misto [a-zA-Z]{3,}/g"

    # Stampa la tabella
    listaMercati = [""]
    idx = 0
    for i, e in enumerate(tabellaMercati):
        listaMercati.append(tabellaMercati[i][1] + "_" + tabellaMercati[i][0])
    for row in tabellaReport:
        if str(row[3]).__eq__("NO") or str(row[3]).__eq__("No") or str(row[3]).__eq__("no") or str(row[3]).__eq__("SI È FATTO IL RECUPERO?"):
            continue
        tabellaMercati = food_string_parser(row, listaMercati, misto, pattern, patternInverso, tabellaMercati)


    for genereCibo in tabellaMercati[2:]:
        genereCibo[3] = float(str(genereCibo[3]).replace(",", "."))

    return tabellaMercati