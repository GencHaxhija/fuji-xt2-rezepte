import { useState, useEffect } from 'react'
import { collection, getDocs, addDoc, deleteDoc, doc, updateDoc, query, orderBy } from 'firebase/firestore'
import { db } from './firebase'
import { Recipe } from './types'

const FILM_SIM_OPTIONS = [
  'Provia/Standard', 'Velvia/Vivid', 'Astia/Soft',
  'Classic Chrome', 'Classic Neg.', 'PRO Neg. Hi', 'PRO Neg. Std',
  'Acros', 'Acros+R', 'Acros+G', 'Acros+Ye',
  'Monochrome', 'Monochrome+R', 'Monochrome+G', 'Monochrome+Ye',
  'Nostalgic Neg.', 'Eterna/Cinema', 'Eterna Bleach Bypass', 'Reala Ace', 'Sepia',
]

const CATEGORY_OPTIONS = ['Architektur', 'Porträt', 'Street', 'Reise', 'Landschaft', 'Allgemein']

const EMPTY_RECIPE: Omit<Recipe, 'id'> = {
  name: '', kategorie: 'Allgemein', film_simulation: 'Provia/Standard',
  weissabgleich: '', wb_shift: '', dynamikbereich: 'DR100',
  lichter: 0, schatten: 0, farbe: 0, schaerfe: 0, rauschreduzierung: 0,
  grain: 'Off', tone_curve: 'None', color_chrome: 'Off',
  bild_url: '', tags: '', notizen: '', quelle: '',
  favorit: false, datum: ''
}

