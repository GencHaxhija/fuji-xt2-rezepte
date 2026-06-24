import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# --- Google Sheets Verbindung ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
SHEET_ID = "1fLh1F5JgKqJYk9Iqryl6JaJjq2jhhPhqmbdqHUjl2j4"

@st.cache_resource
def get_sheet():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).sheet1
    return sheet

def load_rezepte():
    try:
        sheet = get_sheet()
        data = sheet.get_all_records()
        return data
    except Exception as e:
        st.error(f"Fehler beim Laden: {e}")
        return []

def save_rezept(rezept):
    try:
        sheet = get_sheet()
        headers = sheet.row_values(1)
        if not headers:
            headers = ["name","kategorie","film_simulation","weissabgleich",
                       "wb_shift","dynamikbereich","lichter","schatten",
                       "farbe","schaerfe","rauschreduzierung","notizen",
                       "quelle","datum"]
            sheet.append_row(headers)
        row = [rezept.get(h, "") for h in headers]
        sheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"Fehler beim Speichern: {e}")
        return False

def delete_rezept(index):
    try:
        sheet = get_sheet()
        sheet.delete_rows(index + 2)
        return True
    except Exception as e:
        st.error(f"Fehler beim Loeschen: {e}")
        return False

# --- App Layout ---
st.set_page_config(page_title="Fuji X-T2 Rezepte", layout="wide", page_icon="camera")
st.title("Fuji X-T2 Film Simulation Rezepte")
st.caption("Deine persoenliche Rezept-Datenbank | gespeichert in Google Sheets")

# --- Sidebar Filter ---
st.sidebar.header("Filter")
rezepte = load_rezepte()

alle_kategorien = sorted(set(r.get("kategorie", "Allgemein") for r in rezepte)) or ["Allgemein"]
filter_kat = st.sidebar.multiselect("Kategorie", alle_kategorien, default=alle_kategorien)

alle_sims = sorted(set(r.get("film_simulation", "") for r in rezepte if r.get("film_simulation"))) or [""]
filter_sim = st.sidebar.multiselect("Film Simulation", alle_sims, default=alle_sims)

gefiltert = [
    r for r in rezepte
    if r.get("kategorie", "Allgemein") in filter_kat
    and r.get("film_simulation", "") in (filter_sim or alle_sims)
]

# --- Rezepte anzeigen ---
tab1, tab2 = st.tabs(["Rezepte ansehen", "Neues Rezept hinzufuegen"])

with tab1:
    st.subheader(f"{len(gefiltert)} Rezept(e) gefunden")
    if not gefiltert:
        st.info("Noch keine Rezepte gespeichert. Fuege unten dein erstes Rezept hinzu!")
    for i, r in enumerate(gefiltert):
        with st.expander(f"{r.get('name','Unbekannt')} | {r.get('kategorie','')} | {r.get('film_simulation','')} "):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Film Simulation:** {r.get('film_simulation','-')}")
                st.markdown(f"**Weissabgleich:** {r.get('weissabgleich','-')}")
                st.markdown(f"**WB Shift:** {r.get('wb_shift','-')}")
                st.markdown(f"**Dynamikbereich:** {r.get('dynamikbereich','-')}")
            with col2:
                st.markdown(f"**Lichter:** {r.get('lichter','-')}")
                st.markdown(f"**Schatten:** {r.get('schatten','-')}")
                st.markdown(f"**Farbe:** {r.get('farbe','-')}")
            with col3:
                st.markdown(f"**Schaerfe:** {r.get('schaerfe','-')}")
                st.markdown(f"**Rauschreduzierung:** {r.get('rauschreduzierung','-')}")
                if r.get('quelle'):
                    st.markdown(f"**Quelle:** [{r.get('quelle')}]({r.get('quelle')})")
            if r.get('notizen'):
                st.info(f"Notiz: {r.get('notizen')}")
            if r.get('datum'):
                st.caption(f"Gespeichert am: {r.get('datum')}")
            if st.button("Loeschen", key=f"del_{i}"):
                real_index = rezepte.index(r)
                if delete_rezept(real_index):
                    st.success("Rezept geloescht!")
                    st.cache_resource.clear()
                    st.rerun()

with tab2:
    st.subheader("Neues Rezept speichern")
    with st.form("rezept_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Rezeptname *", placeholder="z.B. Mein Classic Chrome Look")
            kategorie = st.selectbox("Kategorie", ["Architektur", "Portraet", "Street", "Reise", "Landschaft", "Allgemein"])
            film_sim = st.selectbox("Film Simulation", [
                "Provia/Standard", "Velvia/Vivid", "Astia/Soft",
                "Classic Chrome", "PRO Neg. Hi", "PRO Neg. Std",
                "Acros", "Acros+R", "Acros+G", "Acros+Ye",
                "Monochrome", "Monochrome+R", "Monochrome+G", "Monochrome+Ye",
                "Sepia", "Eterna/Cinema"
            ])
            weissabgleich = st.text_input("Weissabgleich", placeholder="z.B. Tageslicht oder 5200K")
            wb_shift = st.text_input("WB Shift (R/B)", placeholder="z.B. R+3, B-2")
        with col2:
            dynamikbereich = st.selectbox("Dynamikbereich", ["DR100", "DR200", "DR400", "Auto"])
            lichter = st.slider("Lichter", -2, 4, 0)
            schatten = st.slider("Schatten", -2, 4, 0)
            farbe = st.slider("Farbe", -4, 4, 0)
            schaerfe = st.slider("Schaerfe", -4, 4, 0)
            rauschreduzierung = st.slider("Rauschreduzierung", -4, 4, 0)
        notizen = st.text_area("Notizen", placeholder="z.B. Ideal fuer goldene Stunde")
        quelle = st.text_input("Quelle (URL)", placeholder="https://fujixweekly.com/...")
        submitted = st.form_submit_button("Rezept speichern")
        if submitted:
            if not name:
                st.error("Bitte einen Rezeptnamen eingeben!")
            else:
                neues_rezept = {
                    "name": name,
                    "kategorie": kategorie,
                    "film_simulation": film_sim,
                    "weissabgleich": weissabgleich,
                    "wb_shift": wb_shift,
                    "dynamikbereich": dynamikbereich,
                    "lichter": lichter,
                    "schatten": schatten,
                    "farbe": farbe,
                    "schaerfe": schaerfe,
                    "rauschreduzierung": rauschreduzierung,
                    "notizen": notizen,
                    "quelle": quelle,
                    "datum": datetime.now().strftime("%d.%m.%Y %H:%M")
                }
                if save_rezept(neues_rezept):
                    st.success(f"Rezept '{name}' erfolgreich gespeichert!")
                    st.cache_resource.clear()
                    st.rerun()
