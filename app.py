import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re

# --- Page Config (MUST be the first Streamlit command) ---
st.set_page_config(page_title="Fuji X-T2 Rezepte", layout="wide", page_icon="📷")

# --- Language Support ---
LANGS = {
    "de": {
        "title": "Fuji X-T2 Rezeptverwaltung",
        "subtitle": "Deine persönliche Rezept-Datenbank | gespeichert in Google Sheets",
        "recipe_data": "Rezeptdaten (manuell oder aus URL)",
        "recipe_name": "Rezeptname",
        "recipe_name_placeholder": "z.B. Mein Classic Chrome Look",
        "recipe_name_required": "Rezeptname *",
        "category": "Kategorie",
        "film_simulation": "Film Simulation",
        "white_balance": "Weissabgleich",
        "wb_placeholder": "z.B. Tageslicht oder 5200K",
        "wb_shift": "WB Shift (R/B)",
        "wb_shift_placeholder": "z.B. R+3, B-2",
        "dynamic_range": "Dynamikbereich",
        "highlights": "Lichter",
        "shadows": "Schatten",
        "color": "Farbe",
        "sharpness": "Schärfe",
        "noise_reduction": "Rauschreduzierung",
        "notes": "Notizen",
        "notes_placeholder": "z.B. Ideal für goldene Stunde",
        "source": "Quelle (URL)",
        "source_placeholder": "https://fujixweekly.com/...",
        "save_recipe": "Rezept speichern",
        "recipe_saved": "Rezept '{name}' erfolgreich gespeichert!",
        "new_recipe": "Neues Rezept speichern",
        "url_import": "Automatisch von FujiXWeekly importieren",
        "url_input": "FujiXWeekly URL",
        "url_button": "Von URL auslesen",
        "load_recipe": "Lade Rezept...",
        "scraping_error": "Fehler beim Auslesen: {error}",
        "recipe_read": "Rezept ausgelesen! Prüfe die Werte unten und passe sie bei Bedarf an.",
        "no_data": "Keine Rezepte gefunden.",
        "no_recipes_yet": "Noch keine Rezepte gespeichert. Füge unten dein erstes Rezept hinzu!",
        "enter_url": "Bitte eine URL eingeben.",
        "enter_name": "Bitte einen Rezeptnamen eingeben!",
        "delete": "Löschen",
        "deleted": "Rezept gelöscht!",
        "saved_recipes": "Gespeicherte Rezepte",
        "recipes_found": "{count} Rezept(e) gefunden",
        "filter": "Filter",
        "unknown": "Unbekannt",
        "saved_on": "Gespeichert am: {date}",
        "note_label": "Notiz: {note}",
        "loading_error": "Fehler beim Laden: {error}",
        "saving_error": "Fehler beim Speichern: {error}",
        "deleting_error": "Fehler beim Löschen: {error}",
        "no_scrape_data": "Keine Daten gefunden. Bitte manuell eingeben.",
        "confirm_delete": "Bist du sicher, dass du das Rezept '{name}' löschen möchtest?",
        "yes_delete": "Ja, löschen",
        "cancel": "Abbrechen",
    },
    "en": {
        "title": "Fuji X-T2 Recipe Management",
        "subtitle": "Your personal recipe database | stored in Google Sheets",
        "recipe_data": "Recipe Data (manual or from URL)",
        "recipe_name": "Recipe Name",
        "recipe_name_placeholder": "e.g. My Classic Chrome Look",
        "recipe_name_required": "Recipe Name *",
        "category": "Category",
        "film_simulation": "Film Simulation",
        "white_balance": "White Balance",
        "wb_placeholder": "e.g. Daylight or 5200K",
        "wb_shift": "WB Shift (R/B)",
        "wb_shift_placeholder": "e.g. R+3, B-2",
        "dynamic_range": "Dynamic Range",
        "highlights": "Highlights",
        "shadows": "Shadows",
        "color": "Color",
        "sharpness": "Sharpness",
        "noise_reduction": "Noise Reduction",
        "notes": "Notes",
        "notes_placeholder": "e.g. Ideal for golden hour",
        "source": "Source (URL)",
        "source_placeholder": "https://fujixweekly.com/...",
        "save_recipe": "Save Recipe",
        "recipe_saved": "Recipe '{name}' saved successfully!",
        "new_recipe": "Save New Recipe",
        "url_import": "Auto-import from FujiXWeekly",
        "url_input": "FujiXWeekly URL",
        "url_button": "Load from URL",
        "load_recipe": "Loading recipe...",
        "scraping_error": "Error during scraping: {error}",
        "recipe_read": "Recipe read! Check and adjust values below if needed.",
        "no_data": "No recipes found.",
        "no_recipes_yet": "No recipes saved yet. Add your first recipe below!",
        "enter_url": "Please enter a URL.",
        "enter_name": "Please enter a recipe name!",
        "delete": "Delete",
        "deleted": "Recipe deleted!",
        "saved_recipes": "Saved Recipes",
        "recipes_found": "{count} recipe(s) found",
        "filter": "Filter",
        "unknown": "Unknown",
        "saved_on": "Saved on: {date}",
        "note_label": "Note: {note}",
        "loading_error": "Error loading data: {error}",
        "saving_error": "Error saving recipe: {error}",
        "deleting_error": "Error deleting recipe: {error}",
        "no_scrape_data": "No data found. Please enter manually.",
        "confirm_delete": "Are you sure you want to delete the recipe '{name}'?",
        "yes_delete": "Yes, delete",
        "cancel": "Cancel",
    },
}


