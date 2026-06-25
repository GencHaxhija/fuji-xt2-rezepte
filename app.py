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
        "duplicate_warning": "Achtung: Ein Rezept mit diesem Namen existiert bereits.",
        "delete": "Löschen",
        "deleted": "Rezept gelöscht!",
        "saved_recipes": "Gespeicherte Rezepte",
        "recipes_found": "{count} Rezept(e) gefunden",
        "filter": "Filter",
        "search": "Suche",
        "search_placeholder": "Rezeptname oder Notiz...",
        "sort": "Sortierung",
        "sort_options": ["Neueste zuerst", "Älteste zuerst", "Name A-Z", "Name Z-A"],
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
        "edit": "Bearbeiten",
        "save_changes": "Änderungen speichern",
        "recipe_updated": "Rezept '{name}' erfolgreich aktualisiert!",
        "cat_architektur": "Architektur",
        "cat_portraet": "Porträt",
        "cat_street": "Street",
        "cat_reise": "Reise",
        "cat_landschaft": "Landschaft",
        "cat_allgemein": "Allgemein",
        "scraper_note": "Hinweis: Der automatische Import liest die Webseite von FujiXWeekly aus. Falls sich das dortige Layout ändert, kann es sein, dass einige Parameter nicht korrekt erkannt werden. Bitte überprüfe die Werte nach dem Import.",
        "download_csv": "Rezepte als CSV exportieren",
        "csv_filename": "fuji_xt2_rezepte.csv",
        "compare": "Vergleichen",
        "comparison": "Rezept-Vergleich",
        "clear_comparison": "Vergleich leeren",
        "max_compare_warning": "Du kannst maximal 3 Rezepte gleichzeitig vergleichen.",
        "only_favorites": "Nur Favoriten",
        "favorite": "Favorit",
        "image_url": "Bild-URL",
        "image_url_placeholder": "https://example.com/bild.jpg",
        "grain": "Körnung",
        "tone_curve": "Gradationskurve",
        "color_chrome": "Color Chrome Effekt",
        "tags": "Tags",
        "tags_placeholder": "z.B. sonnig, reise, kontrast",
        "filter_tags": "Tags filtern",
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
        "duplicate_warning": "Warning: A recipe with this name already exists.",
        "delete": "Delete",
        "deleted": "Recipe deleted!",
        "saved_recipes": "Saved Recipes",
        "recipes_found": "{count} recipe(s) found",
        "filter": "Filter",
        "search": "Search",
        "search_placeholder": "Recipe name or note...",
        "sort": "Sorting",
        "sort_options": ["Newest first", "Oldest first", "Name A-Z", "Name Z-A"],
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
        "edit": "Edit",
        "save_changes": "Save Changes",
        "recipe_updated": "Recipe '{name}' updated successfully!",
        "cat_architektur": "Architecture",
        "cat_portraet": "Portrait",
        "cat_street": "Street",
        "cat_reise": "Travel",
        "cat_landschaft": "Landscape",
        "cat_allgemein": "General",
        "scraper_note": "Note: Auto-import reads the FujiXWeekly page layout. If their layout changes, some parameters might not be correctly recognized. Please verify the imported values.",
        "download_csv": "Export recipes as CSV",
        "csv_filename": "fuji_xt2_recipes.csv",
        "compare": "Compare",
        "comparison": "Recipe Comparison",
        "clear_comparison": "Clear Comparison",
        "max_compare_warning": "You can compare a maximum of 3 recipes at once.",
        "only_favorites": "Only Favorites",
        "favorite": "Favorite",
        "image_url": "Image URL",
        "image_url_placeholder": "https://example.com/image.jpg",
        "grain": "Grain Effect",
        "tone_curve": "Tone Curve",
        "color_chrome": "Color Chrome Effect",
        "tags": "Tags",
        "tags_placeholder": "e.g. sunny, travel, contrast",
        "filter_tags": "Filter by tags",
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


# --- Bilingual Category Support ---
CAT_MAP = {
    "Architektur": "cat_architektur",
    "Porträt": "cat_portraet",
    "Street": "cat_street",
    "Reise": "cat_reise",
    "Landschaft": "cat_landschaft",
    "Allgemein": "cat_allgemein",
}


def bicat(cat_name):
    """Return a bilingual representation of a category name."""
    key = CAT_MAP.get(cat_name)
    if key:
        return bilabel(key)
    return cat_name


def safe_int(val, default=0):
    """Safely cast value to integer, handling floats as strings."""
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return default


