import type { VercelRequest, VercelResponse } from '@vercel/node';
import { google } from 'googleapis';

const SHEET_ID = process.env.GOOGLE_SHEET_ID!;
const SHEET_NAME = 'Rezepte';

async function getSheets() {
  const auth = new google.auth.GoogleAuth({
    credentials: JSON.parse(process.env.GOOGLE_SERVICE_ACCOUNT_JSON!),
    scopes: ['https://www.googleapis.com/auth/spreadsheets'],
  });
  return google.sheets({ version: 'v4', auth });
}

function rowToRezept(headers: string[], row: string[], index: number) {
  const obj: Record<string, string | number> = { id: index + 2 };
  headers.forEach((h, i) => {
    obj[h] = row[i] ?? '';
  });
  return obj;
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();

  try {
    const sheets = await getSheets();

    if (req.method === 'GET') {
      const response = await sheets.spreadsheets.values.get({
        spreadsheetId: SHEET_ID,
        range: `${SHEET_NAME}!A1:ZZ`,
      });
      const rows = response.data.values ?? [];
      if (rows.length < 2) return res.json([]);
      const headers = rows[0];
      const data = rows.slice(1).map((row, i) => rowToRezept(headers, row, i));
      return res.json(data);
    }

    if (req.method === 'POST') {
      const body = req.body;
      // Get headers first
      const headerRes = await sheets.spreadsheets.values.get({
        spreadsheetId: SHEET_ID,
        range: `${SHEET_NAME}!1:1`,
      });
      const headers = headerRes.data.values?.[0] ?? [];
      const row = headers.map((h: string) => body[h] ?? '');
      await sheets.spreadsheets.values.append({
        spreadsheetId: SHEET_ID,
        range: `${SHEET_NAME}!A1`,
        valueInputOption: 'USER_ENTERED',
        requestBody: { values: [row] },
      });
      return res.json({ success: true });
    }

    if (req.method === 'PUT') {
      const { id, ...body } = req.body;
      const headerRes = await sheets.spreadsheets.values.get({
        spreadsheetId: SHEET_ID,
        range: `${SHEET_NAME}!1:1`,
      });
      const headers = headerRes.data.values?.[0] ?? [];
      const row = headers.map((h: string) => body[h] ?? '');
      await sheets.spreadsheets.values.update({
        spreadsheetId: SHEET_ID,
        range: `${SHEET_NAME}!A${id}`,
        valueInputOption: 'USER_ENTERED',
        requestBody: { values: [row] },
      });
      return res.json({ success: true });
    }

    if (req.method === 'DELETE') {
      const rowIndex = parseInt(req.query.id as string);
      const sheetRes = await sheets.spreadsheets.get({ spreadsheetId: SHEET_ID });
      const sheet = sheetRes.data.sheets?.find(s => s.properties?.title === SHEET_NAME);
      const sheetId = sheet?.properties?.sheetId ?? 0;
      await sheets.spreadsheets.batchUpdate({
        spreadsheetId: SHEET_ID,
        requestBody: {
          requests: [{
            deleteDimension: {
              range: {
                sheetId,
                dimension: 'ROWS',
                startIndex: rowIndex - 1,
                endIndex: rowIndex,
              },
            },
          }],
        },
      });
      return res.json({ success: true });
    }

    return res.status(405).json({ error: 'Method not allowed' });
  } catch (err: unknown) {
    console.error(err);
    const message = err instanceof Error ? err.message : 'Unknown error';
    return res.status(500).json({ error: message });
  }
}
