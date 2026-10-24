import { useEffect, useState } from 'react'
import { Check, PencilLine, Trash2 } from 'lucide-react'
import { api } from '../services/api'

export default function Preferences({ userId }) {
  const [preferences, setPreferences] = useState({})
  const [draft, setDraft] = useState({ budget: '3000', brand: 'AeroStride' })

  useEffect(() => {
    api
      .getPreferences()
      .then((payload) => setPreferences(payload.preferences?.[userId] || {}))
      .catch(() => setPreferences({}))
  }, [userId])

  const handleSave = async () => {
    const next = { ...preferences, ...draft }
    const payload = await api.updatePreferences(userId, next)
    setPreferences(payload.preferences || next)
  }

  const handleDelete = async (key) => {
    const next = { ...preferences }
    delete next[key]
    setPreferences(next)
    await api.updatePreferences(userId, next)
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Preference memory</p>
        <h1 className="mt-2 text-3xl font-bold text-slate-900">Your saved shopping preferences</h1>

        <div className="mt-8 grid gap-5 md:grid-cols-3">
          <label className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
            Preferred budget
            <input
              value={draft.budget}
              onChange={(event) => setDraft((prev) => ({ ...prev, budget: event.target.value }))}
              className="mt-3 w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-slate-800 outline-none"
            />
          </label>
          <label className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
            Preferred brand
            <input
              value={draft.brand}
              onChange={(event) => setDraft((prev) => ({ ...prev, brand: event.target.value }))}
              className="mt-3 w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-slate-800 outline-none"
            />
          </label>
          <div className="flex items-end">
            <button
              type="button"
              onClick={handleSave}
              className="flex w-full items-center justify-center gap-2 rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-700"
            >
              <Check className="h-4 w-4" />
              Save preferences
            </button>
          </div>
        </div>

        <div className="mt-8 space-y-3">
          {Object.entries(preferences).length === 0 ? (
            <p className="text-sm text-slate-500">No stored preferences yet.</p>
          ) : (
            Object.entries(preferences).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm">
                <div>
                  <span className="font-medium text-slate-900">{key}</span>
                  <p className="text-slate-600">{String(value)}</p>
                </div>
                <button type="button" onClick={() => handleDelete(key)} className="rounded-full border border-slate-200 bg-white p-2 text-slate-500 hover:text-red-600">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