def recipe_matches_sim(recipe_sim, selected_sims):
    """Check if any of the recipe's film simulations are in the selected list."""
    if not selected_sims:
        return True
    sims_in_recipe = [s.strip().lower() for s in recipe_sim.split("/") if s.strip()]
    return any(s in [opt.lower() for opt in selected_sims] for s in sims_in_recipe)


def recipe_matches_tags(recipe_tags_str, selected_tags):
    """Check if the recipe contains any of the selected tags (case-insensitive)."""
    if not selected_tags:
        return True
    if not recipe_tags_str:
        return False
    recipe_tags = [tag.strip().lower() for tag in recipe_tags_str.split(",") if tag.strip()]
    return any(tag.lower() in recipe_tags for tag in selected_tags)


def convert_to_csv(data_list):
    """Convert list of dictionaries to a CSV string."""
    if not data_list:
        return ""
    import io
    import csv
    headers = [k for k in data_list[0].keys() if not k.startswith("_")]
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";", lineterminator="\n")
    writer.writerow(headers)
    for r in data_list:
        writer.writerow([r.get(h, "") for h in headers])
    return output.getvalue()

# --- Google Sheets Connection ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
SHEET_ID = "1fLh1F5JgKqJYk9Iqryl6JaJjq2jhhPhqmbdqHUjl2j4"


@st.cache_resource(ttl=300)
def get_sheet():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).sheet1
    return sheet


@st.cache_data(ttl=60)
def _load_rezepte_data():
    """Load all recipes from Google Sheets (cached, no UI calls)."""
    sheet = get_sheet()
    data = sheet.get_all_records()
    for idx, r in enumerate(data):
        r["_row_idx"] = idx
    return data


def load_rezepte():
    """Load recipes with error handling (not cached itself)."""
    try:
        return _load_rezepte_data()
    except Exception as e:
        lang_code = st.session_state.get("lang", "de")
        err_msg = LANGS.get(lang_code, LANGS["de"])["loading_error"].format(error=e)
        st.error(err_msg)
        return []


REQUIRED_HEADERS = [
    "name", "kategorie", "film_simulation", "weissabgleich",
    "wb_shift", "dynamikbereich", "lichter", "schatten",
    "farbe", "schaerfe", "rauschreduzierung", "notizen",
    "quelle", "datum", "favorit", "bild_url", "grain",
    "tone_curve", "color_chrome", "tags"
]


def update_rezept(index, rezept, t):
    """Update an existing recipe row in Google Sheets."""
    try:
        sheet = get_sheet()
        headers = sheet.row_values(1)
        if not headers:
            return False
        
        # Schema upgrade: append any missing columns
        for req in REQUIRED_HEADERS:
            if req not in headers:
                sheet.update_cell(1, len(headers) + 1, req)
                headers.append(req)
                
        row = [str(rezept.get(h, "")) for h in headers]
        sheet.update(range_name=f"A{index + 2}", values=[row], value_input_option="USER_ENTERED")
        return True
    except Exception as e:
        st.error(t["saving_error"].format(error=e))
        return False


