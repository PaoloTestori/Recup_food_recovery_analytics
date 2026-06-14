import os
import json
from dotenv import load_dotenv
from supabase import create_client
from groq import Groq
from collections import defaultdict
import streamlit as st

#load_dotenv()
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

supabase = create_client(
    supabase_url=SUPABASE_URL,
    supabase_key=SUPABASE_KEY
)

client = Groq(api_key=GROQ_API_KEY)

# --- TOOLS ---

def get_summary():
    all_data = []
    offset = 0
    while True:
        batch = supabase.table("Donations").select("kgIn, kgOut, CO2, H2O").range(offset, offset + 999).execute()
        if not batch.data:
            break
        all_data.extend(batch.data)
        offset += 1000
    return {
        "kg_totali_raccolti": round(sum(r["kgIn"] for r in all_data if r["kgIn"])),
        "kg_totali_donati": round(sum(r["kgOut"] for r in all_data if r["kgOut"])),
        "co2_risparmiata_kg": round(sum(r["CO2"] for r in all_data if r["CO2"])),
        "h2o_risparmiata_litri": round(sum(r["H2O"] for r in all_data if r["H2O"])),
    }

def get_top_products(anno=None):
    all_data = []
    offset = 0
    while True:
        batch = supabase.table("Donations").select("kgOut, Items(name), WorkingDays(date)").range(offset, offset + 999).execute()
        if not batch.data:
            break
        all_data.extend(batch.data)
        offset += 1000
    totali = defaultdict(float)
    for r in all_data:
        if r.get("Items") and r.get("kgOut"):
            if anno and not r.get("WorkingDays", {}).get("date", "").startswith(str(anno)):
                continue
            totali[r["Items"]["name"]] += r["kgOut"]
    top10 = sorted(totali.items(), key=lambda x: x[1], reverse=True)[:10]
    return [{"prodotto": k, "kg_donati": round(v)} for k, v in top10]

def get_top_suppliers(anno=None):
    all_data = []
    offset = 0
    while True:
        batch = supabase.table("Donations").select("kgOut, Suppliers(name), WorkingDays(date)").range(offset, offset + 999).execute()
        if not batch.data:
            break
        all_data.extend(batch.data)
        offset += 1000
    totali = defaultdict(float)
    for r in all_data:
        if r.get("Suppliers") and r.get("kgOut"):
            fornitore = r["Suppliers"]["name"]
            if fornitore == "Sconosciuto":
                continue
            if anno and not r.get("WorkingDays", {}).get("date", "").startswith(str(anno)):
                continue
            totali[fornitore] += r["kgOut"]
    top10 = sorted(totali.items(), key=lambda x: x[1], reverse=True)[:10]
    return [{"fornitore": k, "kg_donati": round(v)} for k, v in top10]

def get_efficiency_by_supplier(anno=None, **kwargs):
    if anno is None or anno == "null":
        anno = None
    all_data = []
    offset = 0
    while True:
        batch = supabase.table("Donations").select("kgIn, kgOut, Suppliers(name), WorkingDays(date)").range(offset, offset + 999).execute()
        if not batch.data:
            break
        all_data.extend(batch.data)
        offset += 1000
    raccolti = defaultdict(float)
    donati = defaultdict(float)
    conteggio = defaultdict(int)
    for r in all_data:
        if r.get("Suppliers") and r.get("kgIn") and r.get("kgOut"):
            fornitore = r["Suppliers"]["name"]
            if fornitore == "Sconosciuto":
                continue
            if anno and not r.get("WorkingDays", {}).get("date", "").startswith(str(anno)):
                continue
            raccolti[fornitore] += r["kgIn"]
            donati[fornitore] += r["kgOut"]
            conteggio[fornitore] += 1
    efficienza = {
        f: round(donati[f] / raccolti[f] * 100, 1)
        for f in raccolti
        if raccolti[f] > 0
        and conteggio[f] >= 10       # almeno 10 lotti
        and donati[f] <= raccolti[f] # esclude efficienza > 100%
    }
    top10 = sorted(efficienza.items(), key=lambda x: x[1], reverse=True)[:10]
    return [{"fornitore": k, "efficienza_pct": v, "num_lotti": conteggio[k]} for k, v in top10]

def get_monthly_trend(anno=None):
    all_data = []
    offset = 0
    while True:
        batch = supabase.table("Donations").select("kgOut, WorkingDays(date)").range(offset, offset + 999).execute()
        if not batch.data:
            break
        all_data.extend(batch.data)
        offset += 1000
    totali = defaultdict(float)
    for r in all_data:
        if r.get("WorkingDays") and r.get("kgOut"):
            data = r["WorkingDays"]["date"]
            if anno and not data.startswith(str(anno)):
                continue
            mese = data[:7]  # "2025-03"
            totali[mese] += r["kgOut"]
    return [{"mese": k, "kg_donati": round(v)} for k, v in sorted(totali.items())]

