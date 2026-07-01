import { google } from 'googleapis';

const SHEET_ID = process.env.GOOGLE_SHEET_ID!;
const SHEET_NAME = 'Tabellenblatt1';
const SCOPES = ['https://www.googleapis.com/auth/spreadsheets'];

const REQUIRED_HEADERS = [
  'name','kategorie','film_simulation','weissabgleich',
  'wb_shift','dynamikbereich','lichter','schatten',
  'farbe','schaerfe','rauschreduzierung','notizen',
  'quelle','datum','favorit','bild_url','grain',
  'tone_curve','color_chrome','tags'
];

export type Rezept = {
  [key: string]: string | number;
  _rowIdx: number;
};

function getAuth() {
  const creds = JSON.parse(process.env.GOOGLE_SERVICE_ACCOUNT_JSON!);
  return new google.auth.GoogleAuth({
    credentials: creds,
    scopes: SCOPES,
  });
}

async function getSheet() {
  const auth = getAuth();
  const sheets = google.sheets({ version: 'v4', auth });
  return sheets;
}

export async function loadRezepte(): Promise<Rezept[]> {
  const sheets = await getSheet();
  const res = await sheets.spreadsheets.values.get({
    spreadsheetId: SHEET_ID,
    range: SHEET_NAME,
  });
  const rows = res.data.values || [];
  if (rows.length < 2) return [];
  const headers = rows[0] as string[];
  return rows.slice(1).map((row, idx) => {
    const obj: Rezept = { _rowIdx: idx };
    headers.forEach((h, i) => { obj[h] = row[i] ?? ''; });
    return obj;
  });
}

export async function saveRezept(rezept: Record<string, string | number>): Promise<void> {
  const sheets = await getSheet();
  const res = await sheets.spreadsheets.values.get({
    spreadsheetId: SHEET_ID,
    range: `${SHEET_NAME}!1:1`,
  });
  let headers: string[] = (res.data.values?.[0] as string[]) || [];
  if (headers.length === 0) {
    headers = REQUIRED_HEADERS;
    await sheets.spreadsheets.values.update({
      spreadsheetId: SHEET_ID,
      range: `${SHEET_NAME}!A1`,
      valueInputOption: 'RAW',
      requestBody: { values: [headers] },
    });
  } else {
    const missing = REQUIRED_HEADERS.filter(h => !headers.includes(h));
    if (missing.length > 0) {
      const newHeaders = [...headers, ...missing];
      await sheets.spreadsheets.values.update({
        spreadsheetId: SHEET_ID,
        range: `${SHEET_NAME}!A1`,
        valueInputOption: 'RAW',
        requestBody: { values: [newHeaders] },
      });
      headers = newHeaders;
    }
  }
  const row = headers.map(h => String(rezept[h] ?? ''));
  await sheets.spreadsheets.values.append({
    spreadsheetId: SHEET_ID,
    range: SHEET_NAME,
    valueInputOption: 'RAW',
    requestBody: { values: [row] },
  });
}

export async function updateRezept(rowIdx: number, rezept: Record<string, string | number>): Promise<void> {
  const sheets = await getSheet();
  const res = await sheets.spreadsheets.values.get({
    spreadsheetId: SHEET_ID,
    range: `${SHEET_NAME}!1:1`,
  });
  const headers: string[] = (res.data.values?.[0] as string[]) || REQUIRED_HEADERS;
  const row = headers.map(h => String(rezept[h] ?? ''));
  await sheets.spreadsheets.values.update({
    spreadsheetId: SHEET_ID,
    range: `${SHEET_NAME}!A${rowIdx + 2}`,
    valueInputOption: 'RAW',
    requestBody: { values: [row] },
  });
}

export async function deleteRezept(rowIdx: number): Promise<void> {
  const sheets = await getSheet();
  const meta = await sheets.spreadsheets.get({ spreadsheetId: SHEET_ID });
  const sheetId = meta.data.sheets?.[0].properties?.sheetId ?? 0;
  await sheets.spreadsheets.batchUpdate({
    spreadsheetId: SHEET_ID,
    requestBody: {
      requests: [{
        deleteDimension: {
          range: {
            sheetId,
            dimension: 'ROWS',
            startIndex: rowIdx + 1,
            endIndex: rowIdx + 2,
          },
        },
      }],
    },
  });
}