def save_rezept(rezept, t):
    """Save a new recipe to Google Sheets."""
    try:
        sheet = get_sheet()
        headers = sheet.row_values(1)
        if not headers:
            headers = REQUIRED_HEADERS.copy()
            sheet.append_row(headers, value_input_option="USER_ENTERED")
        else:
            # Schema upgrade: append any missing columns
            for req in REQUIRED_HEADERS:
                if req not in headers:
                    sheet.update_cell(1, len(headers) + 1, req)
                    headers.append(req)
                    
        row = [str(rezept.get(h, "")) for h in headers]
        sheet.append_row(row, value_input_option="USER_ENTERED")
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

        # Film simulation candidates
        film_sim_options_lower = [
            "provia", "standard", "velvia", "vivid", "astia", "soft",
            "classic chrome", "pro neg", "acros", "monochrome", "sepia", "eterna",
        ]
        film_sim_map = {
            "provia": "Provia/Standard",
            "standard": "Provia/Standard",
            "velvia": "Velvia/Vivid",
            "vivid": "Velvia/Vivid",
            "astia": "Astia/Soft",
            "soft": "Astia/Soft",
            "classic chrome": "Classic Chrome",
            "pro neg. hi": "PRO Neg. Hi",
            "pro neg. std": "PRO Neg. Std",
            "pro neg": "PRO Neg. Hi",
            "acros": "Acros",
            "monochrome": "Monochrome",
            "sepia": "Sepia",
            "eterna": "Eterna/Cinema",
        }

        # Auto-Scraping Image (Bilder direkt aus der Internetseite übernehmen)
        # 1. Try OpenGraph image metadata
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            data["bild_url"] = og_image.get("content")

        # 2. Try Twitter image metadata
        if "bild_url" not in data or not data["bild_url"]:
            twitter_image = soup.find("meta", name="twitter:image")
            if twitter_image and twitter_image.get("content"):
                data["bild_url"] = twitter_image.get("content")

        # Helper to get the best source attribute from an img tag
        def get_best_img_src(img_tag):
            if not img_tag:
                return None
            for attr in ["data-orig-file", "data-lazy-src", "src", "srcset"]:
                val = img_tag.get(attr)
                if val:
                    if attr == "srcset":
                        urls = [item.strip().split()[0] for item in val.split(",") if item.strip()]
                        if urls:
                            return urls[-1]
                    else:
                        return val
            return None

        # 3. Try entry-content images
        if "bild_url" not in data or not data["bild_url"]:
            entry_content = soup.find(class_="entry-content")
            if entry_content:
                for img in entry_content.find_all("img"):
                    src = get_best_img_src(img)
                    if src and "avatar" not in src and "logo" not in src and not src.endswith(".gif") and "gravatar" not in src:
                        data["bild_url"] = src
                        break

        # 4. Fallback to any first non-avatar image on the page
        if "bild_url" not in data or not data["bild_url"]:
            for img in soup.find_all("img"):
                src = get_best_img_src(img)
                if src and "avatar" not in src and "logo" not in src and not src.endswith(".gif") and "gravatar" not in src:
                    data["bild_url"] = src
                    break

        # LI parsing (robust WordPress layout parsing)
        li_parsed = {}
        for li in soup.find_all("li"):
            text = li.get_text().strip()
            if ":" in text:
                parts = text.split(":", 1)
                key = parts[0].strip().lower()
                val = parts[1].strip()

                if "film simulation" in key:
                    for sim in film_sim_options_lower:
                        if sim in val.lower():
                            li_parsed["film_simulation"] = film_sim_map.get(sim, sim.title())
                            break
                elif "dynamic range" in key or "dr" in key:
                    dr_match = re.search(r"DR?([0-9]+|Auto)", val, re.IGNORECASE)
                    if dr_match:
                        li_parsed["dynamikbereich"] = f"DR{dr_match.group(1)}" if dr_match.group(1).isdigit() else dr_match.group(1)
                elif "white balance" in key or "weissabgleich" in key:
                    li_parsed["weissabgleich"] = val
                    shift_match = re.search(r"([RB][-+0-9\s,]+)", val, re.IGNORECASE)
                    if shift_match:
                        li_parsed["wb_shift"] = shift_match.group(1).strip()
                elif "wb shift" in key or "white balance shift" in key:
                    li_parsed["wb_shift"] = val
                elif "highlight" in key or "lichter" in key:
                    tone_match = re.search(r"([+-]?[0-9.]+)", val)
                    if tone_match:
                        li_parsed["lichter"] = safe_int(tone_match.group(1))
                elif "shadow" in key or "schatten" in key:
                    tone_match = re.search(r"([+-]?[0-9.]+)", val)
                    if tone_match:
                        li_parsed["schatten"] = safe_int(tone_match.group(1))
                elif "color" in key or "farbe" in key:
                    tone_match = re.search(r"([+-]?[0-9.]+)", val)
                    if tone_match:
                        li_parsed["farbe"] = safe_int(tone_match.group(1))
                elif "sharpness" in key or "schaerfe" in key:
                    tone_match = re.search(r"([+-]?[0-9.]+)", val)
                    if tone_match:
                        li_parsed["schaerfe"] = safe_int(tone_match.group(1))
                elif "noise reduction" in key or "rauschreduzierung" in key:
                    tone_match = re.search(r"([+-]?[0-9.]+)", val)
                    if tone_match:
                        li_parsed["rauschreduzierung"] = safe_int(tone_match.group(1))
                elif "grain" in key or "körnung" in key:
                    for opt in ["weak", "strong", "off"]:
                        if opt in val.lower():
                            li_parsed["grain"] = opt.title()
                            break
                elif "chrome" in key or "chrome effect" in key:
                    for opt in ["weak", "strong", "off"]:
                        if opt in val.lower():
                            li_parsed["color_chrome"] = opt.title()
                            break
                elif "tone curve" in key:
                    li_parsed["tone_curve"] = val

        # If we successfully parsed at least 3 parameters via LI, merge them
        if len(li_parsed) >= 3:
            data.update(li_parsed)
        else:
            # Fallback to regex on raw content
            for sim in film_sim_options_lower:
                if re.search(rf"Film Simulation[:\s]+{sim}", content, re.IGNORECASE):
                    data["film_simulation"] = film_sim_map.get(sim, sim.title())
                    break

            dr_match = re.search(r"(DR|Dynamic Range)[:\s]+(DR)?([0-9]+)", content, re.IGNORECASE)
            if dr_match:
                data["dynamikbereich"] = f"DR{dr_match.group(3)}"

            wb_match = re.search(r"(White Balance|Weissabgleich)[:\s]+([A-Za-z0-9\s]+)", content, re.IGNORECASE)
            if wb_match:
                data["weissabgleich"] = wb_match.group(2).strip()

            wb_shift_match = re.search(r"(WB Shift|White Balance Shift)[:\s]+([RB][-+0-9\s,]+)", content, re.IGNORECASE)
            if wb_shift_match:
                data["wb_shift"] = wb_shift_match.group(2).strip()

            hl_match = re.search(r"(Highlight|Tone)[:\s]+([+-]?[0-9])", content, re.IGNORECASE)
            if hl_match:
                data["lichter"] = safe_int(hl_match.group(2))

            sh_match = re.search(r"Shadow[:\s]+([+-]?[0-9])", content, re.IGNORECASE)
            if sh_match:
                data["schatten"] = safe_int(sh_match.group(1))

            col_match = re.search(r"(Color|Farbe)[:\s]+([+-]?[0-9])", content, re.IGNORECASE)
            if col_match:
                data["farbe"] = safe_int(col_match.group(2))

            sharp_match = re.search(r"(Sharpness|Schaerfe)[:\s]+([+-]?[0-9])", content, re.IGNORECASE)
            if sharp_match:
                data["schaerfe"] = safe_int(sharp_match.group(2))

            nr_match = re.search(r"(Noise Reduction|Rauschreduzierung)[:\s]+([+-]?[0-9])", content, re.IGNORECASE)
            if nr_match:
                data["rauschreduzierung"] = safe_int(nr_match.group(2))

            grain_match = re.search(r"Grain (Effect)?[:\s]+(Weak|Strong|Off)", content, re.IGNORECASE)
            if grain_match:
                data["grain"] = grain_match.group(2).title()

            cc_match = re.search(r"(Color|Colour) Chrome (Effect)?[:\s]+(Weak|Strong|Off)", content, re.IGNORECASE)
            if cc_match:
                data["color_chrome"] = cc_match.group(3).title()

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
search_query = st.sidebar.text_input(t["search"], placeholder=t["search_placeholder"])
only_favs = st.sidebar.checkbox(t["only_favorites"], value=False)

