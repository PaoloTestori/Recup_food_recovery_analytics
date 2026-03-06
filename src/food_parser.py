from src.is_convertible_to_date import is_convertible_to_date
from datetime import datetime
import re

def food_string_parser(row, listaMercati, patternInverso, misto, pattern, tabellaMercati):
    dataCibo = row[2]
    dataCibo = dataCibo[:10]
    dizionarioCibo = {}
    mercatoCorrente = row[1]
    if is_convertible_to_date(dataCibo):
        dt = datetime.strptime(dataCibo, "%d/%m/%Y")
        if ((str.upper(mercatoCorrente) + "_" + dataCibo) not in listaMercati):
            print("---" + str.upper(mercatoCorrente) + "_" + dataCibo + "---")
            ciboRecuperato = row[7].replace(":", "").replace("kg", "").replace(";", "").replace("-", "").replace("*", "")
            for match in (re.findall(patternInverso, ciboRecuperato)):
                ciboChiave = (match.strip().replace("  ", " ").replace("   ", " ").split(" ")[1]).strip()
                if re.match(misto, ciboChiave):
                    ciboChiave = ciboChiave.replace("misto", "").strip()
                if ciboChiave not in dizionarioCibo.keys():
                    dizionarioCibo.update({ciboChiave: float((match.strip().split(" ")[0]).strip().replace(",", "."))})
                else:
                    dizionarioCibo.update({ciboChiave: (
                            float(str(dizionarioCibo[ciboChiave]).replace(",", ".")) + float(
                        (match.strip().split(" ")[0]).strip().replace(",", ".")))})
            matches = re.findall(pattern, ciboRecuperato)
            for match in matches:
                ciboChiave = str(match[0]).strip()
                if re.match(misto, ciboChiave):
                    ciboChiave = ciboChiave.replace("misto", "").strip()
                if ciboChiave not in dizionarioCibo.keys():
                    dizionarioCibo.update({ciboChiave: float(str(match[1]).replace(",", "."))})
                else:
                    dizionarioCibo.update({ciboChiave: (float(str(dizionarioCibo[ciboChiave]).replace(",", ".")) + float(
                        str(match[1]).replace(",", ".")))})
            ciboChiave = ()
            for ciboChiave, ciboValue in dizionarioCibo.items():
                print(str(ciboValue) + ": " + str(ciboChiave))
                tabellaMercati.insert(len(tabellaMercati) + 1,
                                      [dataCibo, mercatoCorrente.upper(), str(ciboChiave).upper(), float(str(ciboValue))])

    return tabellaMercati
