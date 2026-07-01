export type ScrapedData = {
  name?: string;
  film_simulation?: string;
  weissabgleich?: string;
  wb_shift?: string;
  dynamikbereich?: string;
  lichter?: number;
  schatten?: number;
  farbe?: number;
  schaerfe?: number;
  rauschreduzierung?: number;
  grain?: string;
  color_chrome?: string;
  tone_curve?: string;
  bild_url?: string;
  quelle?: string;
};

// Vollständige Film-Simulation-Map inkl. neuerer Fujifilm-Simulationen
// (X100V, X-T4, X-T5, X-S10, GFX etc.)
const FILM_SIM_MAP: Record<string, string> = {
  // Provia
  'provia/standard': 'Provia/Standard',
  'provia standard': 'Provia/Standard',
  'provia': 'Provia/Standard',
  'standard': 'Provia/Standard',

  // Velvia
  'velvia/vivid': 'Velvia/Vivid',
  'velvia vivid': 'Velvia/Vivid',
  'velvia': 'Velvia/Vivid',
  'vivid': 'Velvia/Vivid',

  // Astia
  'astia/soft': 'Astia/Soft',
  'astia soft': 'Astia/Soft',
  'astia': 'Astia/Soft',
  'soft': 'Astia/Soft',

  // Classic Chrome
  'classic chrome': 'Classic Chrome',

  // Classic Neg.
  'classic neg.': 'Classic Neg.',
  'classic neg': 'Classic Neg.',

  // Nostalgic Neg.
  'nostalgic neg.': 'Nostalgic Neg.',
  'nostalgic neg': 'Nostalgic Neg.',
  'nostalgic negative': 'Nostalgic Neg.',

  // Reala Ace (X100VI, X-T50 etc.)
  'reala ace': 'Reala Ace',
  'reala': 'Reala Ace',

  // PRO Neg.
  'pro neg. hi': 'PRO Neg. Hi',
  'pro neg. std': 'PRO Neg. Std',
  'pro neg hi': 'PRO Neg. Hi',
  'pro neg std': 'PRO Neg. Std',
  'pro neg': 'PRO Neg. Hi',

  // Acros variants
  'acros+ye': 'Acros+Ye',
  'acros+r': 'Acros+R',
  'acros+g': 'Acros+G',
  'acros ye': 'Acros+Ye',
  'acros r': 'Acros+R',
  'acros g': 'Acros+G',
  'acros': 'Acros',

  // Monochrome variants
  'monochrome+r': 'Monochrome+R',
  'monochrome+g': 'Monochrome+G',
  'monochrome+ye': 'Monochrome+Ye',
  'monochrome r': 'Monochrome+R',
  'monochrome g': 'Monochrome+G',
  'monochrome ye': 'Monochrome+Ye',
  'monochrome': 'Monochrome',
  'b&w': 'Monochrome',
  'b+w': 'Monochrome',

  // Sepia
  'sepia': 'Sepia',

  // Eterna
  'eterna/cinema': 'Eterna/Cinema',
  'eterna cinema': 'Eterna/Cinema',
  'eterna bleach bypass': 'Eterna Bleach Bypass',
  'bleach bypass': 'Eterna Bleach Bypass',
  'eterna': 'Eterna/Cinema',
};

// Schlüssel nach Länge absteigend sortieren → längster Match gewinnt
const FILM_SIM_KEYS = Object.keys(FILM_SIM_MAP).sort((a, b) => b.length - a.length);

/** Grain-Wert normalisieren */
const GRAIN_MAP: Record<string, string> = {
  'off': 'Off', 'none': 'Off', 'no': 'Off',
  'weak': 'Weak', 'light': 'Weak', 'small': 'Weak',
  'strong': 'Strong', 'heavy': 'Strong', 'large': 'Strong',
  'weak, large': 'Weak',
  'weak, small': 'Weak',
  'strong, large': 'Strong',
  'strong, small': 'Strong',
};

