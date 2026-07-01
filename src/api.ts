const BASE = '/api/rezepte';

export async function fetchRezepte() {
  const res = await fetch(BASE);
  if (!res.ok) throw new Error('Fehler beim Laden der Rezepte');
  return res.json();
}

export async function createRezept(data: Record<string, unknown>) {
  const res = await fetch(BASE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Fehler beim Erstellen');
  return res.json();
}

export async function updateRezept(id: number, data: Record<string, unknown>) {
  const res = await fetch(BASE, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id, ...data }),
  });
  if (!res.ok) throw new Error('Fehler beim Aktualisieren');
  return res.json();
}

export async function deleteRezept(id: number) {
  const res = await fetch(`${BASE}?id=${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Fehler beim Löschen');
  return res.json();
}
