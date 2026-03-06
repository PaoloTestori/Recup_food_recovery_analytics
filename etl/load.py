
def load_food_data(tabellaMercati, sheet):
    import csv

    with open("MercatiMilano.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(tabellaMercati)

    #scrivi sullo sheet condiviso
    sheet.update(tabellaMercati, "A1")