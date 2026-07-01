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

const FILM_SIM_MAP: Record<string, string> = {
  'provia': 'Provia/Standard',
  'standard': 'Provia/Standard',
  'velvia': 'Velvia/Vivid',
  'vivid': 'Velvia/Vivid',
  'astia': 'Astia/Soft',
  'soft': 'Astia/Soft',
  'classic chrome': 'Classic Chrome',
  'classic neg': 'Classic Neg.',
  'nostalgic neg': 'Nostalgic Neg.',
  'nostalgic neg.': 'Nostalgic Neg.',
  'pro neg. hi': 'PRO Neg. Hi',
  'pro neg. std': 'PRO Neg. Std',
  'pro neg hi': 'PRO Neg. Hi',
  'pro neg std': 'PRO Neg. Std',
  'pro neg': 'PRO Neg. Hi',
  'acros': 'Acros',
  'monochrome': 'Monochrome',
  'sepia': 'Sepia',
  'eterna bleach bypass': 'Eterna Bleach Bypass',
  'eterna cinema': 'Eterna/Cinema',
  'eterna': 'Eterna/Cinema',
  'reala ace': 'Reala Ace',
};

const FILM_SIM_KEYS = Object.keys(FILM_SIM_MAP).sort((a, b) => b.length - a.length);

function safeInt(val: string | undefined, fallback = 0): number {
  if (val === undefined) return fallback;
  const n = parseInt(val.replace('+', ''), 10);
  return isNaN(n) ? fallback : n;
}

export async function scrapeFujiXWeekly(url: string): Promise<{ data?: ScrapedData; error?: string }> {
  try {
    const res = await fetch(url, {
      headers: { 'User-Agent': 'Mozilla/5.0' },
      signal: AbortSignal.timeout(10000),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const html = await res.text();
    const data: ScrapedData = { quelle: url };

    // Title
    const titleMatch = html.match(/<title[^>]*>([^<]+)<\/title>/i);
    if (titleMatch) data.name = titleMatch[1].split('|')[0].trim();

    // OG image
    const ogImg = html.match(/<meta[^>]+property=["']og:image["'][^>]+content=["']([^"']+)["']/i)
      || html.match(/<meta[^>]+content=["']([^"']+)["'][^>]+property=["']og:image["']/i);
    if (ogImg) data.bild_url = ogImg[1];

    // Twitter image fallback
    if (!data.bild_url) {
      const twImg = html.match(/<meta[^>]+name=["']twitter:image["'][^>]+content=["']([^"']+)["']/i);
      if (twImg) data.bild_url = twImg[1];
    }

    // Parse <li> elements via regex
    const liMatches = [...html.matchAll(/<li[^>]*>(.*?)<\/li>/gis)];
    const liParsed: Partial<ScrapedData> = {};
    let liCount = 0;

    for (const m of liMatches) {
      const text = m[1].replace(/<[^>]+>/g, '').trim();
      if (!text.includes(':')) continue;
      const colonIdx = text.indexOf(':');
      const key = text.slice(0, colonIdx).trim().toLowerCase();
      const val = text.slice(colonIdx + 1).trim();

      if (key.includes('film simulation')) {
        const vl = val.toLowerCase();
        for (const k of FILM_SIM_KEYS) {
          if (vl.includes(k)) { liParsed.film_simulation = FILM_SIM_MAP[k]; liCount++; break; }
        }
      } else if (key.includes('dynamic range') || key === 'dr') {
        const drM = val.match(/DR?([0-9]+|auto)/i);
        if (drM) { liParsed.dynamikbereich = `DR${drM[1]}`; liCount++; }
      } else if (key.includes('white balance') && !key.includes('shift')) {
        liParsed.weissabgleich = val; liCount++;
        const shiftM = val.match(/R([+-]?\d+)[,\s]+B([+-]?\d+)/i);
        if (shiftM) liParsed.wb_shift = `R${shiftM[1]}, B${shiftM[2]}`;
      } else if (key.includes('wb shift') || key.includes('white balance shift')) {
        liParsed.wb_shift = val; liCount++;
      } else if (key.includes('highlight') || key.includes('lichter')) {
        const n = val.match(/([+-]?\d+)/);
        if (n) { liParsed.lichter = safeInt(n[1]); liCount++; }
      } else if (key.includes('shadow') || key.includes('schatten')) {
        const n = val.match(/([+-]?\d+)/);
        if (n) { liParsed.schatten = safeInt(n[1]); liCount++; }
      } else if ((key.includes('color') || key.includes('farbe')) && !key.includes('chrome')) {
        const n = val.match(/([+-]?\d+)/);
        if (n) { liParsed.farbe = safeInt(n[1]); liCount++; }
      } else if (key.includes('sharpness') || key.includes('schaerfe')) {
        const n = val.match(/([+-]?\d+)/);
        if (n) { liParsed.schaerfe = safeInt(n[1]); liCount++; }
      } else if (key.includes('noise reduction') || key.includes('rauschreduzierung')) {
        const n = val.match(/([+-]?\d+)/);
        if (n) { liParsed.rauschreduzierung = safeInt(n[1]); liCount++; }
      } else if (key.includes('grain')) {
        const vl = val.toLowerCase();
        for (const opt of ['weak', 'strong', 'off']) {
          if (vl.includes(opt)) { liParsed.grain = opt.charAt(0).toUpperCase() + opt.slice(1); liCount++; break; }
        }
      } else if (key.includes('chrome')) {
        const vl = val.toLowerCase();
        for (const opt of ['weak', 'strong', 'off']) {
          if (vl.includes(opt)) { liParsed.color_chrome = opt.charAt(0).toUpperCase() + opt.slice(1); liCount++; break; }
        }
      } else if (key.includes('tone curve')) {
        liParsed.tone_curve = val; liCount++;
      }
    }

    if (liCount >= 3) Object.assign(data, liParsed);

    return { data };
  } catch (e: unknown) {
    return { error: e instanceof Error ? e.message : String(e) };
  }
}
