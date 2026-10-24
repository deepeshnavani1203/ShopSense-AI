import { useEffect, useMemo, useState } from 'react'
import { BrowserRouter, NavLink, Route, Routes } from 'react-router-dom'
import { Compass, Heart, History, Home, LayoutGrid, Sparkles } from 'lucide-react'
import HomePage from './pages/Home'
import DiscoverPage from './pages/Discover'
import ComparePage from './pages/Compare'
import PreferencesPage from './pages/Preferences'
import SessionHistoryPage from './pages/SessionHistory'
import NotFoundPage from './pages/NotFound'
import { api } from './services/api'

const navItems = [
  { to: '/', label: 'Home', icon: Home },
  { to: '/discover', label: 'Discover', icon: Compass },
  { to: '/compare', label: 'Compare', icon: LayoutGrid },
  { to: '/preferences', label: 'Preferences', icon: Heart },
  { to: '/history', label: 'History', icon: History },
]

function App() {
  const userId = useMemo(() => {
    const stored = localStorage.getItem('shopsense-user')
    if (stored) return stored
    const next = 'demo-user'
    localStorage.setItem('shopsense-user', next)
    return next
  }, [])

  const [savedProducts, setSavedProducts] = useState([])
  const [selectedCompare, setSelectedCompare] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('shopsense-compare') || '[]')
    } catch {
      return []
    }
  })

  useEffect(() => {
    localStorage.setItem('shopsense-compare', JSON.stringify(selectedCompare))
  }, [selectedCompare])

  useEffect(() => {
    api
      .getSavedProducts()
      .then((payload) => setSavedProducts(payload.items || []))
      .catch(() => setSavedProducts([]))
  }, [])

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[#f7f5f3] text-slate-800">
        <header className="border-b border-slate-200 bg-white/90 backdrop-blur-sm">
          <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-violet-600 text-white shadow-sm">
                <Sparkles className="h-5 w-5" />
              </div>
              <div>
                <p className="text-lg font-black tracking-tight text-slate-900">ShopSense AI</p>
              </div>
            </div>

            <nav className="hidden items-center gap-1 rounded-full border border-slate-200 bg-slate-50 p-1 md:flex">
              {navItems.map(({ to, label, icon: Icon }) => (
                <NavLink
                  key={to}
                  to={to}
                  className={({ isActive }) =>
                    `inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition ${
                      isActive ? 'bg-slate-900 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'
                    }`
                  }
                >
                  <Icon className="h-4 w-4" />
                  {label}
                </NavLink>
              ))}
            </nav>
          </div>
        </header>

        <main>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route
              path="/discover"
              element={
                <DiscoverPage
                  userId={userId}
                  selectedCompare={selectedCompare}
                  setSelectedCompare={setSelectedCompare}
                  savedProducts={savedProducts}
                  setSavedProducts={setSavedProducts}
                />
              }
            />
            <Route path="/compare" element={<ComparePage selectedCompare={selectedCompare} />} />
            <Route path="/preferences" element={<PreferencesPage userId={userId} />} />
            <Route path="/history" element={<SessionHistoryPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