def get_waste_by_product(anno=None, min_lotti=10):
    all_data = []
    offset = 0
    while True:
        batch = supabase.table("Donations").select("kgIn, kgOut, Items(name), WorkingDays(date)").range(offset, offset + 999).execute()
        if not batch.data:
            break
        all_data.extend(batch.data)
        offset += 1000
    raccolti = defaultdict(float)
    donati = defaultdict(float)
    conteggio = defaultdict(int)
    for r in all_data:
        if r.get("Items") and r.get("kgIn") and r.get("kgOut"):
            prodotto = r["Items"]["name"]
            if anno and not r.get("WorkingDays", {}).get("date", "").startswith(str(anno)):
                continue
            raccolti[prodotto] += r["kgIn"]
            donati[prodotto] += r["kgOut"]
            conteggio[prodotto] += 1
    scarti = {
        p: round(100 - donati[p] / raccolti[p] * 100, 1)
        for p in raccolti if raccolti[p] > 0 and conteggio[p] >= min_lotti
    }
    top10 = sorted(scarti.items(), key=lambda x: x[1], reverse=True)[:10]
    return [{"prodotto": k, "scarto_pct": v, "num_lotti": conteggio[k]} for k, v in top10]

def get_env_impact_by_year():
    all_data = []
    offset = 0
    while True:
        batch = supabase.table("Donations").select("CO2, H2O, WorkingDays(date)").range(offset, offset + 999).execute()
        if not batch.data:
            break
        all_data.extend(batch.data)
        offset += 1000
    co2 = defaultdict(float)
    h2o = defaultdict(float)
    for r in all_data:
        if r.get("WorkingDays") and r.get("CO2"):
            anno = r["WorkingDays"]["date"][:4]
            co2[anno] += r["CO2"]
            h2o[anno] += r.get("H2O") or 0
    return [{"anno": k, "co2_kg": round(co2[k]), "h2o_litri": round(h2o[k])} for k in sorted(co2.keys())]

def get_fruiter_stats():
    all_data = []
    offset = 0
    while True:
        batch = supabase.table("DonationOut").select("kgTotaliDonati, Fruiter(name, label)").range(offset, offset + 999).execute()
        if not batch.data:
            break
        all_data.extend(batch.data)
        offset += 1000
    totali = defaultdict(float)
    for r in all_data:
        if r.get("Fruiter") and r.get("kgTotaliDonati"):
            nome = r["Fruiter"].get("name") or r["Fruiter"].get("label") or "Sconosciuto"
            totali[nome] += r["kgTotaliDonati"]
    top10 = sorted(totali.items(), key=lambda x: x[1], reverse=True)[:10]
    return [{"fruitore": k, "kg_ricevuti": round(v)} for k, v in top10]

def get_working_days_stats():
    data = supabase.table("WorkingDays").select("date").execute()
    from collections import Counter
    anni = Counter(r["date"][:4] for r in data.data if r.get("date"))
    totale = sum(anni.values())
    return {
        "giornate_per_anno": dict(sorted(anni.items())),
        "totale_giornate": totale,
        "media_annuale": round(totale / len(anni)) if anni else 0
    }

def get_supplier_by_product(prodotto: str, anno=None, **kwargs):
    all_data = []
    offset = 0
    while True:
        batch = supabase.table("Donations").select(
            "kgOut, Items(name), Suppliers(name), WorkingDays(date)"
        ).range(offset, offset + 999).execute()
        if not batch.data:
            break
        all_data.extend(batch.data)
        offset += 1000

    totali = defaultdict(float)
    for r in all_data:
        if not (r.get("Items") and r.get("Suppliers") and r.get("kgOut")):
            continue
        if prodotto.lower() not in r["Items"]["name"].lower():
            continue
        fornitore = r["Suppliers"]["name"]
        if fornitore == "Sconosciuto":
            continue
        if anno and not r.get("WorkingDays", {}).get("date", "").startswith(str(anno)):
            continue
        totali[fornitore] += r["kgOut"]

    if not totali:
        return {"messaggio": f"Nessun fornitore trovato per il prodotto '{prodotto}'"}

    top5 = sorted(totali.items(), key=lambda x: x[1], reverse=True)[:5]
    return [{"fornitore": k, "kg_donati": round(v)} for k, v in top5]

# --- DEFINIZIONE TOOLS PER GROQ ---