function normalizeGrain(val: string): string | undefined {
  const vl = val.toLowerCase().trim();
  // Direkter Match
  for (const [k, v] of Object.entries(GRAIN_MAP)) {
    if (vl.includes(k)) return v;
  }
  return undefined;
}

/** Color Chrome Wert normalisieren (inkl. FX-Variante) */
function normalizeColorChrome(val: string): string | undefined {
  const vl = val.toLowerCase().trim();
  if (vl.includes('strong')) return 'Strong';
  if (vl.includes('weak')) return 'Weak';
  if (vl.includes('off') || vl.includes('none') || vl.includes('no')) return 'Off';
  return undefined;
}

/** Dynamikbereich normalisieren */
function normalizeDR(val: string): string | undefined {
  const drM = val.match(/DR\s*([0-9]+)|(?:^|\s)([0-9]+)%|auto/i);
  if (!drM) return undefined;
  if (/auto/i.test(val)) return 'Auto';
  const num = drM[1] || drM[2];
  const n = parseInt(num, 10);
  if ([100, 200, 400].includes(n)) return `DR${n}`;
  return undefined;
}

/** Tone-Curve-Wert normalisieren */
const TONE_MAP: Record<string, string> = {
  'none': 'None',
  'linear': 'Linear',
  'medium soft': 'Medium Soft',
  'medium hard': 'Medium Hard',
  'strong': 'Strong',
};

function normalizeTone(val: string): string | undefined {
  const vl = val.toLowerCase().trim();
  for (const [k, v] of Object.entries(TONE_MAP)) {
    if (vl.includes(k)) return v;
  }
  return undefined;
}

/** Integer aus Fuji-Wert (+2, -1, 0 etc.) parsen */
function safeInt(val: string | undefined, fallback = 0): number {
  if (val === undefined) return fallback;
  const n = parseInt(val.replace('+', ''), 10);
  return isNaN(n) ? fallback : n;
}

/** Text aus einem HTML-Fragment extrahieren (Tags entfernen) */
function stripTags(html: string): string {
  return html.replace(/<[^>]+>/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&nbsp;/g, ' ').replace(/\s+/g, ' ').trim();
}

/** Alle Key-Value-Paare aus Listen- und Absatz-Elementen einer HTML-Seite extrahieren */
function extractKeyValues(html: string): { key: string; val: string }[] {
  const results: { key: string; val: string }[] = [];

  // Matcht <li>...</li>, <p>...</p> und <div>...</div>
  const pattern = /<(?:li|p|div)[^>]*>(.*?)<\/(?:li|p|div)>/gis;
  for (const m of html.matchAll(pattern)) {
    const text = stripTags(m[1]).trim();
    const colonIdx = text.indexOf(':');
    if (colonIdx < 1 || colonIdx > 60) continue; // Kein Key-Value oder Key zu lang
    const key = text.slice(0, colonIdx).trim().toLowerCase();
    const val = text.slice(colonIdx + 1).trim();
    if (key && val) results.push({ key, val });
  }
  return results;
}