def bilabel(key):
    """Return a dual-language label like 'Weissabgleich / White Balance'.

    If both languages have the same text (e.g. 'Film Simulation'), the
    label is shown only once to avoid redundancy.
    """
    de = LANGS["de"][key]
    en = LANGS["en"][key]
    if de == en:
        return de
    return f"{de} / {en}"

# --- Google Sheets Connection ---
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


def load_rezepte(t):
    """Load all recipes from Google Sheets."""
    try:
        sheet = get_sheet()
        data = sheet.get_all_records()
        return data
    except Exception as e:
        st.error(t["loading_error"].format(error=e))
        return []


def save_rezept(rezept, t):
    """Save a new recipe to Google Sheets."""
    try:
        sheet = get_sheet()
        headers = sheet.row_values(1)
        if not headers:
            headers = [
                "name", "kategorie", "film_simulation", "weissabgleich",
                "wb_shift", "dynamikbereich", "lichter", "schatten",
                "farbe", "schaerfe", "rauschreduzierung", "notizen",
                "quelle", "datum",
            ]
            sheet.append_row(headers)
        row = [rezept.get(h, "") for h in headers]
        sheet.append_row(row)
        return True
    except Exception as e:
        st.error(t["saving_error"].format(error=e))
        return False


def delete_rezept(index, t):
    """Delete a recipe row from Google Sheets."""
    try:
        sheet = get_sheet()
        sheet.delete_rows(index + 2)
        return True
    except Exception as e:
        st.error(t["deleting_error"].format(error=e))
        return False


