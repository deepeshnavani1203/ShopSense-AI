import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="mx-auto max-w-xl px-4 py-16 text-center">
      <p className="text-xs font-semibold uppercase tracking-[0.25em] text-violet-600">404</p>
      <h1 className="mt-4 text-4xl font-bold text-slate-900">Page not found</h1>
      <p className="mt-4 text-slate-600">The page you tried to view does not exist in the ShopSense experience.</p>
      <Link to="/" className="mt-8 inline-flex rounded-full bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-700">
        Return home
      </Link>
    </div>
  )
}
