import streamlit as st
import json
import os

DATA_FILE = "rezepte.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

st.set_page_config(page_title="📷 Fuji X-T2 Rezepte", layout="wide")
st.title("📷 Fuji X-T2 Film Simulation Rezepte")

rezepte = load_data()

# --- SIDEBAR: Filter ---
st.sidebar.header("🔍 Filter")
alle_kategorien = sorted(set(r.get("kategorie", "Allgemein") for r in rezepte)) or ["Allgemein"]
filter_kat = st.sidebar.multiselect("Kategorie", alle_kategorien, default=alle_kategorien)
alle_sims = sorted(set(r.get("film_simulation", "") for r in rezepte)) or [""]
filter_sim = st.sidebar.multiselect("Film Simulation", alle_sims, default=alle_sims)

gefiltert = [
    r for r in rezepte
    if r.get("kategorie", "Allgemein") in (filter_kat or alle_kategorien)
    and r.get("film_simulation", "") in (filter_sim or alle_sims)
]

# --- REZEPTE ANZEIGEN ---
st.subheader(f"📋 {len(gefiltert)} Rezept(e) gefunden")

if not gefiltert:
    st.info("Noch keine Rezepte gespeichert. Füge unten dein erstes Rezept hinzu!")

cols = st.columns(3)
for i, r in enumerate(gefiltert):
    with cols[i % 3]:
        with st.expander(f"🎞️ {r['name']} — {r.get('kategorie', '')}"):
            st.markdown(f"**Film Simulation:** {r.get('film_simulation', '-')}")
            st.markdown(f"**Weissabgleich:** {r.get('weissabgleich', '-')}")
            st.markdown(f"**WB Shift:** {r.get('wb_shift', '-')}")
            st.markdown(f"**Dynamikbereich:** {r.get('dynamikbereich', '-')}")
            st.markdown(f"**Lichter:** {r.get('lichter', '-')}")
            st.markdown(f"**Schatten:** {r.get('schatten', '-')}")
            st.markdown(f"**Farbe:** {r.get('farbe', '-')}")
            st.markdown(f"**Schärfe:** {r.get('schaerfe', '-')}")
            st.markdown(f"**Rauschreduzierung:** {r.get('rauschreduzierung', '-')}")
            if r.get("notizen"):
                st.markdown(f"📝 *{r['notizen']}*")
            if r.get("quelle"):
                st.markdown(f"[🔗 Originalrezept ansehen]({r['quelle']})")
            if st.button(f"🗑️ Löschen", key=f"del_{i}"):
                rezepte.remove(r)
                save_data(rezepte)
                st.rerun()

# --- NEUES REZEPT HINZUFÜGEN ---
st.divider()
st.subheader("➕ Neues Rezept hinzufügen")

with st.form("neues_rezept"):
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Name des Rezepts *")
        kategorie = st.selectbox("Kategorie", ["Architektur", "Porträt", "Street", "Landschaft", "Reise", "Schwarz/Weiss", "Allgemein"])
        film_simulation = st.selectbox("Film Simulation", ["Classic Chrome", "Velvia", "Provia/Standard", "Astia/Soft", "PRO Neg. Std", "PRO Neg. Hi", "Acros", "Acros+R", "Acros+G", "Acros+Ye", "Monochrome", "Eterna", "Sepia"])
    with col2:
        weissabgleich = st.text_input("Weissabgleich (z.B. 4300K / Auto)")
        wb_shift = st.text_input("WB Shift (z.B. R-3 B+3)")
        dynamikbereich = st.selectbox("Dynamikbereich", ["DR100", "DR200", "DR400"])
        lichter = st.select_slider("Lichter (Highlight)", options=list(range(-2, 5)), value=0)
        schatten = st.select_slider("Schatten (Shadow)", options=list(range(-2, 5)), value=0)
    with col3:
        farbe = st.select_slider("Farbe (Color)", options=list(range(-4, 5)), value=0)
        schaerfe = st.select_slider("Schärfe", options=list(range(-4, 5)), value=0)
        rauschreduzierung = st.select_slider("Rauschreduzierung", options=list(range(-4, 5)), value=0)
        quelle = st.text_input("Quelle URL (optional)")
        notizen = st.text_area("Notizen (optional)", height=80)

    submitted = st.form_submit_button("💾 Rezept speichern")
    if submitted:
        if name:
            neues = {
                "name": name, "kategorie": kategorie, "film_simulation": film_simulation,
                "weissabgleich": weissabgleich, "wb_shift": wb_shift, "dynamikbereich": dynamikbereich,
                "lichter": lichter, "schatten": schatten, "farbe": farbe,
                "schaerfe": schaerfe, "rauschreduzierung": rauschreduzierung,
                "quelle": quelle, "notizen": notizen
            }
            rezepte.append(neues)
            save_data(rezepte)
            st.success(f"✅ Rezept '{name}' gespeichert!")
            st.rerun()
        else:
            st.error("Bitte mindestens einen Namen eingeben.")