rezepte = load_rezepte()

alle_kategorien = sorted(
    set(r.get("kategorie", "Allgemein") for r in rezepte)
) or ["Allgemein"]
filter_kat = st.sidebar.multiselect(
    t["category"], alle_kategorien, default=alle_kategorien, format_func=bicat
)

alle_sims = sorted(
    set(r.get("film_simulation", "") for r in rezepte if r.get("film_simulation"))
) or [""]
filter_sim = st.sidebar.multiselect(
    t["film_simulation"], alle_sims, default=alle_sims
)

# Extract unique tags for sidebar filter
alle_tags_set = set()
for r in rezepte:
    tags_str = r.get("tags", "")
    if tags_str:
        for tag in tags_str.split(","):
            clean_tag = tag.strip()
            if clean_tag:
                alle_tags_set.add(clean_tag)
alle_tags = sorted(list(alle_tags_set))

filter_tags = st.sidebar.multiselect(
    t["filter_tags"], alle_tags, default=[]
)

gefiltert = [
    r for r in rezepte
    if r.get("kategorie", "Allgemein") in filter_kat
    and recipe_matches_sim(r.get("film_simulation", ""), filter_sim)
    and recipe_matches_tags(r.get("tags", ""), filter_tags)
    and (not only_favs or r.get("favorit", "").strip().lower() == "ja")
    and (
        not search_query
        or search_query.lower() in r.get("name", "").lower()
        or search_query.lower() in r.get("notizen", "").lower()
    )
]

# --- Sorting ---
st.sidebar.markdown("---")
sort_option = st.sidebar.selectbox(t["sort"], t["sort_options"])