tools_def = [
    {
        "type": "function",
        "function": {
            "name": "get_summary",
            "description": "Statistiche generali ReCup: kg totali raccolti e donati, CO2 e H2O risparmiate.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_products",
            "description": "Top 10 prodotti per kg donati. Usa per domande su quali prodotti vengono recuperati di più.",
            "parameters": {
                "type": "object",
                "properties": {
                    "anno": {"type": "integer", "description": "Anno opzionale (es. 2024, 2025)"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_suppliers",
            "description": "Top 10 fornitori per volume di kg donati. Usa per domande su chi dona di più.",
            "parameters": {
                "type": "object",
                "properties": {
                    "anno": {"type": "integer", "description": "Anno opzionale"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_efficiency_by_supplier",
            "description": "Fornitori più efficienti: % kg donati su kg raccolti. Usa per domande su efficienza, sprechi, qualità dei fornitori.",
            "parameters": {
                "type": "object",
                "properties": {
                    "anno": {
                        "type": "integer",
                        "description": "Anno opzionale (es. 2024, 2025). Ometti se non specificato."
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_monthly_trend",
            "description": "Trend mensile dei kg donati. Usa per domande su andamento nel tempo, stagionalità, mesi migliori.",
            "parameters": {
                "type": "object",
                "properties": {
                    "anno": {"type": "integer", "description": "Anno opzionale"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_waste_by_product",
            "description": "Prodotti con più scarto (% kg scartati su kg raccolti). Usa per domande su sprechi, prodotti problematici.",
            "parameters": {
                "type": "object",
                "properties": {
                    "anno": {"type": "integer", "description": "Anno opzionale"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_fruiter_stats",
            "description": "Enti e organizzazioni che ricevono il cibo (fruitori): chi riceve di più. Usa per domande sui destinatari del cibo.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
{
    "type": "function",
    "function": {
        "name": "get_working_days_stats",
        "description": "Statistiche sulle giornate operative: quante giornate per anno, totale, media.",
        "parameters": {
            "type": "object",
            "properties": {
                "dummy": {"type": "string", "description": "Non usare questo parametro."}
            }
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "get_env_impact_by_year",
        "description": "CO2 e H2O risparmiate per anno. Usa per domande sull'impatto ambientale.",
        "parameters": {
            "type": "object",
            "properties": {
                "dummy": {"type": "string", "description": "Non usare questo parametro."}
            }
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "get_fruiter_stats",
        "description": "Enti e organizzazioni che ricevono il cibo (fruitori): chi riceve di più.",
        "parameters": {
            "type": "object",
            "properties": {
                "dummy": {"type": "string", "description": "Non usare questo parametro."}
            }
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "get_supplier_by_product",
        "description": "Trova i fornitori principali per un prodotto specifico. Usa quando si chiede chi fornisce un determinato prodotto.",
        "parameters": {
            "type": "object",
            "properties": {
                "prodotto": {
                    "type": "string",
                    "description": "Nome del prodotto da cercare (es. 'zucchine', 'fragole', 'pomodori')"
                },
                "anno": {
                    "type": "integer",
                    "description": "Anno opzionale"
                }
            },
            "required": ["prodotto"]
        }
    }
}
]


def run_tool(name, args):
    args = args or {}

    # Normalizza anno — può arrivare come stringa, None o intero
    if "anno" in args:
        try:
            args["anno"] = int(args["anno"]) if args["anno"] else None
        except (ValueError, TypeError):
            args["anno"] = None

    if name == "get_summary":
        return get_summary()
    elif name == "get_top_products":
        return get_top_products(**args)
    elif name == "get_top_suppliers":
        return get_top_suppliers(**args)
    elif name == "get_efficiency_by_supplier":
        return get_efficiency_by_supplier(anno=args.get("anno"))
    elif name == "get_monthly_trend":
        return get_monthly_trend(**args)
    elif name == "get_waste_by_product":
        return get_waste_by_product(**args)
    elif name == "get_env_impact_by_year":
        return get_env_impact_by_year()
    elif name == "get_fruiter_stats":
        return get_fruiter_stats()
    elif name == "get_working_days_stats":
        return get_working_days_stats()
    elif name == "get_supplier_by_product":
        return get_supplier_by_product(**args)

# --- LOOP AGENTE ---

SYSTEM = """Sei un assistente per il progetto ReCup — recupero cibo all'ingrosso a Milano.
Rispondi sempre in italiano, in modo chiaro e conciso.
Usa i tools per rispondere alle domande sui dati.
Quando dai numeri, arrotonda e usa linguaggio comprensibile anche per non tecnici."""


# Sostituisci la funzione ask() e il loop finale con questo:

def ask(domanda, history):
    """history è la lista dei messaggi precedenti della sessione"""

    messages = [{"role": "system", "content": SYSTEM}] + history + [{"role": "user", "content": domanda}]

    while True:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=tools_def,
            tool_choice="auto"
        )
        msg = response.choices[0].message

        if msg.tool_calls:
            # Aggiungi la chiamata al tool alla history
            messages.append(msg)
            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments) if tc.function.arguments else {}
                result = run_tool(tc.function.name, args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result)
                })
        else:
            # Risposta finale — aggiorna la history
            history.append({"role": "user", "content": domanda})
            history.append({"role": "assistant", "content": msg.content})
            return msg.content, history


if __name__ == "__main__":
    history = []  # memoria della sessione
    print("Agente ReCup pronto! (scrivi 'esci' per uscire, 'reset' per cancellare la memoria)\n")

    while True:
        domanda = input("Fai una domanda: ")
        if domanda.lower() == "esci":
            break
        if domanda.lower() == "reset":
            history = []
            print("→ Memoria cancellata!\n")
            continue

        risposta, history = ask(domanda, history)
        print(f"\n→ {risposta}\n")
        print(f"[memoria: {len(history) // 2} scambi]\n")