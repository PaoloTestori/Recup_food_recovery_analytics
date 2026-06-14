"""
components/palette.py
─────────────────────
Palette colori condivisa Recup — unica fonte di verità per entrambe le
dashboard (Mercati rionali + Ortomercato).

Colori desaturati pensati per tema scuro: su sfondo nero i colori a piena
saturazione (#00ff9c, #ff4b4b, #ffea00) "sparano"; questi toni mantengono
il significato semantico senza affaticare gli occhi.

USO:
    from components.palette import VERDE, ROSSO, BLU, GIALLO, GRIGIO
    fig = px.bar(..., color_discrete_sequence=[VERDE])
"""

# ── semantici ────────────────────────────────────────────────────────────────
VERDE  = "#2E8B57"   # positivo / crescita / kg donati   (sea green, già Ortomercato)
ROSSO  = "#E74C3C"   # negativo / calo / scarto          (già Ortomercato)
BLU    = "#5B9BD5"   # neutro / volumi / kg raccolti     (già Ortomercato)
GIALLO = "#F2C94C"   # accento KPI (ambrato, sostituisce #ffea00)
GRIGIO = "#9aa0a6"   # categorie residuali ("Altro")

# ── varianti con trasparenza per annotazioni/aree ───────────────────────────
VERDE_SOFT = "rgba(46, 139, 87, 0.9)"
ROSSO_SOFT = "rgba(231, 76, 60, 0.9)"
BLU_AREA   = "rgba(91, 155, 213, 0.35)"   # riempimenti tipo banda ±std

# ── neutri del tema ──────────────────────────────────────────────────────────
TESTO_SECONDARIO = "#8a9ba8"   # etichette, sottotitoli
BORDO_CARD       = "#1a3a2a"   # bordo kpi-card / selectbox
SFONDO_CARD_1    = "#0d1f1a"   # gradiente card, inizio
SFONDO_CARD_2    = "#0a1a14"   # gradiente card, fine