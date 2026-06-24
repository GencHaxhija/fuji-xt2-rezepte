import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re

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
    except Exception    as e:
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

# --- URL Scraping Funktion ---
def scrape_fujixweekly(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.get_text()
        
        data = {}
        
        # Rezeptname aus Titel
        title = soup.find('title')
        if title:
            data['name'] = title.get_text().split('|')[0].strip()
        
        # Film Simulation
        film_sims = ["Provia", "Standard", "Velvia", "Vivid", "Astia", "Soft",
                     "Classic Chrome", "PRO Neg", "Acros", "Monochrome", "Sepia", "Eterna"]
        for sim in film_sims:
            if re.search(rf"Film Simulation[:\s]+{sim}", content, re.IGNORECASE):
                data['film_simulation'] = sim
                break
        
        # Dynamikbereich
        dr_match = re.search(r"(DR|Dynamic Range)[:\s]+(DR)?([0-9]+)", content, re.IGNORECASE)
        if dr_match:
            dr_val = dr_match.group(3)
            data['dynamikbereich'] = f"DR{dr_val}"
        
        # Weissabgleich
        wb_match = re.search(r"(White Balance|Weissabgleich)[:\s]+([A-Za-z0-9\s]+)", content, re.IGNORECASE)
        if wb_match:
            data['weissabgleich'] = wb_match.group(2).strip()
        
        # WB Shift
        wb_shift_match = re.search(r"(WB Shift|White Balance Shift)[:\s]+([RB][-+0-9\s,]+)", content, re.IGNORECASE)
        if wb_shift_match:
            data['wb_shift'] = wb_shift_match.group(2).strip()
        
        # Highlight / Lichter
        hl_match = re.search(r"(Highlight|Tone)[:\s]+([+-]?[0-9])", content, re.IGNORECASE)
        if hl_match:
            data['lichter'] = int(hl_match.group(2))
        
        # Shadow / Schatten
        sh_match = re.search(r"Shadow[:\s]+([+-]?[0-9])", content, re.IGNORECASE)
        if sh_match:
            data['schatten'] = int(sh_match.group(2))
        
        # Farbe / Color
        col_match = re.search(r"(Color|Farbe)[:\s]+([+-]?[0-9])", content, re.IGNORECASE)
        if col_match:
            data['farbe'] = int(col_match.group(2))
        
        # Schaerfe / Sharpness
        sharp_match = re.search(r"(Sharpness|Schaerfe)[:\s]+([+-]?[0-9])", content, re.IGNORECASE)
        if sharp_match:
            data['schaerfe'] = int(sharp_match.group(2))
        
        # Rauschreduzierung / Noise Reduction
        nr_match = re.search(r"(Noise Reduction|Rauschreduzierung)[:\s]+([+-]?[0-9])", content, re.IGNORECASE)
        if nr_match:
            data['rauschreduzierung'] = int(nr_match.group(2))
        
        data['quelle'] = url
        return data, None
    except Exception as e:
        return None, str(e)

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
    
    # URL Import Sektion
    st.markdown("#### Automatisch von FujiXWeekly importieren")
    url_input = st.text_input("FujiXWeekly URL", placeholder="https://fujixweekly.com/...")
    if st.button("Von URL auslesen"):
        if url_input:
            with st.spinner("Lade Rezept..."):
                scraped_data, error = scrape_fujixweekly(url_input)
                if error:
                    st.error(f"Fehler beim Auslesen: {error}")
                elif scraped_data:
                    st.session_state['scraped_data'] = scraped_data
                    st.success("Rezept ausgelesen! Pruefe die Werte unten und passe sie bei Bedarf an.")
                else:
                    st.warning("Keine Daten gefunden. Bitte manuell eingeben.")
        else:
            st.warning("Bitte eine URL eingeben.")
    
    st.markdown("---")
    st.markdown("#### Rezeptdaten (manuell oder aus URL)")
    
    # Vorausfuellen wenn scraping erfolgreich
    scraped = st.session_state.get('scraped_data', {})
    
    with st.form("rezept_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Rezeptname *", value=scraped.get('name', ''), placeholder="z.B. Mein Classic Chrome Look")
            kategorie = st.selectbox("Kategorie", ["Architektur", "Portraet", "Street", "Reise", "Landschaft", "Allgemein"])
            film_sim_options = [
                "Provia/Standard", "Velvia/Vivid", "Astia/Soft",
                "Classic Chrome", "PRO Neg. Hi", "PRO Neg. Std",
                "Acros", "Acros+R", "Acros+G", "Acros+Ye",
                "Monochrome", "Monochrome+R", "Monochrome+G", "Monochrome+Ye",
                "Sepia", "Eterna/Cinema"
            ]
            film_sim_default = next((i for i, opt in enumerate(film_sim_options) if scraped.get('film_simulation','').lower() in opt.lower()), 0)
            film_sim = st.selectbox("Film Simulation", film_sim_options, index=film_sim_default)
            weissabgleich = st.text_input("Weissabgleich", value=scraped.get('weissabgleich', ''), placeholder="z.B. Tageslicht oder 5200K")
            wb_shift = st.text_input("WB Shift (R/B)", value=scraped.get('wb_shift', ''), placeholder="z.B. R+3, B-2")
        with col2:
            dr_options = ["DR100", "DR200", "DR400", "Auto"]
            dr_default = next((i for i, opt in enumerate(dr_options) if scraped.get('dynamikbereich','') == opt), 0)
            dynamikbereich = st.selectbox("Dynamikbereich", dr_options, index=dr_default)
            lichter = st.slider("Lichter", -2, 4, scraped.get('lichter', 0))
            schatten = st.slider("Schatten", -2, 4, scraped.get('schatten', 0))
            farbe = st.slider("Farbe", -4, 4, scraped.get('farbe', 0))
            schaerfe = st.slider("Schaerfe", -4, 4, scraped.get('schaerfe', 0))
            rauschreduzierung = st.slider("Rauschreduzierung", -4, 4, scraped.get('rauschreduzierung', 0))
        notizen = st.text_area("Notizen", placeholder="z.B. Ideal fuer goldene Stunde")
        quelle = st.text_input("Quelle (URL)", value=scraped.get('quelle', url_input or ''), placeholder="https://fujixweekly.com/...")
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
                    if 'scraped_data' in st.session_state:
                        del st.session_state['scraped_data']
                    st.cache_resource.clear()
                    st.rerun()
