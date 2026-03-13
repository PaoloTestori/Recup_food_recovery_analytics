import pandas as pd

from src.food_parser import food_string_parser
from datetime import datetime
import re
from src.is_convertible_to_date import is_convertible_to_date

def transform_food_data(tabellaMercati, tabellaReport):
    pattern = r"([A-Za-zÀ-ÿ\s]+?)(?::\s*|\s*)([0-9]+(?:[.,][0-9]+)?(?:\+[0-9]+(?:[.,][0-9]+)?)*)"
    patternInverso = r"([0-9]+(?:[.,][0-9]+)?)\s+([A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+)*)(?=\s+[0-9]|$)"
    misto = r"/misto [a-zA-Z]{3,}/g"

    # Stampa la tabella
    listaMercati = [""]
    idx = 0
    for i, e in enumerate(tabellaMercati):
        listaMercati.append(tabellaMercati[i][1] + "_" + tabellaMercati[i][0])
    for row in tabellaReport:
        if str(row[3]).__eq__("NO") or str(row[3]).__eq__("No") or str(row[3]).__eq__("no") or str(row[3]).__eq__(
                "SI È FATTO IL RECUPERO?"):
            continue
        dataCibo = row[2]
        dataCibo = dataCibo[:10]
        numeroBeneficiari = row[6]
        numeroVolontari = row[10]
        dizionarioCibo = {}
        mercatoCorrente = row[1]
        if is_convertible_to_date(dataCibo):
            dt = datetime.strptime(dataCibo, "%d/%m/%Y")
            if ((str.upper(mercatoCorrente) + "_" + dataCibo) not in listaMercati):
                print("---" + str.upper(mercatoCorrente) + "_" + dataCibo + "---")
                ciboRecuperato = row[7].replace(":", "").replace("kg", "").replace(";", "").replace("-", "").replace(
                    "*", "")
                ciboRecuperato = ciboRecuperato.replace("più", "+").replace(" + ", "+")
                for match in (re.findall(patternInverso, ciboRecuperato)):
                    ciboChiave = (match[1].replace("  ", " ").replace("   ", " ").split(" "))[0]
                    if re.match(misto, ciboChiave):
                        ciboChiave = ciboChiave.replace("misto", "").strip()
                    if ciboChiave not in dizionarioCibo.keys():
                        dizionarioCibo.update(
                            {ciboChiave: float((match[0].strip().split(" ")[0]).strip().replace(",", "."))})
                    else:
                        dizionarioCibo.update({ciboChiave: (
                                float(str(dizionarioCibo[ciboChiave]).replace(",", ".")) + float(
                            (match[0].replace(",", "."))))})
                matches = re.findall(pattern, ciboRecuperato)
                for match in matches:
                    ciboChiave = str(match[0]).strip()
                    if re.match(misto, ciboChiave):
                        ciboChiave = ciboChiave.replace("misto", "").strip()
                    if ciboChiave not in dizionarioCibo.keys():
                        dizionarioCibo.update({ciboChiave: float(eval(str(match[1]).replace(",", ".")))})
                    else:
                        dizionarioCibo.update({ciboChiave: (
                                    float(str(dizionarioCibo[ciboChiave]).replace(",", ".")) + float(
                                str(match[1]).replace(",", ".")))})
                ciboChiave = ()
                for ciboChiave, ciboValue in dizionarioCibo.items():
                    print(str(ciboValue) + ": " + str(ciboChiave))
                    tabellaMercati.insert(len(tabellaMercati) + 1,
                                          [dataCibo, mercatoCorrente.upper(), str(ciboChiave).upper(),
                                           float(str(ciboValue)), numeroVolontari, numeroBeneficiari])

    for genereCibo in tabellaMercati[2:]:
        genereCibo[3] = float(str(genereCibo[3]).replace(",", "."))

    df = pd.DataFrame(tabellaMercati,
                      columns=['DATA', "MERCATO", "ITEM", "KG", "NUMERO VOLONTARI", "NUMERO BENEFICIARI"])
    df = df.iloc[2:].reset_index(drop=True)
    df['DATA'] = pd.to_datetime(df['DATA'], format='%d/%m/%Y', errors='coerce')
    df = df.sort_values(['DATA', 'MERCATO'])
    df['DATA'] = df['DATA'].dt.strftime('%d/%m/%Y')
    df = pd.concat([df.iloc[:0], pd.DataFrame([[""] * len(df.columns)], columns=df.columns), df.iloc[0:]],
                   ignore_index=True)

    return df