export async function scrapeFujiXWeekly(url: string): Promise<{ data?: ScrapedData; error?: string }> {
  try {
    const res = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9',
      },
      signal: AbortSignal.timeout(12000),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const html = await res.text();
    const data: ScrapedData = { quelle: url };

    // ── Titel ───────────────────────────────────────────────────────
    const titleMatch = html.match(/<title[^>]*>([^<]+)<\/title>/i);
    if (titleMatch) {
      data.name = titleMatch[1]
        .split('|')[0]
        .split('–')[0]
        .split('—')[0]
        .replace(/fuji(film)?\s+x-?\w+/i, '')
        .trim();
    }

    // ── OG-Bild ─────────────────────────────────────────────────────
    const ogImg =
      html.match(/<meta[^>]+property=["']og:image["'][^>]+content=["']([^"']+)["']/i) ||
      html.match(/<meta[^>]+content=["']([^"']+)["'][^>]+property=["']og:image["']/i);
    if (ogImg) data.bild_url = ogImg[1];

    if (!data.bild_url) {
      const twImg = html.match(/<meta[^>]+name=["']twitter:image["'][^>]+content=["']([^"']+)["']/i);
      if (twImg) data.bild_url = twImg[1];
    }

    // ── Key-Value Parsing ───────────────────────────────────────────
    const pairs = extractKeyValues(html);
    const liParsed: Partial<ScrapedData> = {};
    let matchCount = 0;

    for (const { key, val } of pairs) {
      // Film Simulation
      if (key.includes('film simulation') || key.includes('film sim') || key === 'simulation') {
        const vl = val.toLowerCase();
        for (const k of FILM_SIM_KEYS) {
          if (vl.includes(k)) {
            liParsed.film_simulation = FILM_SIM_MAP[k];
            matchCount++;
            break;
          }
        }
      }

      // Dynamikbereich
      else if (key.includes('dynamic range') || key === 'dr' || key === 'dynamic range setting') {
        const dr = normalizeDR(val);
        if (dr) { liParsed.dynamikbereich = dr; matchCount++; }
      }

      // Weissabgleich
      else if ((key.includes('white balance') || key.includes('wb')) && !key.includes('shift') && !key.includes('compensation')) {
        liParsed.weissabgleich = val;
        matchCount++;
        // WB-Shift im selben Wert?
        const shiftM = val.match(/R([+-]?\d+)[,\s]+B([+-]?\d+)/i);
        if (shiftM) liParsed.wb_shift = `R${shiftM[1]}, B${shiftM[2]}`;
      }

      // WB-Shift
      else if (key.includes('wb shift') || key.includes('white balance shift') || key.includes('wb compensation')) {
        liParsed.wb_shift = val;
        matchCount++;
      }

      // Lichter / Highlights
      else if (key.includes('highlight') || key === 'lichter' || key === 'highlights') {
        const n = val.match(/([+-]?\d+)/);
        if (n) { liParsed.lichter = safeInt(n[1]); matchCount++; }
      }

      // Schatten / Shadows
      else if (key.includes('shadow') || key === 'schatten' || key === 'shadows') {
        const n = val.match(/([+-]?\d+)/);
        if (n) { liParsed.schatten = safeInt(n[1]); matchCount++; }
      }

      // Farbe / Color (nicht Color Chrome!)
      else if ((key === 'color' || key === 'colour' || key === 'farbe' || key.includes('color saturation')) && !key.includes('chrome') && !key.includes('fx')) {
        const n = val.match(/([+-]?\d+)/);
        if (n) { liParsed.farbe = safeInt(n[1]); matchCount++; }
      }

      // Schärfe / Sharpness
      else if (key.includes('sharpness') || key === 'schaerfe' || key === 'schärfe' || key === 'sharp') {
        const n = val.match(/([+-]?\d+)/);
        if (n) { liParsed.schaerfe = safeInt(n[1]); matchCount++; }
      }

      // Rauschreduzierung / Noise Reduction
      else if (key.includes('noise reduction') || key.includes('noise reduc') || key === 'nr' || key === 'rauschreduzierung') {
        const n = val.match(/([+-]?\d+)/);
        if (n) { liParsed.rauschreduzierung = safeInt(n[1]); matchCount++; }
      }

      // Grain
      else if (key.includes('grain') || key === 'grain effect') {
        const g = normalizeGrain(val);
        if (g) { liParsed.grain = g; matchCount++; }
      }

      // Color Chrome Effect (inkl. Color Chrome FX Blue)
      else if (key.includes('color chrome') && !key.includes('fx')) {
        const cc = normalizeColorChrome(val);
        if (cc) { liParsed.color_chrome = cc; matchCount++; }
      }

      // Tone Curve / Gradation
      else if (key.includes('tone curve') || key.includes('gradation') || key === 'tone') {
        const tc = normalizeTone(val);
        if (tc) { liParsed.tone_curve = tc; matchCount++; }
      }
    }

    // Mindestens 3 erkannte Felder → Daten übernehmen
    if (matchCount >= 3) Object.assign(data, liParsed);

    return { data };
  } catch (e: unknown) {
    return { error: e instanceof Error ? e.message : String(e) };
  }
}
