import { useEffect, useMemo, useState } from 'react'
import { BrowserRouter, NavLink, Route, Routes } from 'react-router-dom'
import {
  Bookmark,
  Compass,
  Heart,
  History,
  Home,
  LayoutGrid,
  ShoppingBag,
  Sparkles,
  Swords,
} from 'lucide-react'
import HomePage from './pages/Home'
import DiscoverPage from './pages/Discover'
import ComparePage from './pages/Compare'
import PreferencesPage from './pages/Preferences'
import SessionHistoryPage from './pages/SessionHistory'
import SavedProductsPage from './pages/SavedProducts'
import NotFoundPage from './pages/NotFound'
import { api } from './services/api'
import { CartProvider, useCart } from './context/CartContext'
import SmartCartDrawer from './components/SmartCartDrawer'
import RazorpayModal from './components/RazorpayModal'
import ProductBattleModal from './components/ProductBattleModal'

const navItems = [
  { to: '/', label: 'Home', icon: Home },
  { to: '/discover', label: 'Discover', icon: Compass },
  { to: '/compare', label: 'Compare', icon: LayoutGrid },
  { to: '/saved', label: 'Saved', icon: Bookmark },
  { to: '/preferences', label: 'Preferences', icon: Heart },
  { to: '/history', label: 'History', icon: History },
]

function Header({ selectedCompare, savedProducts }) {
  const { totalItemsCount, subtotal, setIsCartOpen } = useCart()

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur-sm shadow-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        <a href="/" className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-2xl bg-violet-600 text-white shadow-sm">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <p className="text-base font-black tracking-tight text-slate-900 leading-none">ShopSense AI</p>
            <span className="text-[10px] font-semibold text-violet-600 tracking-wider">SMART SHOPPING</span>
          </div>
        </a>

        {/* Desktop Nav */}
        <nav className="hidden items-center gap-1 rounded-full border border-slate-200 bg-slate-50 p-1 md:flex">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-semibold transition ${
                  isActive ? 'bg-slate-900 text-white shadow-sm' : 'text-slate-500 hover:text-slate-900'
                }`
              }
            >
              <Icon className="h-3.5 w-3.5" />
              {label}
              {label === 'Compare' && selectedCompare.length > 0 && (
                <span className="rounded-full bg-violet-500 px-1.5 py-0.5 text-[10px] font-bold text-white leading-none">
                  {selectedCompare.length}
                </span>
              )}
              {label === 'Saved' && savedProducts.length > 0 && (
                <span className="rounded-full bg-emerald-500 px-1.5 py-0.5 text-[10px] font-bold text-white leading-none">
                  {savedProducts.length}
                </span>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Right Action: Smart Cart Button */}
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setIsCartOpen(true)}
            className="inline-flex items-center gap-2 rounded-full bg-slate-900 px-3.5 py-1.5 text-xs font-bold text-white hover:bg-slate-800 transition shadow-sm"
          >
            <div className="relative">
              <ShoppingBag className="h-3.5 w-3.5" />
              {totalItemsCount > 0 && (
                <span className="absolute -top-1.5 -right-2 flex h-4 w-4 items-center justify-center rounded-full bg-violet-500 text-[9px] font-black text-white">
                  {totalItemsCount}
                </span>
              )}
            </div>
            <span>Cart</span>
            {subtotal > 0 && (
              <span className="rounded-full bg-white/20 px-1.5 py-0.5 text-[10px] font-bold">
                ₹{subtotal.toLocaleString('en-IN')}
              </span>
            )}
          </button>
        </div>
      </div>
    </header>
  )
}

function MainApp() {
  const userId = useMemo(() => {
    const stored = localStorage.getItem('shopsense-user')
    if (stored) return stored
    localStorage.setItem('shopsense-user', 'demo-user')
    return 'demo-user'
  }, [])

  const [savedProducts, setSavedProducts] = useState([])
  const [selectedCompare, setSelectedCompare] = useState(() => {
    try {
      const stored = JSON.parse(localStorage.getItem('shopsense-compare') || '[]')
      return stored.map(item => (typeof item === 'string' ? { product_id: item } : item))
    } catch {
      return []
    }
  })

  useEffect(() => {
    localStorage.setItem('shopsense-compare', JSON.stringify(selectedCompare))
  }, [selectedCompare])

  useEffect(() => {
    api.getSavedProducts()
      .then(p => setSavedProducts(p.items || []))
      .catch(() => setSavedProducts([]))
  }, [])

  return (
    <div className="min-h-screen bg-[#f7f5f3] text-slate-800">
      <Header selectedCompare={selectedCompare} savedProducts={savedProducts} />

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
          <Route
            path="/compare"
            element={
              <ComparePage selectedCompare={selectedCompare} setSelectedCompare={setSelectedCompare} />
            }
          />
          <Route path="/saved" element={<SavedProductsPage />} />
          <Route path="/preferences" element={<PreferencesPage userId={userId} />} />
          <Route path="/history" element={<SessionHistoryPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </main>

      {/* Global Drawers & Modals */}
      <SmartCartDrawer />
      <RazorpayModal />
      <ProductBattleModal />
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <CartProvider>
        <MainApp />
      </CartProvider>
    </BrowserRouter>
  )
}

export default App