export default function App() {
  const [recipes, setRecipes] = useState<Recipe[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState<'list' | 'new'>('list')
  const [form, setForm] = useState<Omit<Recipe, 'id'>>(EMPTY_RECIPE)
  const [saving, setSaving] = useState(false)
  const [search, setSearch] = useState('')
  const [filterKat, setFilterKat] = useState<string[]>(CATEGORY_OPTIONS)
  const [onlyFavs, setOnlyFavs] = useState(false)
  const [editId, setEditId] = useState<string | null>(null)

  const loadRecipes = async () => {
    try {
      setLoading(true)
      const q = query(collection(db, 'rezepte'), orderBy('datum', 'desc'))
      const snap = await getDocs(q)
      setRecipes(snap.docs.map(d => ({ id: d.id, ...d.data() } as Recipe)))
    } catch (e: unknown) {
      setError('Fehler beim Laden: ' + (e instanceof Error ? e.message : String(e)))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadRecipes() }, [])

  const handleSave = async () => {
    if (!form.name.trim()) return alert('Bitte Rezeptname eingeben!')
    setSaving(true)
    try {
      const data = { ...form, datum: new Date().toLocaleString('de-CH') }
      if (editId) {
        await updateDoc(doc(db, 'rezepte', editId), data)
        setEditId(null)
      } else {
        await addDoc(collection(db, 'rezepte'), data)
      }
      setForm(EMPTY_RECIPE)
      setActiveTab('list')
      await loadRecipes()
    } catch (e: unknown) {
      alert('Fehler beim Speichern: ' + (e instanceof Error ? e.message : String(e)))
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Rezept wirklich löschen?')) return
    await deleteDoc(doc(db, 'rezepte', id))
    await loadRecipes()
  }

  const handleEdit = (r: Recipe) => {
    setForm({ ...r })
    setEditId(r.id!)
    setActiveTab('new')
  }

  const handleFav = async (r: Recipe) => {
    await updateDoc(doc(db, 'rezepte', r.id!), { favorit: !r.favorit })
    await loadRecipes()
  }

  const filtered = recipes.filter(r =>
    (filterKat.length === 0 || filterKat.includes(r.kategorie)) &&
    (!onlyFavs || r.favorit) &&
    (!search || r.name.toLowerCase().includes(search.toLowerCase()) ||
      r.notizen?.toLowerCase().includes(search.toLowerCase()))
  )

  const sliderField = (label: string, key: keyof Recipe, min: number, max: number) => (
    <div style={{ marginBottom: 12 }}>
      <label style={{ fontSize: 13, color: 'var(--color-text-muted)', display: 'flex', justifyContent: 'space-between' }}>
        <span>{label}</span><span style={{ color: 'var(--color-primary)' }}>{form[key] as number}</span>
      </label>
      <input type="range" min={min} max={max} value={form[key] as number}
        onChange={e => setForm(f => ({ ...f, [key]: parseInt(e.target.value) }))}
        style={{ width: '100%', accentColor: 'var(--color-primary)' }} />
    </div>
  )

  const selectField = (label: string, key: keyof Recipe, options: string[]) => (
    <div style={{ marginBottom: 12 }}>
      <label style={{ fontSize: 13, color: 'var(--color-text-muted)', display: 'block', marginBottom: 4 }}>{label}</label>
      <select value={form[key] as string} onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
        style={{ width: '100%', padding: '8px 10px', background: 'var(--color-surface-2)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)', color: 'var(--color-text)', fontSize: 14 }}>
        {options.map(o => <option key={o} value={o}>{o}</option>)}
      </select>
    </div>
  )

  const inputField = (label: string, key: keyof Recipe, placeholder = '') => (
    <div style={{ marginBottom: 12 }}>
      <label style={{ fontSize: 13, color: 'var(--color-text-muted)', display: 'block', marginBottom: 4 }}>{label}</label>
      <input value={form[key] as string} onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
        placeholder={placeholder}
        style={{ width: '100%', padding: '8px 10px', background: 'var(--color-surface-2)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)', color: 'var(--color-text)', fontSize: 14 }} />
    </div>
  )

  return (
    <div style={{ maxWidth: 960, margin: '0 auto', padding: '24px 16px' }}>
      {/* Header */}
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 28, fontWeight: 700, letterSpacing: '-0.5px' }}>📷 Fuji X-T2 Rezepte</h1>
        <p style={{ color: 'var(--color-text-muted)', fontSize: 14, marginTop: 4 }}>Persönliche Film Simulation Datenbank</p>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 24, borderBottom: '1px solid var(--color-border)', paddingBottom: 0 }}>
        {(['list', 'new'] as const).map(tab => (
          <button key={tab} onClick={() => { setActiveTab(tab); if (tab === 'list') { setEditId(null); setForm(EMPTY_RECIPE) } }}
            style={{ padding: '10px 20px', borderRadius: 'var(--radius-sm) var(--radius-sm) 0 0', background: activeTab === tab ? 'var(--color-surface)' : 'transparent',
              color: activeTab === tab ? 'var(--color-primary)' : 'var(--color-text-muted)', fontWeight: activeTab === tab ? 600 : 400,
              borderBottom: activeTab === tab ? '2px solid var(--color-primary)' : '2px solid transparent', fontSize: 14, transition: 'all 0.15s' }}>
            {tab === 'list' ? `Rezepte (${filtered.length})` : editId ? '✏️ Bearbeiten' : '+ Neues Rezept'}
          </button>
        ))}
      </div>

      {/* TAB: List */}
      {activeTab === 'list' && (
        <div>
          {/* Filters */}
          <div style={{ display: 'flex', gap: 12, marginBottom: 20, flexWrap: 'wrap', alignItems: 'center' }}>
            <input value={search} onChange={e => setSearch(e.target.value)} placeholder="🔍 Suchen..."
              style={{ flex: 1, minWidth: 200, padding: '8px 12px', background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', color: 'var(--color-text)', fontSize: 14 }} />
            <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 14, color: 'var(--color-text-muted)', cursor: 'pointer' }}>
              <input type="checkbox" checked={onlyFavs} onChange={e => setOnlyFavs(e.target.checked)} style={{ accentColor: 'var(--color-primary)' }} />
              Nur Favoriten
            </label>
          </div>

          {loading && <p style={{ color: 'var(--color-text-muted)', textAlign: 'center', padding: 40 }}>Laden...</p>}
          {error && <p style={{ color: '#e05' }}>{error}</p>}

          {!loading && filtered.length === 0 && (
            <div style={{ textAlign: 'center', padding: 60, color: 'var(--color-text-muted)' }}>
              <div style={{ fontSize: 40, marginBottom: 12 }}>🎞️</div>
              <p>Noch keine Rezepte. Füge dein erstes hinzu!</p>
            </div>
          )}

          <div style={{ display: 'grid', gap: 12 }}>
            {filtered.map(r => (
              <div key={r.id} style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}>
                <div style={{ display: 'flex', gap: 0 }}>
                  {r.bild_url && (
                    <img src={r.bild_url} alt={r.name} style={{ width: 120, height: 120, objectFit: 'cover', flexShrink: 0 }} />
                  )}
                  <div style={{ padding: '14px 16px', flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 8 }}>
                      <div>
                        <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 2 }}>{r.favorit ? '⭐ ' : ''}{r.name}</h3>
                        <p style={{ fontSize: 13, color: 'var(--color-text-muted)' }}>{r.kategorie} · {r.film_simulation}</p>
                      </div>
                      <div style={{ display: 'flex', gap: 6, flexShrink: 0 }}>
                        <button onClick={() => handleFav(r)} title="Favorit" style={{ fontSize: 16, opacity: r.favorit ? 1 : 0.4 }}>⭐</button>
                        <button onClick={() => handleEdit(r)} style={{ fontSize: 12, padding: '4px 10px', background: 'var(--color-surface-2)', borderRadius: 'var(--radius-sm)', color: 'var(--color-text-muted)' }}>✏️</button>
                        <button onClick={() => handleDelete(r.id!)} style={{ fontSize: 12, padding: '4px 10px', background: 'var(--color-surface-2)', borderRadius: 'var(--radius-sm)', color: '#e05' }}>🗑️</button>
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: 16, marginTop: 10, flexWrap: 'wrap' }}>
                      {[['Lichter', r.lichter], ['Schatten', r.schatten], ['Farbe', r.farbe], ['Schärfe', r.schaerfe], ['NR', r.rauschreduzierung]].map(([label, val]) => (
                        <span key={label as string} style={{ fontSize: 12, color: 'var(--color-text-muted)' }}>
                          <span style={{ color: 'var(--color-text)' }}>{label}</span> {(val as number) > 0 ? '+' : ''}{val}
                        </span>
                      ))}
                      {r.dynamikbereich && <span style={{ fontSize: 12, color: 'var(--color-primary)' }}>{r.dynamikbereich}</span>}
                    </div>
                    {r.tags && (
                      <div style={{ marginTop: 8, display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                        {r.tags.split(',').map(t => t.trim()).filter(Boolean).map(tag => (
                          <span key={tag} style={{ fontSize: 11, padding: '2px 8px', background: 'var(--color-surface-2)', borderRadius: 'var(--radius-sm)', color: 'var(--color-text-muted)' }}>#{tag}</span>
                        ))}
                      </div>
                    )}
                    {r.notizen && <p style={{ fontSize: 13, color: 'var(--color-text-muted)', marginTop: 6, fontStyle: 'italic' }}>📝 {r.notizen}</p>}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB: New / Edit */}
      {activeTab === 'new' && (
        <div style={{ maxWidth: 720 }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div>
              {inputField('Rezeptname *', 'name', 'z.B. Mein Classic Chrome Look')}
              {selectField('Kategorie', 'kategorie', CATEGORY_OPTIONS)}
              {selectField('Film Simulation', 'film_simulation', FILM_SIM_OPTIONS)}
              {inputField('Weissabgleich', 'weissabgleich', 'z.B. Tageslicht oder 5200K')}
              {inputField('WB Shift (R/B)', 'wb_shift', 'z.B. R+3, B-2')}
              {selectField('Dynamikbereich', 'dynamikbereich', ['DR100', 'DR200', 'DR400', 'Auto'])}
              {selectField('Körnung', 'grain', ['Off', 'Weak', 'Strong'])}
              {selectField('Gradationskurve', 'tone_curve', ['None', 'Linear', 'Medium Soft', 'Medium Hard', 'Strong'])}
              {selectField('Color Chrome Effekt', 'color_chrome', ['Off', 'Weak', 'Strong'])}
            </div>
            <div>
              {sliderField('Lichter', 'lichter', -2, 4)}
              {sliderField('Schatten', 'schatten', -2, 4)}
              {sliderField('Farbe', 'farbe', -4, 4)}
              {sliderField('Schärfe', 'schaerfe', -4, 4)}
              {sliderField('Rauschreduzierung', 'rauschreduzierung', -4, 4)}
              {inputField('Bild-URL', 'bild_url', 'https://example.com/bild.jpg')}
              {inputField('Tags', 'tags', 'z.B. sonnig, reise, kontrast')}
              {inputField('Quelle (URL)', 'quelle', 'https://fujixweekly.com/...')}
            </div>
          </div>
          <div style={{ marginBottom: 16 }}>
            <label style={{ fontSize: 13, color: 'var(--color-text-muted)', display: 'block', marginBottom: 4 }}>Notizen</label>
            <textarea value={form.notizen} onChange={e => setForm(f => ({ ...f, notizen: e.target.value }))}
              placeholder="z.B. Ideal für goldene Stunde"
              rows={3} style={{ width: '100%', padding: '8px 10px', background: 'var(--color-surface-2)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)', color: 'var(--color-text)', fontSize: 14, resize: 'vertical' }} />
          </div>
          <div style={{ display: 'flex', gap: 10 }}>
            <button onClick={handleSave} disabled={saving}
              style={{ padding: '10px 28px', background: 'var(--color-primary)', color: '#000', borderRadius: 'var(--radius-md)', fontWeight: 600, fontSize: 15, opacity: saving ? 0.6 : 1 }}>
              {saving ? 'Speichert...' : editId ? 'Änderungen speichern' : 'Rezept speichern'}
            </button>
            <button onClick={() => { setEditId(null); setForm(EMPTY_RECIPE); setActiveTab('list') }}
              style={{ padding: '10px 20px', background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', color: 'var(--color-text-muted)', fontSize: 15 }}>
              Abbrechen
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