# --- URL Scraping Function ---
def scrape_fujixweekly(url):
    """Scrape recipe settings from a FujiXWeekly article URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        content = soup.get_text()

        data = {}

        # Recipe name from page title
        title = soup.find("title")
        if title:
            data["name"] = title.get_text().split("|")[0].strip()

        # Film Simulation
        film_sims = [
            "Provia", "Standard", "Velvia", "Vivid", "Astia", "Soft",
            "Classic Chrome", "PRO Neg", "Acros", "Monochrome", "Sepia", "Eterna",
        ]
        for sim in film_sims:
            if re.search(rf"Film Simulation[:\s]+{sim}", content, re.IGNORECASE):
                data["film_simulation"] = sim
                break

        # Dynamic Range
        dr_match = re.search(
            r"(DR|Dynamic Range)[:\s]+(DR)?([0-9]+)", content, re.IGNORECASE
        )
        if dr_match:
            data["dynamikbereich"] = f"DR{dr_match.group(3)}"

        # White Balance
        wb_match = re.search(
            r"(White Balance|Weissabgleich)[:\s]+([A-Za-z0-9\s]+)",
            content, re.IGNORECASE,
        )
        if wb_match:
            data["weissabgleich"] = wb_match.group(2).strip()

        # WB Shift
        wb_shift_match = re.search(
            r"(WB Shift|White Balance Shift)[:\s]+([RB][-+0-9\s,]+)",
            content, re.IGNORECASE,
        )
        if wb_shift_match:
            data["wb_shift"] = wb_shift_match.group(2).strip()

        # Highlights
        hl_match = re.search(
            r"(Highlight|Tone)[:\s]+([+-]?[0-9])", content, re.IGNORECASE
        )
        if hl_match:
            data["lichter"] = int(hl_match.group(2))

        # Shadows
        sh_match = re.search(
            r"Shadow[:\s]+([+-]?[0-9])", content, re.IGNORECASE
        )
        if sh_match:
            data["schatten"] = int(sh_match.group(2))

        # Color
        col_match = re.search(
            r"(Color|Farbe)[:\s]+([+-]?[0-9])", content, re.IGNORECASE
        )
        if col_match:
            data["farbe"] = int(col_match.group(2))

        # Sharpness
        sharp_match = re.search(
            r"(Sharpness|Schaerfe)[:\s]+([+-]?[0-9])", content, re.IGNORECASE
        )
        if sharp_match:
            data["schaerfe"] = int(sharp_match.group(2))

        # Noise Reduction
        nr_match = re.search(
            r"(Noise Reduction|Rauschreduzierung)[:\s]+([+-]?[0-9])",
            content, re.IGNORECASE,
        )
        if nr_match:
            data["rauschreduzierung"] = int(nr_match.group(2))

        data["quelle"] = url
        return data, None
    except Exception as e:
        return None, str(e)


# --- Film Simulation Options (X-T2) ---
FILM_SIM_OPTIONS = [
    "Provia/Standard", "Velvia/Vivid", "Astia/Soft",
    "Classic Chrome", "PRO Neg. Hi", "PRO Neg. Std",
    "Acros", "Acros+R", "Acros+G", "Acros+Ye",
    "Monochrome", "Monochrome+R", "Monochrome+G", "Monochrome+Ye",
    "Sepia", "Eterna/Cinema",
]

# --- Category Options ---
CATEGORY_OPTIONS = [
    "Architektur", "Porträt", "Street", "Reise", "Landschaft", "Allgemein",
]


# ===================================================================
# APP LAYOUT
# ===================================================================

# Language selector
if "lang" not in st.session_state:
    st.session_state["lang"] = "de"

col_lang1, col_lang2 = st.columns([6, 1])
with col_lang2:
    lang = st.selectbox(
        "🌐",
        ["de", "en"],
        index=0 if st.session_state["lang"] == "de" else 1,
        label_visibility="collapsed",
    )
    st.session_state["lang"] = lang

t = LANGS[st.session_state["lang"]]

# Title & subtitle
st.title(t["title"])
st.caption(t["subtitle"])

# --- Sidebar Filter ---
st.sidebar.header(t["filter"])
rezepte = load_rezepte(t)

alle_kategorien = sorted(
    set(r.get("kategorie", "Allgemein") for r in rezepte)
) or ["Allgemein"]
filter_kat = st.sidebar.multiselect(
    t["category"], alle_kategorien, default=alle_kategorien
)

alle_sims = sorted(
    set(r.get("film_simulation", "") for r in rezepte if r.get("film_simulation"))
) or [""]
filter_sim = st.sidebar.multiselect(
    t["film_simulation"], alle_sims, default=alle_sims
)

gefiltert = [
    r for r in rezepte
    if r.get("kategorie", "Allgemein") in filter_kat
    and r.get("film_simulation", "") in (filter_sim or alle_sims)
]

# --- Tabs ---
tab1, tab2 = st.tabs([t["saved_recipes"], t["new_recipe"]])

# ===================== TAB 1: Saved Recipes =====================
with tab1:
    st.subheader(t["recipes_found"].format(count=len(gefiltert)))

    if not gefiltert:
        st.info(t["no_recipes_yet"])

    for i, r in enumerate(gefiltert):
        label = (
            f"{r.get('name', t['unknown'])} | "
            f"{r.get('kategorie', '')} | "
            f"{r.get('film_simulation', '')}"
        )
        with st.expander(label):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**{bilabel('film_simulation')}:** {r.get('film_simulation', '-')}")
                st.markdown(f"**{bilabel('white_balance')}:** {r.get('weissabgleich', '-')}")
                st.markdown(f"**{bilabel('wb_shift')}:** {r.get('wb_shift', '-')}")
                st.markdown(f"**{bilabel('dynamic_range')}:** {r.get('dynamikbereich', '-')}")
            with col2:
                st.markdown(f"**{bilabel('highlights')}:** {r.get('lichter', '-')}")
                st.markdown(f"**{bilabel('shadows')}:** {r.get('schatten', '-')}")
                st.markdown(f"**{bilabel('color')}:** {r.get('farbe', '-')}")
            with col3:
                st.markdown(f"**{bilabel('sharpness')}:** {r.get('schaerfe', '-')}")
                st.markdown(f"**{bilabel('noise_reduction')}:** {r.get('rauschreduzierung', '-')}")
                if r.get("quelle"):
                    st.markdown(f"**{bilabel('source')}:** [{r.get('quelle')}]({r.get('quelle')})")

            if r.get("notizen"):
                st.info(t["note_label"].format(note=r.get("notizen")))
            if r.get("datum"):
                st.caption(t["saved_on"].format(date=r.get("datum")))

            # Delete confirmation logic
            if st.session_state.get("delete_confirm_idx") == i:
                st.warning(t["confirm_delete"].format(name=r.get("name", t["unknown"])))
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button(t["yes_delete"], key=f"yes_del_{i}", type="primary"):
                        real_index = rezepte.index(r)
                        if delete_rezept(real_index, t):
                            st.success(t["deleted"])
                            if "delete_confirm_idx" in st.session_state:
                                del st.session_state["delete_confirm_idx"]
                            st.cache_resource.clear()
                            st.rerun()
                with col_no:
                    if st.button(t["cancel"], key=f"cancel_del_{i}"):
                        if "delete_confirm_idx" in st.session_state:
                            del st.session_state["delete_confirm_idx"]
                        st.rerun()
            else:
                if st.button(t["delete"], key=f"del_{i}"):
                    st.session_state["delete_confirm_idx"] = i
                    st.rerun()

# ===================== TAB 2: New Recipe =====================
with tab2:
    st.subheader(t["new_recipe"])

    # URL Import Section
    st.markdown(f"#### {t['url_import']}")
    url_input = st.text_input(
        t["url_input"], placeholder=t["source_placeholder"]
    )

    if st.button(t["url_button"]):
        if url_input:
            with st.spinner(t["load_recipe"]):
                scraped_data, error = scrape_fujixweekly(url_input)
                if error:
                    st.error(t["scraping_error"].format(error=error))
                elif scraped_data:
                    st.session_state["scraped_data"] = scraped_data
                    st.success(t["recipe_read"])
                else:
                    st.warning(t["no_scrape_data"])
        else:
            st.warning(t["enter_url"])

    st.markdown("---")
    st.markdown(f"#### {t['recipe_data']}")

    # Pre-fill from scraping if available
    scraped = st.session_state.get("scraped_data", {})

    with st.form("rezept_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(
                bilabel("recipe_name") + " *",
                value=scraped.get("name", ""),
                placeholder=t["recipe_name_placeholder"],
            )
            kategorie = st.selectbox(bilabel("category"), CATEGORY_OPTIONS)

            film_sim_default_idx = next(
                (i for i, opt in enumerate(FILM_SIM_OPTIONS)
                 if scraped.get("film_simulation", "").lower() in opt.lower()),
                0,
            )
            film_sim = st.multiselect(
                bilabel("film_simulation"),
                FILM_SIM_OPTIONS,
                default=[FILM_SIM_OPTIONS[film_sim_default_idx]],
            )
            weissabgleich = st.text_input(
                bilabel("white_balance"),
                value=scraped.get("weissabgleich", ""),
                placeholder=t["wb_placeholder"],
            )
            wb_shift = st.text_input(
                bilabel("wb_shift"),
                value=scraped.get("wb_shift", ""),
                placeholder=t["wb_shift_placeholder"],
            )

        with col2:
            dr_options = ["DR100", "DR200", "DR400", "Auto"]
            dr_default = next(
                (i for i, opt in enumerate(dr_options)
                 if scraped.get("dynamikbereich", "") == opt),
                0,
            )
            dynamikbereich = st.selectbox(
                bilabel("dynamic_range"), dr_options, index=dr_default
            )
            lichter = st.slider(
                bilabel("highlights"), -2, 4, scraped.get("lichter", 0)
            )
            schatten = st.slider(
                bilabel("shadows"), -2, 4, scraped.get("schatten", 0)
            )
            farbe = st.slider(
                bilabel("color"), -4, 4, scraped.get("farbe", 0)
            )
            schaerfe = st.slider(
                bilabel("sharpness"), -4, 4, scraped.get("schaerfe", 0)
            )
            rauschreduzierung = st.slider(
                bilabel("noise_reduction"), -4, 4, scraped.get("rauschreduzierung", 0)
            )

        notizen = st.text_area(
            bilabel("notes"), placeholder=t["notes_placeholder"]
        )
        quelle = st.text_input(
            bilabel("source"),
            value=scraped.get("quelle", url_input or ""),
            placeholder=t["source_placeholder"],
        )

        submitted = st.form_submit_button(t["save_recipe"])
        if submitted:
            if not name:
                st.error(t["enter_name"])
            else:
                neues_rezept = {
                    "name": name,
                    "kategorie": kategorie,
                    "film_simulation": (
                        " / ".join(film_sim)
                        if isinstance(film_sim, list)
                        else film_sim
                    ),
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
                    "datum": datetime.now().strftime("%d.%m.%Y %H:%M"),
                }
                if save_rezept(neues_rezept, t):
                    st.success(t["recipe_saved"].format(name=name))
                    if "scraped_data" in st.session_state:
                        del st.session_state["scraped_data"]
                    st.cache_resource.clear()
                    st.rerun()