# Apply sorting
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%d.%m.%Y %H:%M")
    except (ValueError, TypeError):
        return datetime.min

sort_idx = t["sort_options"].index(sort_option)
if sort_idx == 0:  # Newest first
    gefiltert.sort(key=lambda r: parse_date(r.get("datum", "")), reverse=True)
elif sort_idx == 1:  # Oldest first
    gefiltert.sort(key=lambda r: parse_date(r.get("datum", "")))
elif sort_idx == 2:  # Name A-Z
    gefiltert.sort(key=lambda r: r.get("name", "").lower())
elif sort_idx == 3:  # Name Z-A
    gefiltert.sort(key=lambda r: r.get("name", "").lower(), reverse=True)

# --- Sidebar Export ---
st.sidebar.markdown("---")
if gefiltert:
    csv_data = convert_to_csv(gefiltert)
    st.sidebar.download_button(
        label=t["download_csv"],
        data=csv_data,
        file_name=t["csv_filename"],
        mime="text/csv",
        key="download_csv_btn",
        use_container_width=True
    )

# --- Tabs ---
tab1, tab2 = st.tabs([t["saved_recipes"], t["new_recipe"]])

# ===================== TAB 1: Saved Recipes =====================
with tab1:
    if "compare_ids" not in st.session_state:
        st.session_state["compare_ids"] = []

    # Comparison UI Section
    compare_ids = st.session_state["compare_ids"]
    if compare_ids:
        # Find the actual recipes to compare
        compare_recipes = [r for r in rezepte if r.get("_row_idx") in compare_ids]
        if compare_recipes:
            st.markdown(f"### 📊 {t['comparison']}")
            cols = st.columns(len(compare_recipes))
            for col_idx, cr in enumerate(compare_recipes):
                with cols[col_idx]:
                    st.markdown(f"#### {cr.get('name', t['unknown'])}")
                    st.caption(f"{bicat(cr.get('kategorie', ''))} | {cr.get('film_simulation', '')}")
                    
                    if cr.get("bild_url"):
                        st.image(cr["bild_url"], use_container_width=True)
                    
                    st.markdown(f"**{bilabel('film_simulation')}:** {cr.get('film_simulation', '-')}")
                    st.markdown(f"**{bilabel('white_balance')}:** {cr.get('weissabgleich', '-')}")
                    st.markdown(f"**{bilabel('wb_shift')}:** {cr.get('wb_shift', '-')}")
                    st.markdown(f"**{bilabel('dynamic_range')}:** {cr.get('dynamikbereich', '-')}")
                    st.markdown(f"**{bilabel('highlights')}:** {cr.get('lichter', '-')}")
                    st.markdown(f"**{bilabel('shadows')}:** {cr.get('schatten', '-')}")
                    st.markdown(f"**{bilabel('color')}:** {cr.get('farbe', '-')}")
                    st.markdown(f"**{bilabel('sharpness')}:** {cr.get('schaerfe', '-')}")
                    st.markdown(f"**{bilabel('noise_reduction')}:** {cr.get('rauschreduzierung', '-')}")
                    st.markdown(f"**{bilabel('grain')}:** {cr.get('grain', '-')}")
                    st.markdown(f"**{bilabel('tone_curve')}:** {cr.get('tone_curve', '-')}")
                    st.markdown(f"**{bilabel('color_chrome')}:** {cr.get('color_chrome', '-')}")
                    
                    # Tags display as code badges
                    tags_list = [tag.strip() for tag in cr.get("tags", "").split(",") if tag.strip()]
                    if tags_list:
                        st.markdown(" ".join([f"`#{tag}`" for tag in tags_list]))
                        
                    if cr.get("notizen"):
                        st.caption(f"📝 {cr.get('notizen')}")
                        
                    # Remove from comparison button
                    if st.button("❌", key=f"remove_compare_{cr['_row_idx']}"):
                        st.session_state["compare_ids"].remove(cr["_row_idx"])
                        st.rerun()
            
            if st.button(t["clear_comparison"], key="clear_compare_btn"):
                st.session_state["compare_ids"] = []
                st.rerun()
            st.markdown("---")

    st.subheader(t["recipes_found"].format(count=len(gefiltert)))

    if not gefiltert:
        st.info(t["no_recipes_yet"])

    for i, r in enumerate(gefiltert):
        is_fav = r.get("favorit", "").strip().lower() == "ja"
        fav_prefix = "⭐ " if is_fav else ""
        label = (
            f"{fav_prefix}{r.get('name', t['unknown'])} | "
            f"{bicat(r.get('kategorie', ''))} | "
            f"{r.get('film_simulation', '')}"
        )
        with st.expander(label):
            if st.session_state.get("edit_recipe_idx") == r.get("_row_idx"):
                with st.form(key=f"edit_form_{r['_row_idx']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        edit_name = st.text_input(
                            bilabel("recipe_name") + " *",
                            value=r.get("name", ""),
                            key=f"edit_name_{r['_row_idx']}"
                        )
                        if edit_name and edit_name.strip().lower() != r.get("name", "").strip().lower():
                            if any(other.get("name", "").strip().lower() == edit_name.strip().lower() for other in rezepte):
                                st.warning(t["duplicate_warning"])
                        edit_kategorie = st.selectbox(
                            bilabel("category"),
                            CATEGORY_OPTIONS,
                            index=CATEGORY_OPTIONS.index(r.get("kategorie", "Allgemein")) if r.get("kategorie") in CATEGORY_OPTIONS else 0,
                            format_func=bicat,
                            key=f"edit_kat_{r['_row_idx']}"
                        )
                        
                        current_sims = [s.strip() for s in r.get("film_simulation", "").split("/") if s.strip()]
                        valid_current_sims = [s for s in current_sims if s in FILM_SIM_OPTIONS]
                        if not valid_current_sims and FILM_SIM_OPTIONS:
                            valid_current_sims = [FILM_SIM_OPTIONS[0]]
                            
                        edit_film_sim = st.multiselect(
                            bilabel("film_simulation"),
                            FILM_SIM_OPTIONS,
                            default=valid_current_sims,
                            key=f"edit_sim_{r['_row_idx']}"
                        )
                        edit_weissabgleich = st.text_input(
                            bilabel("white_balance"),
                            value=r.get("weissabgleich", ""),
                            key=f"edit_wb_{r['_row_idx']}"
                        )
                        edit_wb_shift = st.text_input(
                            bilabel("wb_shift"),
                            value=r.get("wb_shift", ""),
                            key=f"edit_wb_shift_{r['_row_idx']}"
                        )
                        grain_options = ["Off", "Weak", "Strong"]
                        grain_default = grain_options.index(r.get("grain")) if r.get("grain") in grain_options else 0
                        edit_grain = st.selectbox(bilabel("grain"), grain_options, index=grain_default, key=f"edit_grain_{r['_row_idx']}")
                    with col2:
                        dr_options = ["DR100", "DR200", "DR400", "Auto"]
                        dr_default = dr_options.index(r.get("dynamikbereich")) if r.get("dynamikbereich") in dr_options else 0
                        edit_dr = st.selectbox(
                            bilabel("dynamic_range"),
                            dr_options,
                            index=dr_default,
                            key=f"edit_dr_{r['_row_idx']}"
                        )
                        
                        edit_lichter = st.slider(
                            bilabel("highlights"), -2, 4, safe_int(r.get("lichter")), key=f"edit_hl_{r['_row_idx']}"
                        )
                        edit_schatten = st.slider(
                            bilabel("shadows"), -2, 4, safe_int(r.get("schatten")), key=f"edit_sh_{r['_row_idx']}"
                        )
                        edit_farbe = st.slider(
                            bilabel("color"), -4, 4, safe_int(r.get("farbe")), key=f"edit_col_{r['_row_idx']}"
                        )
                        edit_schaerfe = st.slider(
                            bilabel("sharpness"), -4, 4, safe_int(r.get("schaerfe")), key=f"edit_sharp_{r['_row_idx']}"
                        )
                        edit_nr = st.slider(
                            bilabel("noise_reduction"), -4, 4, safe_int(r.get("rauschreduzierung")), key=f"edit_nr_{r['_row_idx']}"
                        )
                        tone_options = ["None", "Linear", "Medium Soft", "Medium Hard", "Strong"]
                        tone_default = tone_options.index(r.get("tone_curve")) if r.get("tone_curve") in tone_options else 0
                        edit_tone = st.selectbox(bilabel("tone_curve"), tone_options, index=tone_default, key=f"edit_tone_{r['_row_idx']}")

                        cc_options = ["Off", "Weak", "Strong"]
                        cc_default = cc_options.index(r.get("color_chrome")) if r.get("color_chrome") in cc_options else 0
                        edit_cc = st.selectbox(bilabel("color_chrome"), cc_options, index=cc_default, key=f"edit_cc_{r['_row_idx']}")
                    
                    edit_bild_url = st.text_input(
                        bilabel("image_url"),
                        value=r.get("bild_url", ""),
                        key=f"edit_bild_url_{r['_row_idx']}"
                    )
                    edit_tags = st.text_input(
                        bilabel("tags"),
                        value=r.get("tags", ""),
                        key=f"edit_tags_{r['_row_idx']}"
                    )
                    edit_notizen = st.text_area(
                        bilabel("notes"),
                        value=r.get("notizen", ""),
                        key=f"edit_notes_{r['_row_idx']}"
                    )
                    edit_quelle = st.text_input(
                        bilabel("source"),
                        value=r.get("quelle", ""),
                        key=f"edit_source_{r['_row_idx']}"
                    )
                    
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        save_submitted = st.form_submit_button(t["save_changes"])
                        if save_submitted:
                            if not edit_name:
                                st.error(t["enter_name"])
                            else:
                                updated_data = r.copy()
                                for k in list(updated_data.keys()):
                                    if k.startswith("_"):
                                        del updated_data[k]
                                updated_data.update({
                                    "name": edit_name,
                                    "kategorie": edit_kategorie,
                                    "film_simulation": " / ".join(edit_film_sim) if isinstance(edit_film_sim, list) else edit_film_sim,
                                    "weissabgleich": edit_weissabgleich,
                                    "wb_shift": edit_wb_shift,
                                    "dynamikbereich": edit_dr,
                                    "lichter": edit_lichter,
                                    "schatten": edit_schatten,
                                    "farbe": edit_farbe,
                                    "schaerfe": edit_schaerfe,
                                    "rauschreduzierung": edit_nr,
                                    "grain": edit_grain,
                                    "tone_curve": edit_tone,
                                    "color_chrome": edit_cc,
                                    "bild_url": edit_bild_url,
                                    "tags": edit_tags,
                                    "notizen": edit_notizen,
                                    "quelle": edit_quelle,
                                    "datum": r.get("datum", datetime.now().strftime("%d.%m.%Y %H:%M")),
                                })
                                if update_rezept(r["_row_idx"], updated_data, t):
                                    st.success(t["recipe_updated"].format(name=edit_name))
                                    if "edit_recipe_idx" in st.session_state:
                                        del st.session_state["edit_recipe_idx"]
                                    st.cache_data.clear()
                                    st.rerun()
                    with col_cancel:
                        cancel_submitted = st.form_submit_button(t["cancel"])
                        if cancel_submitted:
                            if "edit_recipe_idx" in st.session_state:
                                del st.session_state["edit_recipe_idx"]
                            st.rerun()
            else:
                # Layout checking: If there is an image, split in two columns
                if r.get("bild_url"):
                    col_img, col_params = st.columns([1, 2])
                    with col_img:
                        st.image(r["bild_url"], use_container_width=True)
                    with col_params:
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
                            st.markdown(f"**{bilabel('grain')}:** {r.get('grain', '-')}")
                            st.markdown(f"**{bilabel('tone_curve')}:** {r.get('tone_curve', '-')}")
                            st.markdown(f"**{bilabel('color_chrome')}:** {r.get('color_chrome', '-')}")
                            if r.get("quelle"):
                                st.markdown(f"**{bilabel('source')}:** [{r.get('quelle')}]({r.get('quelle')})")
                else:
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
                        st.markdown(f"**{bilabel('grain')}:** {r.get('grain', '-')}")
                        st.markdown(f"**{bilabel('tone_curve')}:** {r.get('tone_curve', '-')}")
                        st.markdown(f"**{bilabel('color_chrome')}:** {r.get('color_chrome', '-')}")
                        if r.get("quelle"):
                            st.markdown(f"**{bilabel('source')}:** [{r.get('quelle')}]({r.get('quelle')})")

                # Tags display as code badges
                tags_list = [tag.strip() for tag in r.get("tags", "").split(",") if tag.strip()]
                if tags_list:
                    st.markdown(" ".join([f"`#{tag}`" for tag in tags_list]))

                if r.get("notizen"):
                    st.info(t["note_label"].format(note=r.get("notizen")))
                if r.get("datum"):
                    st.caption(t["saved_on"].format(date=r.get("datum")))

                # Delete and Edit buttons / confirmation logic
                if st.session_state.get("delete_confirm_idx") == i:
                    st.warning(t["confirm_delete"].format(name=r.get("name", t["unknown"])))
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button(t["yes_delete"], key=f"yes_del_{i}", type="primary"):
                            real_index = r.get("_row_idx")
                            if real_index is not None and delete_rezept(real_index, t):
                                st.success(t["deleted"])
                                if "delete_confirm_idx" in st.session_state:
                                    del st.session_state["delete_confirm_idx"]
                                st.cache_data.clear()
                                st.rerun()
                    with col_no:
                        if st.button(t["cancel"], key=f"cancel_del_{i}"):
                            if "delete_confirm_idx" in st.session_state:
                                del st.session_state["delete_confirm_idx"]
                            st.rerun()
                else:
                    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns([1, 1, 1, 4])
                    with col_btn1:
                        fav_label = "⭐" if is_fav else "☆"
                        if st.button(fav_label, key=f"fav_btn_{i}"):
                            updated_rezept = r.copy()
                            updated_rezept["favorit"] = "" if is_fav else "ja"
                            for k in list(updated_rezept.keys()):
                                if k.startswith("_"):
                                    del updated_rezept[k]
                            if update_rezept(r["_row_idx"], updated_rezept, t):
                                st.cache_data.clear()
                                st.rerun()
                    with col_btn2:
                        if st.button(t["edit"], key=f"edit_btn_{i}"):
                            st.session_state["edit_recipe_idx"] = r["_row_idx"]
                            st.rerun()
                    with col_btn3:
                        if st.button(t["delete"], key=f"del_{i}"):
                            st.session_state["delete_confirm_idx"] = i
                            st.rerun()
                    with col_btn4:
                        is_compared = r["_row_idx"] in st.session_state.get("compare_ids", [])
                        if st.checkbox(t["compare"], value=is_compared, key=f"comp_check_{r['_row_idx']}"):
                            if r["_row_idx"] not in st.session_state.get("compare_ids", []):
                                if len(st.session_state.get("compare_ids", [])) >= 3:
                                    st.error(t["max_compare_warning"])
                                else:
                                    st.session_state["compare_ids"].append(r["_row_idx"])
                                    st.rerun()
                        else:
                            if r["_row_idx"] in st.session_state.get("compare_ids", []):
                                st.session_state["compare_ids"].remove(r["_row_idx"])
                                st.rerun()

