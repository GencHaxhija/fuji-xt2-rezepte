'use client';
import { useEffect, useState, useCallback } from 'react';

const FILM_SIM_OPTIONS = [
  'Provia/Standard','Velvia/Vivid','Astia/Soft',
  'Classic Chrome','Classic Neg.','PRO Neg. Hi','PRO Neg. Std',
  'Acros','Acros+R','Acros+G','Acros+Ye',
  'Monochrome','Monochrome+R','Monochrome+G','Monochrome+Ye',
  'Sepia','Eterna/Cinema','Eterna Bleach Bypass','Nostalgic Neg.','Reala Ace',
];
const CATEGORY_OPTIONS = ['Architektur','Porträt','Street','Reise','Landschaft','Allgemein'];
const DR_OPTIONS = ['DR100','DR200','DR400','Auto'];
const GRAIN_OPTIONS = ['Off','Weak','Strong'];
const CC_OPTIONS = ['Off','Weak','Strong'];
const TONE_OPTIONS = ['None','Linear','Medium Soft','Medium Hard','Strong'];

// CSS-Filter-Profile für jede Film-Simulation
const FILM_SIM_FILTERS: Record<string, string> = {
  'Provia/Standard':      'saturate(1.0) contrast(1.0) brightness(1.0)',
  'Velvia/Vivid':         'saturate(1.7) contrast(1.25) brightness(1.02)',
  'Astia/Soft':           'saturate(0.85) contrast(0.9) brightness(1.05)',
  'Classic Chrome':       'saturate(0.7) contrast(1.1) brightness(0.97) sepia(0.15)',
  'Classic Neg.':         'saturate(0.75) contrast(1.15) brightness(0.95) sepia(0.1)',
  'PRO Neg. Hi':          'saturate(0.9) contrast(1.1) brightness(1.0)',
  'PRO Neg. Std':         'saturate(0.8) contrast(0.95) brightness(1.0)',
  'Acros':                'grayscale(1) contrast(1.15) brightness(0.98)',
  'Acros+R':              'grayscale(1) contrast(1.2) brightness(0.97) sepia(0.05)',
  'Acros+G':              'grayscale(1) contrast(1.1) brightness(1.02)',
  'Acros+Ye':             'grayscale(1) contrast(1.15) brightness(1.0)',
  'Monochrome':           'grayscale(1) contrast(1.0) brightness(1.0)',
  'Monochrome+R':         'grayscale(1) contrast(1.05) brightness(0.98)',
  'Monochrome+G':         'grayscale(1) contrast(0.98) brightness(1.02)',
  'Monochrome+Ye':        'grayscale(1) contrast(1.02) brightness(1.0)',
  'Sepia':                'sepia(0.9) contrast(0.95) brightness(1.0)',
  'Eterna/Cinema':        'saturate(0.8) contrast(0.88) brightness(1.03)',
  'Eterna Bleach Bypass': 'saturate(0.35) contrast(1.3) brightness(0.96)',
  'Nostalgic Neg.':       'saturate(0.75) contrast(0.92) brightness(1.05) sepia(0.2)',
  'Reala Ace':            'saturate(1.05) contrast(1.0) brightness(1.01)',
};

type Rezept = { [k: string]: string | number; _rowIdx: number };
type Lang = 'de' | 'en';

