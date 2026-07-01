import { NextResponse } from 'next/server';
import { loadRezepte, saveRezept, updateRezept, deleteRezept } from '@/lib/sheets';

export async function GET() {
  try {
    const data = await loadRezepte();
    return NextResponse.json(data);
  } catch (e: unknown) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    await saveRezept(body);
    return NextResponse.json({ ok: true });
  } catch (e: unknown) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}

export async function PUT(req: Request) {
  try {
    const body = await req.json();
    const { _rowIdx, ...rezept } = body;
    await updateRezept(_rowIdx, rezept);
    return NextResponse.json({ ok: true });
  } catch (e: unknown) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}

export async function DELETE(req: Request) {
  try {
    const { rowIdx } = await req.json();
    await deleteRezept(rowIdx);
    return NextResponse.json({ ok: true });
  } catch (e: unknown) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}