# ===================== TAB 2: New Recipe =====================
with tab2:
    st.subheader(t["new_recipe"])

    # URL Import Section
    st.markdown(f"#### {t['url_import']}")
    url_input = st.text_input(
        t["url_input"], placeholder=t["source_placeholder"]
    )
    st.caption(t["scraper_note"])

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
            if name and any(r.get("name", "").strip().lower() == name.strip().lower() for r in rezepte):
                st.warning(t["duplicate_warning"])
            kategorie = st.selectbox(bilabel("category"), CATEGORY_OPTIONS, format_func=bicat)

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
            grain_options = ["Off", "Weak", "Strong"]
            grain_default = grain_options.index(scraped.get("grain")) if scraped.get("grain") in grain_options else 0
            grain = st.selectbox(bilabel("grain"), grain_options, index=grain_default)

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
            tone_options = ["None", "Linear", "Medium Soft", "Medium Hard", "Strong"]
            tone_default = tone_options.index(scraped.get("tone_curve")) if scraped.get("tone_curve") in tone_options else 0
            tone_curve = st.selectbox(bilabel("tone_curve"), tone_options, index=tone_default)

            cc_options = ["Off", "Weak", "Strong"]
            cc_default = cc_options.index(scraped.get("color_chrome")) if scraped.get("color_chrome") in cc_options else 0
            color_chrome = st.selectbox(bilabel("color_chrome"), cc_options, index=cc_default)

        bild_url = st.text_input(
            bilabel("image_url"),
            value=scraped.get("bild_url", ""),
            placeholder=t["image_url_placeholder"],
        )
        tags = st.text_input(
            bilabel("tags"),
            value=scraped.get("tags", ""),
            placeholder=t["tags_placeholder"],
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
                    "grain": grain,
                    "tone_curve": tone_curve,
                    "color_chrome": color_chrome,
                    "bild_url": bild_url,
                    "tags": tags,
                    "notizen": notizen,
                    "quelle": quelle,
                    "datum": datetime.now().strftime("%d.%m.%Y %H:%M"),
                }
                if save_rezept(neues_rezept, t):
                    st.success(t["recipe_saved"].format(name=name))
                    if "scraped_data" in st.session_state:
                        del st.session_state["scraped_data"]
                    st.cache_data.clear()
                    st.rerun()
