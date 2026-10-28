import { CalendarClock, MessageSquareText, Trash2 } from 'lucide-react'
import { useEffect, useState } from 'react'
import { api } from '../services/api'

export default function SessionHistory() {
  const [sessions, setSessions] = useState([])

  useEffect(() => {
    api
      .getSessions()
      .then((payload) => setSessions(payload.sessions || []))
      .catch(() => setSessions([]))
  }, [])

  const handleDelete = async (sessionId) => {
    try {
      await api.deleteSession(sessionId)
      setSessions((prev) => prev.filter((s) => s.session_id !== sessionId))
    } catch {
      // Session may already be gone — remove from local state anyway
      setSessions((prev) => prev.filter((s) => s.session_id !== sessionId))
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
          Session history
        </p>
        <h1 className="mt-2 text-3xl font-bold text-slate-900">
          Recent shopping conversations
        </h1>

        <div className="mt-8 space-y-4">
          {sessions.length === 0 ? (
            <p className="text-sm text-slate-500">No saved sessions yet.</p>
          ) : (
            sessions.map((session) => (
              <article
                key={session.session_id}
                className="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-slate-50 p-4 sm:flex-row sm:items-center sm:justify-between"
              >
                <div className="min-w-0">
                  <div className="flex items-center gap-2 text-sm text-slate-500">
                    <CalendarClock className="h-4 w-4 flex-shrink-0" />
                    <span>{session.last_activity}</span>
                  </div>
                  <h2 className="mt-2 text-lg font-semibold text-slate-900">
                    {session.title || 'Shopping session'}
                  </h2>
                  <p className="mt-1 flex items-center gap-2 text-sm text-slate-600">
                    <MessageSquareText className="h-4 w-4 flex-shrink-0" />
                    <span className="truncate">
                      {session.query_preview || session.last_message || '—'}
                    </span>
                  </p>
                  {session.turn_number > 0 && (
                    <p className="mt-1 text-xs text-slate-400">
                      {session.turn_number} turn{session.turn_number !== 1 ? 's' : ''}
                    </p>
                  )}
                </div>
                <button
                  type="button"
                  onClick={() => handleDelete(session.session_id)}
                  className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:border-red-200 hover:text-red-600 flex-shrink-0"
                >
                  <Trash2 className="h-4 w-4" />
                  Delete
                </button>
              </article>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
