import { NextResponse } from 'next/server';
import { scrapeFujiXWeekly } from '@/lib/scraper';

export async function POST(req: Request) {
  try {
    const { url } = await req.json();
    if (!url) return NextResponse.json({ error: 'No URL provided' }, { status: 400 });
    const result = await scrapeFujiXWeekly(url);
    return NextResponse.json(result);
  } catch (e: unknown) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}