const T = {
  de: {
    title: 'Fuji X-T2 Rezeptverwaltung',
    subtitle: 'Deine persönliche Rezept-Datenbank | gespeichert in Google Sheets',
    saved: 'Gespeicherte Rezepte', newRecipe: 'Neues Rezept',
    search: 'Suche', searchPh: 'Rezeptname oder Notiz...',
    filter: 'Filter', category: 'Kategorie', filmSim: 'Film Simulation',
    filterTags: 'Tags filtern', onlyFavs: 'Nur Favoriten',
    sort: 'Sortierung', sortOpts: ['Neueste zuerst','Älteste zuerst','Name A-Z','Name Z-A'],
    downloadCsv: 'CSV exportieren', csvFile: 'fuji_xt2_rezepte.csv',
    found: (n: number) => `${n} Rezept(e)`,
    noRecipes: 'Noch keine Rezepte. Füge dein erstes unten hinzu!',
    unknown: 'Unbekannt', edit: 'Bearbeiten', delete: 'Löschen', cancel: 'Abbrechen',
    save: 'Rezept speichern', saveChanges: 'Änderungen speichern',
    confirmDel: (n: string) => `Rezept "${n}" wirklich löschen?`,
    yesDel: 'Ja, löschen', deleted: 'Rezept gelöscht!',
    saved_msg: (n: string) => `Rezept "${n}" gespeichert!`,
    updated_msg: (n: string) => `Rezept "${n}" aktualisiert!`,
    enterName: 'Bitte Rezeptname eingeben!',
    duplicate: 'Ein Rezept mit diesem Namen existiert bereits.',
    urlImport: 'Automatisch von FujiXWeekly importieren',
    urlInput: 'FujiXWeekly URL', urlBtn: 'Auslesen',
    loading: 'Lädt...', scrapeOk: 'Rezept ausgelesen! Bitte Werte prüfen.',
    scrapeErr: (e: string) => `Fehler: ${e}`, noData: 'Keine Daten gefunden.',
    scrapeNote: 'Hinweis: Automatischer Import. Werte nach dem Import bitte prüfen.',
    recipeData: 'Rezeptdaten', recipeName: 'Rezeptname *',
    namePh: 'z.B. Mein Classic Chrome Look',
    wb: 'Weissabgleich', wbPh: 'z.B. Tageslicht oder 5200K',
    wbShift: 'WB Shift (R/B)', wbShiftPh: 'z.B. R+3, B-2',
    dr: 'Dynamikbereich', highlights: 'Lichter', shadows: 'Schatten',
    color: 'Farbe', sharpness: 'Schärfe', nr: 'Rauschreduzierung',
    grain: 'Körnung', toneCurve: 'Gradationskurve', colorChrome: 'Color Chrome',
    imageUrl: 'Bild-URL', imageUrlPh: 'https://example.com/bild.jpg',
    tags: 'Tags', tagsPh: 'z.B. sonnig, reise', notes: 'Notizen', notesPh: 'z.B. Ideal für goldene Stunde',
    source: 'Quelle (URL)', sourcePh: 'https://fujixweekly.com/...',
    savedOn: (d: string) => `Gespeichert am: ${d}`,
    compare: 'Vergleichen', comparison: 'Rezept-Vergleich',
    clearCompare: 'Vergleich leeren', maxCompare: 'Maximal 3 Rezepte vergleichen.',
    favorite: 'Favorit',
    simPreview: 'Simulationsvorschau',
    reset: 'Zurücksetzen',
  },
  en: {
    title: 'Fuji X-T2 Recipe Management',
    subtitle: 'Your personal recipe database | stored in Google Sheets',
    saved: 'Saved Recipes', newRecipe: 'New Recipe',
    search: 'Search', searchPh: 'Recipe name or note...',
    filter: 'Filter', category: 'Category', filmSim: 'Film Simulation',
    filterTags: 'Filter by tags', onlyFavs: 'Only Favorites',
    sort: 'Sort', sortOpts: ['Newest first','Oldest first','Name A-Z','Name Z-A'],
    downloadCsv: 'Export CSV', csvFile: 'fuji_xt2_recipes.csv',
    found: (n: number) => `${n} recipe(s)`,
    noRecipes: 'No recipes yet. Add your first one below!',
    unknown: 'Unknown', edit: 'Edit', delete: 'Delete', cancel: 'Cancel',
    save: 'Save Recipe', saveChanges: 'Save Changes',
    confirmDel: (n: string) => `Delete recipe "${n}"?`,
    yesDel: 'Yes, delete', deleted: 'Recipe deleted!',
    saved_msg: (n: string) => `Recipe "${n}" saved!`,
    updated_msg: (n: string) => `Recipe "${n}" updated!`,
    enterName: 'Please enter a recipe name!',
    duplicate: 'A recipe with this name already exists.',
    urlImport: 'Auto-import from FujiXWeekly',
    urlInput: 'FujiXWeekly URL', urlBtn: 'Load',
    loading: 'Loading...', scrapeOk: 'Recipe loaded! Please verify values.',
    scrapeErr: (e: string) => `Error: ${e}`, noData: 'No data found.',
    scrapeNote: 'Note: Auto-import. Please verify imported values.',
    recipeData: 'Recipe Data', recipeName: 'Recipe Name *',
    namePh: 'e.g. My Classic Chrome Look',
    wb: 'White Balance', wbPh: 'e.g. Daylight or 5200K',
    wbShift: 'WB Shift (R/B)', wbShiftPh: 'e.g. R+3, B-2',
    dr: 'Dynamic Range', highlights: 'Highlights', shadows: 'Shadows',
    color: 'Color', sharpness: 'Sharpness', nr: 'Noise Reduction',
    grain: 'Grain Effect', toneCurve: 'Tone Curve', colorChrome: 'Color Chrome',
    imageUrl: 'Image URL', imageUrlPh: 'https://example.com/image.jpg',
    tags: 'Tags', tagsPh: 'e.g. sunny, travel', notes: 'Notes', notesPh: 'e.g. Ideal for golden hour',
    source: 'Source (URL)', sourcePh: 'https://fujixweekly.com/...',
    savedOn: (d: string) => `Saved on: ${d}`,
    compare: 'Compare', comparison: 'Recipe Comparison',
    clearCompare: 'Clear Comparison', maxCompare: 'You can compare max 3 recipes.',
    favorite: 'Favorite',
    simPreview: 'Simulation Preview',
    reset: 'Reset',
  },
};

