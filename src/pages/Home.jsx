import { ArrowRight, Search, Sparkles, Wand2 } from 'lucide-react'
import { Link } from 'react-router-dom'

const prompts = [
  'Find comfortable walking shoes under ₹3,000.',
  'Gift for my dad who enjoys hiking.',
  'Compare lightweight laptops for college.',
]

export default function Home() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <section className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm sm:p-10">
        <div className="grid gap-10 lg:grid-cols-[1.15fr_0.85fr] lg:items-center">
          <div>
            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-violet-200 bg-violet-50 px-3 py-1 text-sm font-medium text-violet-700">
              <Sparkles className="h-4 w-4" />
              Conversational shopping assistant
            </div>
            <h1 className="max-w-xl text-4xl font-black tracking-tight text-slate-900 sm:text-5xl">
              Find the right product. Not just another product.
            </h1>
            <p className="mt-5 max-w-xl text-lg text-slate-600">
              ShopSense AI understands vague requests, surfaces clarifying questions when needed,
              compares real options, and explains why a product fits your budget and intent.
            </p>

            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <div className="flex w-full max-w-xl items-center gap-2 rounded-2xl border border-slate-200 bg-slate-50 p-2 shadow-sm">
                <Search className="ml-2 h-5 w-5 text-slate-400" />
                <input
                  readOnly
                  value="Find comfortable walking shoes under ₹3,000."
                  className="w-full border-0 bg-transparent text-sm text-slate-700 outline-none"
                />
              </div>
              <Link
                to="/discover"
                className="inline-flex items-center justify-center rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-700"
              >
                Start exploring
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </div>

            <div className="mt-6 flex flex-wrap gap-2">
              {prompts.map((prompt) => (
                <Link
                  key={prompt}
                  to="/discover"
                  className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-sm text-slate-700 transition hover:border-violet-200 hover:bg-violet-50 hover:text-violet-700"
                >
                  {prompt}
                </Link>
              ))}
            </div>
          </div>

          <div className="rounded-[1.75rem] border border-slate-200 bg-gradient-to-br from-violet-50 to-indigo-50 p-6">
            <div className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Discovery flow</p>
                  <h2 className="mt-2 text-xl font-bold text-slate-900">What ShopSense does</h2>
                </div>
                <Wand2 className="h-8 w-8 text-violet-600" />
              </div>
              <ol className="mt-5 space-y-4 text-sm text-slate-600">
                <li className="rounded-xl bg-slate-50 p-3">
                  <span className="font-semibold text-slate-900">1.</span> Understand your request and hidden preferences.
                </li>
                <li className="rounded-xl bg-slate-50 p-3">
                  <span className="font-semibold text-slate-900">2.</span> Filter catalogue with price, category, and intent.
                </li>
                <li className="rounded-xl bg-slate-50 p-3">
                  <span className="font-semibold text-slate-900">3.</span> Rank options with explicit fit scores and reasoning.
                </li>
              </ol>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