function unique(arr: string[]): string[] {
  const seen: { [k: string]: boolean } = {};
  return arr.filter(v => { if (seen[v]) return false; seen[v] = true; return true; });
}

/** Clamps a numeric value to [min, max]. Falls back to 0 if NaN. */
function clampVal(v: unknown, min: number, max: number): number {
  const n = Number(v);
  if (isNaN(n)) return 0;
  return Math.min(max, Math.max(min, n));
}

/** Slider with Reset-Button (✕) — only visible when value ≠ 0 */
function Slider({ label, min, max, value, onChange }: { label: string; min: number; max: number; value: number; onChange: (v: number) => void }) {
  return (
    <div className="field">
      <label>{label}</label>
      <div className="slider-row">
        <input type="range" min={min} max={max} value={value} onChange={e => onChange(Number(e.target.value))} />
        <span className="slider-val">{value > 0 ? `+${value}` : value}</span>
        <button
          type="button"
          className={`slider-reset${value !== 0 ? ' visible' : ''}`}
          onClick={() => onChange(0)}
          aria-label="Auf 0 zurücksetzen"
          tabIndex={value !== 0 ? 0 : -1}
        >✕</button>
      </div>
    </div>
  );
}

/** Film-Simulation Vorschau mit CSS-Filtern */
function FilmSimPreview({ simulations, label }: { simulations: string[]; label: string }) {
  const [activeIdx, setActiveIdx] = useState(0);
  const sim = simulations[activeIdx] || simulations[0] || 'Provia/Standard';
  const filter = FILM_SIM_FILTERS[sim] || FILM_SIM_FILTERS['Provia/Standard'];

  return (
    <div className="sim-preview">
      <div className="sim-preview-label">{label}</div>
      {simulations.length > 1 && (
        <div className="sim-preview-tabs">
          {simulations.map((s, i) => (
            <button key={s} type="button"
              className={`sim-tab-btn${activeIdx === i ? ' active' : ''}`}
              onClick={() => setActiveIdx(i)}>
              {s}
            </button>
          ))}
        </div>
      )}
      <div className="sim-preview-name">{sim}</div>
      <div className="sim-preview-img-wrap">
        {/* Neutral reference stripe */}
        <div className="sim-preview-split">
          <img
            src="https://picsum.photos/seed/fuji-sample/600/200"
            alt="Original"
            className="sim-preview-img"
            style={{ filter: 'none' }}
            loading="lazy"
          />
          <div className="sim-preview-split-label">Original</div>
        </div>
        <div className="sim-preview-split">
          <img
            src="https://picsum.photos/seed/fuji-sample/600/200"
            alt={sim}
            className="sim-preview-img"
            style={{ filter }}
            loading="lazy"
          />
          <div className="sim-preview-split-label">{sim}</div>
        </div>
      </div>
    </div>
  );
}

function MultiSelect({ options, selected, onChange }: { options: string[]; selected: string[]; onChange: (v: string[]) => void }) {
  return (
    <div className="multiselect-wrapper">
      {options.map(o => (
        <button key={o} type="button" className={`ms-option${selected.includes(o) ? ' selected' : ''}`}
          onClick={() => onChange(selected.includes(o) ? selected.filter(x => x !== o) : [...selected, o])}>
          {o}
        </button>
      ))}
    </div>
  );
}

function emptyForm() {
  return {
    name: '', kategorie: 'Allgemein', film_simulation: ['Provia/Standard'],
    weissabgleich: '', wb_shift: '', dynamikbereich: 'DR100',
    lichter: 0, schatten: 0, farbe: 0, schaerfe: 0, rauschreduzierung: 0,
    grain: 'Off', tone_curve: 'None', color_chrome: 'Off',
    bild_url: '', tags: '', notizen: '', quelle: '',
  };
}

export default function Home() {
  const [lang, setLang] = useState<Lang>('de');
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [tab, setTab] = useState<'saved' | 'new'>('saved');
  const [rezepte, setRezepte] = useState<Rezept[]>([]);
  const [loadingData, setLoadingData] = useState(true);
  const [expanded, setExpanded] = useState<number | null>(null);
  const [editIdx, setEditIdx] = useState<number | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null);
  const [compareIds, setCompareIds] = useState<number[]>([]);
  const [flash, setFlash] = useState<{ type: 'success' | 'error' | 'warning'; msg: string } | null>(null);

  const [search, setSearch] = useState('');
  const [onlyFavs, setOnlyFavs] = useState(false);
  const [filterKat, setFilterKat] = useState<string[]>([]);
  const [filterSim, setFilterSim] = useState<string[]>([]);
  const [filterTags, setFilterTags] = useState<string[]>([]);
  const [sortOpt, setSortOpt] = useState(0);

  const [form, setForm] = useState(emptyForm());
  const [editForm, setEditForm] = useState<typeof form | null>(null);

  const [scrapeUrl, setScrapeUrl] = useState('');
  const [scraping, setScraping] = useState(false);
  const [scrapeMsg, setScrapeMsg] = useState<{ type: 'success' | 'error' | 'info'; msg: string } | null>(null);

  const t = T[lang];

  const showFlash = (type: 'success' | 'error' | 'warning', msg: string) => {
    setFlash({ type, msg });
    setTimeout(() => setFlash(null), 3500);
  };

  const fetchRezepte = useCallback(async () => {
    setLoadingData(true);
    try {
      const res = await fetch('/api/rezepte');
      const data = await res.json();
      if (Array.isArray(data)) setRezepte(data);
    } finally {
      setLoadingData(false);
    }
  }, []);

  useEffect(() => { fetchRezepte(); }, [fetchRezepte]);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const allKat = unique(rezepte.map(r => String(r.kategorie || 'Allgemein'))).sort();
  const allSims = unique(rezepte.map(r => String(r.film_simulation || '')).filter(Boolean)).sort();
  const allTagsRaw: string[] = [];
  rezepte.forEach(r => String(r.tags || '').split(',').forEach(t => { const c = t.trim(); if (c) allTagsRaw.push(c); }));
  const allTags = unique(allTagsRaw).sort();

  let filtered = rezepte.filter(r => {
    if (filterKat.length && !filterKat.includes(String(r.kategorie || 'Allgemein'))) return false;
    if (filterSim.length) {
      const sims = String(r.film_simulation || '').split('/').map(s => s.trim().toLowerCase());
      if (!filterSim.some(s => sims.includes(s.toLowerCase()))) return false;
    }
    if (filterTags.length) {
      const rt = String(r.tags || '').split(',').map(s => s.trim().toLowerCase());
      if (!filterTags.some(t => rt.includes(t.toLowerCase()))) return false;
    }
    if (onlyFavs && String(r.favorit || '').toLowerCase() !== 'ja') return false;
    if (search) {
      const q = search.toLowerCase();
      if (!String(r.name || '').toLowerCase().includes(q) && !String(r.notizen || '').toLowerCase().includes(q)) return false;
    }
    return true;
  });

  const parseDate = (s: string) => { try { const p = s.split(' '); const [d,m,y] = p[0].split('.'); return new Date(`${y}-${m}-${d}T${p[1] || '00:00'}`).getTime(); } catch { return 0; } };
  if (sortOpt === 0) filtered.sort((a, b) => parseDate(String(b.datum || '')) - parseDate(String(a.datum || '')));
  else if (sortOpt === 1) filtered.sort((a, b) => parseDate(String(a.datum || '')) - parseDate(String(b.datum || '')));
  else if (sortOpt === 2) filtered.sort((a, b) => String(a.name || '').localeCompare(String(b.name || '')));
  else if (sortOpt === 3) filtered.sort((a, b) => String(b.name || '').localeCompare(String(a.name || '')));

  const exportCsv = () => {
    const headers = Object.keys(filtered[0] || {}).filter(k => !k.startsWith('_'));
    const rows = [headers.join(';'), ...filtered.map(r => headers.map(h => String(r[h] ?? '')).join(';'))];
    const blob = new Blob([rows.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = t.csvFile; a.click();
  };

  const handleScrape = async () => {
    if (!scrapeUrl) { setScrapeMsg({ type: 'error', msg: 'Bitte URL eingeben.' }); return; }
    setScraping(true); setScrapeMsg(null);
    try {
      const res = await fetch('/api/scrape', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ url: scrapeUrl }) });
      const result = await res.json();
      if (result.error) { setScrapeMsg({ type: 'error', msg: t.scrapeErr(result.error) }); return; }
      const d = result.data || {};
      const simMatch = FILM_SIM_OPTIONS.find(o => o.toLowerCase() === (d.film_simulation || '').toLowerCase()) || 'Provia/Standard';
      setForm(prev => ({
        ...prev,
        name: d.name || prev.name,
        film_simulation: [simMatch],
        weissabgleich: d.weissabgleich || prev.weissabgleich,
        wb_shift: d.wb_shift || prev.wb_shift,
        dynamikbereich: DR_OPTIONS.includes(d.dynamikbereich) ? d.dynamikbereich : prev.dynamikbereich,
        lichter: d.lichter != null ? clampVal(d.lichter, -2, 4) : prev.lichter,
        schatten: d.schatten != null ? clampVal(d.schatten, -2, 4) : prev.schatten,
        farbe: d.farbe != null ? clampVal(d.farbe, -4, 4) : prev.farbe,
        schaerfe: d.schaerfe != null ? clampVal(d.schaerfe, -4, 4) : prev.schaerfe,
        rauschreduzierung: d.rauschreduzierung != null ? clampVal(d.rauschreduzierung, -4, 4) : prev.rauschreduzierung,
        grain: GRAIN_OPTIONS.includes(d.grain) ? d.grain : prev.grain,
        color_chrome: CC_OPTIONS.includes(d.color_chrome) ? d.color_chrome : prev.color_chrome,
        tone_curve: TONE_OPTIONS.includes(d.tone_curve) ? d.tone_curve : prev.tone_curve,
        bild_url: d.bild_url || prev.bild_url,
        quelle: scrapeUrl,
      }));
      setScrapeMsg({ type: 'success', msg: t.scrapeOk });
      setTab('new');
    } finally {
      setScraping(false);
    }
  };

  const handleSave = async () => {
    if (!form.name.trim()) { showFlash('error', t.enterName); return; }
    const now = new Date();
    const datum = `${String(now.getDate()).padStart(2,'0')}.${String(now.getMonth()+1).padStart(2,'0')}.${now.getFullYear()} ${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`;
    const payload = { ...form, film_simulation: form.film_simulation.join(' / '), datum, favorit: '' };
    const res = await fetch('/api/rezepte', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    const data = await res.json();
    if (data.error) { showFlash('error', data.error); return; }
    showFlash('success', t.saved_msg(form.name));
    setForm(emptyForm());
    setScrapeUrl('');
    setScrapeMsg(null);
    await fetchRezepte();
    setTab('saved');
  };

  const handleUpdate = async (r: Rezept) => {
    if (!editForm || !editForm.name.trim()) { showFlash('error', t.enterName); return; }
    const payload = { ...editForm, film_simulation: editForm.film_simulation.join(' / '), _rowIdx: r._rowIdx, datum: r.datum, favorit: r.favorit || '' };
    const res = await fetch('/api/rezepte', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    const data = await res.json();
    if (data.error) { showFlash('error', data.error); return; }
    showFlash('success', t.updated_msg(editForm.name));
    setEditIdx(null); setEditForm(null);
    await fetchRezepte();
  };

  const handleDelete = async (r: Rezept) => {
    const res = await fetch('/api/rezepte', { method: 'DELETE', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ rowIdx: r._rowIdx }) });
    const data = await res.json();
    if (data.error) { showFlash('error', data.error); return; }
    showFlash('success', t.deleted);
    setDeleteConfirm(null);
    await fetchRezepte();
  };

  const toggleFav = async (r: Rezept) => {
    const isFav = String(r.favorit || '').toLowerCase() === 'ja';
    const payload = { ...r, favorit: isFav ? '' : 'ja' };
    await fetch('/api/rezepte', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    await fetchRezepte();
  };

  const startEdit = (r: Rezept) => {
    const sims = String(r.film_simulation || '').split('/').map(s => s.trim()).filter(s => FILM_SIM_OPTIONS.includes(s));
    setEditForm({
      name: String(r.name || ''),
      kategorie: String(r.kategorie || 'Allgemein'),
      film_simulation: sims.length ? sims : ['Provia/Standard'],
      weissabgleich: String(r.weissabgleich || ''),
      wb_shift: String(r.wb_shift || ''),
      dynamikbereich: DR_OPTIONS.includes(String(r.dynamikbereich)) ? String(r.dynamikbereich) : 'DR100',
      lichter: Number(r.lichter) || 0,
      schatten: Number(r.schatten) || 0,
      farbe: Number(r.farbe) || 0,
      schaerfe: Number(r.schaerfe) || 0,
      rauschreduzierung: Number(r.rauschreduzierung) || 0,
      grain: GRAIN_OPTIONS.includes(String(r.grain)) ? String(r.grain) : 'Off',
      tone_curve: TONE_OPTIONS.includes(String(r.tone_curve)) ? String(r.tone_curve) : 'None',
      color_chrome: CC_OPTIONS.includes(String(r.color_chrome)) ? String(r.color_chrome) : 'Off',
      bild_url: String(r.bild_url || ''),
      tags: String(r.tags || ''),
      notizen: String(r.notizen || ''),
      quelle: String(r.quelle || ''),
    });
    setEditIdx(r._rowIdx);
    setExpanded(r._rowIdx);
  };

  const RecipeForm = ({ f, setF, onSubmit, submitLabel, onCancel }: {
    f: typeof form; setF: (v: typeof form) => void;
    onSubmit: () => void; submitLabel: string; onCancel?: () => void;
  }) => (
    <div>
      <div className="form-grid">
        <div>
          <div className="field"><label>{t.recipeName}</label><input value={f.name} onChange={e => setF({ ...f, name: e.target.value })} placeholder={t.namePh} /></div>
          {f.name && rezepte.some(r => String(r.name || '').toLowerCase() === f.name.toLowerCase()) && editIdx === null &&
            <div className="alert alert-warning" style={{ marginBottom: '0.5rem' }}>{t.duplicate}</div>}
          <div className="field">
            <label>{t.category}</label>
            <select value={f.kategorie} onChange={e => setF({ ...f, kategorie: e.target.value })}>
              {CATEGORY_OPTIONS.map(o => <option key={o} value={o}>{o}</option>)}
            </select>
          </div>
          <div className="field">
            <label>{t.filmSim}</label>
            <MultiSelect options={FILM_SIM_OPTIONS} selected={f.film_simulation} onChange={v => setF({ ...f, film_simulation: v })} />
          </div>
          {/* Film-Simulation Vorschau */}
          {f.film_simulation.length > 0 && (
            <FilmSimPreview simulations={f.film_simulation} label={t.simPreview} />
          )}
          <div className="field"><label>{t.wb}</label><input value={f.weissabgleich} onChange={e => setF({ ...f, weissabgleich: e.target.value })} placeholder={t.wbPh} /></div>
          <div className="field"><label>{t.wbShift}</label><input value={f.wb_shift} onChange={e => setF({ ...f, wb_shift: e.target.value })} placeholder={t.wbShiftPh} /></div>
          <div className="field"><label>{t.grain}</label><select value={f.grain} onChange={e => setF({ ...f, grain: e.target.value })}>{GRAIN_OPTIONS.map(o => <option key={o} value={o}>{o}</option>)}</select></div>
          <div className="field"><label>{t.imageUrl}</label><input value={f.bild_url} onChange={e => setF({ ...f, bild_url: e.target.value })} placeholder={t.imageUrlPh} /></div>
          <div className="field"><label>{t.tags}</label><input value={f.tags} onChange={e => setF({ ...f, tags: e.target.value })} placeholder={t.tagsPh} /></div>
        </div>
        <div>
          <div className="field"><label>{t.dr}</label><select value={f.dynamikbereich} onChange={e => setF({ ...f, dynamikbereich: e.target.value })}>{DR_OPTIONS.map(o => <option key={o} value={o}>{o}</option>)}</select></div>
          <Slider label={t.highlights} min={-2} max={4} value={Number(f.lichter)} onChange={v => setF({ ...f, lichter: v })} />
          <Slider label={t.shadows} min={-2} max={4} value={Number(f.schatten)} onChange={v => setF({ ...f, schatten: v })} />
          <Slider label={t.color} min={-4} max={4} value={Number(f.farbe)} onChange={v => setF({ ...f, farbe: v })} />
          <Slider label={t.sharpness} min={-4} max={4} value={Number(f.schaerfe)} onChange={v => setF({ ...f, schaerfe: v })} />
          <Slider label={t.nr} min={-4} max={4} value={Number(f.rauschreduzierung)} onChange={v => setF({ ...f, rauschreduzierung: v })} />
          <div className="field"><label>{t.toneCurve}</label><select value={f.tone_curve} onChange={e => setF({ ...f, tone_curve: e.target.value })}>{TONE_OPTIONS.map(o => <option key={o} value={o}>{o}</option>)}</select></div>
          <div className="field"><label>{t.colorChrome}</label><select value={f.color_chrome} onChange={e => setF({ ...f, color_chrome: e.target.value })}>{CC_OPTIONS.map(o => <option key={o} value={o}>{o}</option>)}</select></div>
          <div className="field"><label>{t.notes}</label><textarea rows={2} value={f.notizen} onChange={e => setF({ ...f, notizen: e.target.value })} placeholder={t.notesPh} /></div>
          <div className="field"><label>{t.source}</label><input value={f.quelle} onChange={e => setF({ ...f, quelle: e.target.value })} placeholder={t.sourcePh} /></div>
        </div>
      </div>
      <div className="btn-row">
        <button type="button" className="btn btn-primary" onClick={onSubmit}>{submitLabel}</button>
        {onCancel && <button type="button" className="btn" onClick={onCancel}>{t.cancel}</button>}
      </div>
    </div>
  );

  return (
    <div className="layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div>
          <h2>{t.filter}</h2>
          <div className="field"><input placeholder={t.searchPh} value={search} onChange={e => setSearch(e.target.value)} /></div>
          <div className="field" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <input type="checkbox" id="favs" checked={onlyFavs} onChange={e => setOnlyFavs(e.target.checked)} style={{ width: 'auto' }} />
            <label htmlFor="favs" style={{ marginBottom: 0 }}>{t.onlyFavs}</label>
          </div>
        </div>
        {allKat.length > 0 && (
          <div>
            <h2>{t.category}</h2>
            <MultiSelect options={allKat} selected={filterKat} onChange={setFilterKat} />
          </div>
        )}
        {allSims.length > 0 && (
          <div>
            <h2>{t.filmSim}</h2>
            <MultiSelect options={allSims} selected={filterSim} onChange={setFilterSim} />
          </div>
        )}
        {allTags.length > 0 && (
          <div>
            <h2>{t.filterTags}</h2>
            <MultiSelect options={allTags} selected={filterTags} onChange={setFilterTags} />
          </div>
        )}
        <div>
          <h2>{t.sort}</h2>
          <select value={sortOpt} onChange={e => setSortOpt(Number(e.target.value))} style={{ fontSize: '0.8rem' }}>
            {t.sortOpts.map((o, i) => <option key={i} value={i}>{o}</option>)}
          </select>
        </div>
        <hr className="divider" />
        {filtered.length > 0 && <button className="btn btn-sm" onClick={exportCsv} style={{ width: '100%' }}>{t.downloadCsv}</button>}
        <hr className="divider" />
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <div className="lang-switch">
            {(['de','en'] as Lang[]).map(l => <button key={l} className={`lang-btn${lang === l ? ' active' : ''}`} onClick={() => setLang(l)}>{l.toUpperCase()}</button>)}
          </div>
          <button className="theme-btn" onClick={() => setTheme(t => t === 'light' ? 'dark' : 'light')} title="Toggle theme">{theme === 'light' ? '🌙' : '☀️'}</button>
        </div>
      </aside>

      {/* Main */}
      <main className="main">
        <div className="header">
          <div>
            <h1>📷 {t.title}</h1>
            <p>{t.subtitle}</p>
          </div>
        </div>

        {flash && <div className={`alert alert-${flash.type}`}>{flash.msg}</div>}

        <div className="tabs">
          <button className={`tab-btn${tab === 'saved' ? ' active' : ''}`} onClick={() => setTab('saved')}>{t.saved}</button>
          <button className={`tab-btn${tab === 'new' ? ' active' : ''}`} onClick={() => setTab('new')}>{t.newRecipe}</button>
        </div>

        {/* TAB: Saved */}
        {tab === 'saved' && (
          <div>
            {compareIds.length > 0 && (
              <div style={{ marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.75rem' }}>
                  <h3 style={{ fontSize: '1rem' }}>📊 {t.comparison}</h3>
                  <button className="btn btn-sm" onClick={() => setCompareIds([])}>{t.clearCompare}</button>
                </div>
                <div className="compare-grid">
                  {compareIds.map(id => {
                    const cr = rezepte.find(r => r._rowIdx === id);
                    if (!cr) return null;
                    return (
                      <div key={id} className="compare-card">
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                          <strong style={{ fontSize: '0.9rem' }}>{String(cr.name)}</strong>
                          <button className="btn btn-sm" onClick={() => setCompareIds(ids => ids.filter(i => i !== id))}>✕</button>
                        </div>
                        {cr.bild_url && <img src={String(cr.bild_url)} alt={String(cr.name)} className="recipe-img" style={{ marginBottom: '0.5rem' }} />}
                        {[['filmSim','film_simulation'],['wb','weissabgleich'],['wbShift','wb_shift'],['dr','dynamikbereich'],['highlights','lichter'],['shadows','schatten'],['color','farbe'],['sharpness','schaerfe'],['nr','rauschreduzierung'],['grain','grain'],['toneCurve','tone_curve'],['colorChrome','color_chrome']].map(([lk, fk]) => (
                          <div key={fk} className="param"><strong>{t[lk as keyof typeof t] as string}: </strong>{String(cr[fk] || '-')}</div>
                        ))}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            <div className="top-bar">
              <span className="count-badge">{t.found(filtered.length)}</span>
            </div>

            {loadingData && <div className="empty-state"><div className="icon">⏳</div><p>{t.loading}</p></div>}
            {!loadingData && filtered.length === 0 && <div className="empty-state"><div className="icon">📁</div><p>{t.noRecipes}</p></div>}

            {filtered.map(r => {
              const isFav = String(r.favorit || '').toLowerCase() === 'ja';
              const isExpanded = expanded === r._rowIdx;
              const isEditing = editIdx === r._rowIdx;
              const tagsList = String(r.tags || '').split(',').map(t => t.trim()).filter(Boolean);

              return (
                <div key={r._rowIdx} className="card">
                  <div className="card-header" onClick={() => { setExpanded(isExpanded ? null : r._rowIdx); if (isEditing) { setEditIdx(null); setEditForm(null); } }}>
                    <div>
                      <span className="card-title">{isFav ? '⭐ ' : ''}{String(r.name || t.unknown)}</span>
                      <span className="card-meta"> &middot; {String(r.kategorie || '')} &middot; {String(r.film_simulation || '')}</span>
                    </div>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{isExpanded ? '▲' : '▼'}</span>
                  </div>

                  {isExpanded && (
                    <div className="card-body">
                      {isEditing && editForm ? (
                        <>
                          <RecipeForm f={editForm} setF={setEditForm} onSubmit={() => handleUpdate(r)} submitLabel={t.saveChanges} onCancel={() => { setEditIdx(null); setEditForm(null); }} />
                        </>
                      ) : (
                        <>
                          {r.bild_url ? (
                            <div className="with-image-layout">
                              <img src={String(r.bild_url)} alt={String(r.name)} className="recipe-img" loading="lazy" />
                              <RecipeParams r={r} t={t} />
                            </div>
                          ) : <RecipeParams r={r} t={t} />}
                          {tagsList.length > 0 && <div className="tags-row">{tagsList.map(tag => <span key={tag} className="tag">#{tag}</span>)}</div>}
                          {r.notizen && <div className="note-box">📝 {String(r.notizen)}</div>}
                          {r.datum && <div className="date-caption">{t.savedOn(String(r.datum))}</div>}

                          {deleteConfirm === r._rowIdx ? (
                            <div className="confirm-box">
                              <p style={{ marginBottom: '0.5rem', fontSize: '0.875rem' }}>{t.confirmDel(String(r.name))}</p>
                              <div className="btn-row">
                                <button className="btn btn-danger" onClick={() => handleDelete(r)}>{t.yesDel}</button>
                                <button className="btn" onClick={() => setDeleteConfirm(null)}>{t.cancel}</button>
                              </div>
                            </div>
                          ) : (
                            <div className="btn-row">
                              <button className="fav-btn" onClick={() => toggleFav(r)} title={t.favorite}>{isFav ? '⭐' : '☆'}</button>
                              <button className="btn btn-sm" onClick={() => startEdit(r)}>{t.edit}</button>
                              <button className="btn btn-sm btn-danger" onClick={() => setDeleteConfirm(r._rowIdx)}>{t.delete}</button>
                              <label className="compare-checkbox">
                                <input type="checkbox" checked={compareIds.includes(r._rowIdx)}
                                  onChange={e => {
                                    if (e.target.checked) {
                                      if (compareIds.length >= 3) { showFlash('warning', t.maxCompare); return; }
                                      setCompareIds(ids => [...ids, r._rowIdx]);
                                    } else setCompareIds(ids => ids.filter(i => i !== r._rowIdx));
                                  }} />
                                {t.compare}
                              </label>
                            </div>
                          )}
                        </>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* TAB: New Recipe */}
        {tab === 'new' && (
          <div>
            <div className="url-section">
              <h3 style={{ fontSize: '0.95rem', marginBottom: '0.5rem' }}>{t.urlImport}</h3>
              <div className="url-row">
                <input placeholder={t.sourcePh} value={scrapeUrl} onChange={e => setScrapeUrl(e.target.value)}
                  onKeyDown={e => { if (e.key === 'Enter') handleScrape(); }} />
                <button className="btn btn-primary" onClick={handleScrape} disabled={scraping}>{scraping ? '...' : t.urlBtn}</button>
              </div>
              {scrapeMsg && <div className={`alert alert-${scrapeMsg.type}`} style={{ marginTop: '0.5rem' }}>{scrapeMsg.msg}</div>}
              <p className="scraper-note">{t.scrapeNote}</p>
            </div>
            <h3 style={{ fontSize: '0.95rem', marginBottom: '1rem' }}>{t.recipeData}</h3>
            <RecipeForm f={form} setF={setForm} onSubmit={handleSave} submitLabel={t.save} />
          </div>
        )}
      </main>
    </div>
  );
}

function RecipeParams({ r, t }: { r: Rezept; t: typeof T['de'] }) {
  return (
    <div className="params-grid">
      <div className="param"><strong>{t.filmSim}: </strong>{String(r.film_simulation || '-')}</div>
      <div className="param"><strong>{t.wb}: </strong>{String(r.weissabgleich || '-')}</div>
      <div className="param"><strong>{t.wbShift}: </strong>{String(r.wb_shift || '-')}</div>
      <div className="param"><strong>{t.dr}: </strong>{String(r.dynamikbereich || '-')}</div>
      <div className="param"><strong>{t.highlights}: </strong>{String(r.lichter ?? '-')}</div>
      <div className="param"><strong>{t.shadows}: </strong>{String(r.schatten ?? '-')}</div>
      <div className="param"><strong>{t.color}: </strong>{String(r.farbe ?? '-')}</div>
      <div className="param"><strong>{t.sharpness}: </strong>{String(r.schaerfe ?? '-')}</div>
      <div className="param"><strong>{t.nr}: </strong>{String(r.rauschreduzierung ?? '-')}</div>
      <div className="param"><strong>{t.grain}: </strong>{String(r.grain || '-')}</div>
      <div className="param"><strong>{t.toneCurve}: </strong>{String(r.tone_curve || '-')}</div>
      <div className="param"><strong>{t.colorChrome}: </strong>{String(r.color_chrome || '-')}</div>
      {r.quelle && <div className="param" style={{ gridColumn: '1 / -1' }}><strong>{t.source}: </strong><a href={String(r.quelle)} target="_blank" rel="noopener noreferrer">{String(r.quelle)}</a></div>}
    </div>
  );
}
