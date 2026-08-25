import { useEffect, useMemo, useRef, useState } from 'react'
import type { DragEvent, ReactNode } from 'react'
import {
  Bell,
  CheckCircle2,
  ChevronDown,
  Clock3,
  FileAudio,
  FileImage,
  FileText,
  Files,
  Gavel,
  Inbox,
  Landmark,
  Menu,
  Moon,
  MoreHorizontal,
  Plus,
  Search,
  ShieldCheck,
  Sun,
  UploadCloud,
  X,
} from 'lucide-react'
import { initialEvidence, timeline } from './data'
import type { EvidenceFile, EvidenceStatus } from './types'

type Theme = 'light' | 'dark'

const statusStyles: Record<EvidenceStatus, string> = {
  Verified: 'bg-teal-50 text-teal-700 ring-teal-600/20 dark:bg-teal-500/10 dark:text-teal-300 dark:ring-teal-400/30',
  Processing: 'bg-amber-50 text-amber-700 ring-amber-600/20 dark:bg-amber-500/10 dark:text-amber-300 dark:ring-amber-400/30',
  'Needs review': 'bg-rose-50 text-rose-700 ring-rose-600/20 dark:bg-rose-500/10 dark:text-rose-300 dark:ring-rose-400/30',
}

function iconForType(type: string) {
  if (type.includes('Audio')) return FileAudio
  if (type.includes('Image')) return FileImage
  if (type.includes('Archive')) return Files
  return FileText
}

function formatSize(bytes: number) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function typeLabel(file: File) {
  if (file.type.startsWith('audio/')) return 'Audio recording'
  if (file.type.startsWith('image/')) return 'Image evidence'
  if (file.type === 'application/pdf') return 'PDF document'
  if (file.type.includes('zip') || file.name.endsWith('.zip')) return 'Archive'
  return 'Evidence file'
}

export default function App() {
  const [theme, setTheme] = useState<Theme>(() => (localStorage.getItem('sakshya-theme') as Theme) || 'light')
  const [evidence, setEvidence] = useState<EvidenceFile[]>(initialEvidence)
  const [query, setQuery] = useState('')
  const [filter, setFilter] = useState<'All' | EvidenceStatus>('All')
  const [dragging, setDragging] = useState(false)
  const [toast, setToast] = useState<string | null>(null)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const fileInput = useRef<HTMLInputElement>(null)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
    localStorage.setItem('sakshya-theme', theme)
  }, [theme])

  useEffect(() => {
    if (!toast) return
    const timer = window.setTimeout(() => setToast(null), 3600)
    return () => window.clearTimeout(timer)
  }, [toast])

  const visibleEvidence = useMemo(() => evidence.filter((item) => {
    const matchesQuery = `${item.name} ${item.id} ${item.type}`.toLowerCase().includes(query.toLowerCase())
    return matchesQuery && (filter === 'All' || item.status === filter)
  }), [evidence, filter, query])

  // Frontend-only upload queue: once an intake API exists, replace this state update
  // with a multipart request to the hashing/intake service described in the README.
  function addFiles(files: FileList | File[]) {
    const additions = Array.from(files).map((file, index): EvidenceFile => ({
      id: `EV-${String(48 + evidence.length + index).padStart(3, '0')}`,
      name: file.name,
      type: typeLabel(file),
      size: formatSize(file.size),
      uploaded: 'Just now',
      status: 'Processing',
      hash: 'Awaiting intake…',
    }))
    if (!additions.length) return
    setEvidence((current) => [...additions, ...current])
    setToast(`${additions.length} file${additions.length > 1 ? 's' : ''} added to the frontend queue.`)
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault()
    setDragging(false)
    addFiles(event.dataTransfer.files)
  }

  return (
    <div className="min-h-screen bg-stone-50 text-slate-800 transition-colors dark:bg-slate-950 dark:text-slate-100">
      <header className="sticky top-0 z-30 border-b border-slate-200/80 bg-white/95 backdrop-blur dark:border-slate-800 dark:bg-slate-950/95">
        <div className="mx-auto flex h-[72px] max-w-[1440px] items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <button className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 lg:hidden dark:text-slate-300 dark:hover:bg-slate-800" onClick={() => setMobileMenuOpen(!mobileMenuOpen)} aria-label="Toggle navigation"><Menu size={21} /></button>
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-teal-700 text-white shadow-sm"><Landmark size={20} strokeWidth={2.2} /></div>
            <div><p className="font-serif text-xl font-bold tracking-tight text-slate-950 dark:text-white">Sakshya</p><p className="hidden text-[10px] font-semibold uppercase tracking-[0.17em] text-teal-700 sm:block dark:text-teal-400">Evidence intelligence</p></div>
          </div>
          <div className="hidden flex-1 px-10 lg:block"><label className="relative mx-auto block max-w-md"><Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={17} /><input value={query} onChange={(event) => setQuery(event.target.value)} className="w-full rounded-lg border border-slate-200 bg-slate-50 py-2 pl-9 pr-3 text-sm outline-none transition focus:border-teal-600 focus:ring-2 focus:ring-teal-600/15 dark:border-slate-700 dark:bg-slate-900" placeholder="Search evidence or case records" /></label></div>
          <div className="flex items-center gap-1 sm:gap-2"><button className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800" onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')} aria-label="Toggle light and dark mode">{theme === 'light' ? <Moon size={19} /> : <Sun size={19} />}</button><button className="relative rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800" aria-label="Notifications"><Bell size={19} /><span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-rose-500 ring-2 ring-white dark:ring-slate-950" /></button><div className="ml-1 hidden items-center gap-2 border-l border-slate-200 pl-3 sm:flex dark:border-slate-700"><div className="flex h-8 w-8 items-center justify-center rounded-full bg-teal-100 text-xs font-bold text-teal-800 dark:bg-teal-900 dark:text-teal-200">AR</div><ChevronDown size={16} className="text-slate-400" /></div></div>
        </div>
      </header>

      <div className="mx-auto flex max-w-[1440px]">
        <aside className={`${mobileMenuOpen ? 'absolute inset-x-0 top-[72px] z-20 block border-b shadow-lg' : 'hidden'} w-full bg-white px-4 py-4 lg:static lg:block lg:min-h-[calc(100vh-72px)] lg:w-60 lg:shrink-0 lg:border-r lg:border-slate-200 lg:px-5 lg:py-7 lg:shadow-none dark:border-slate-800 dark:bg-slate-950`}>
          <nav className="space-y-1 text-sm"><a className="flex items-center gap-3 rounded-lg bg-teal-50 px-3 py-2.5 font-semibold text-teal-800 dark:bg-teal-500/10 dark:text-teal-300" href="#overview"><Gavel size={18} />Case overview</a><a className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-900" href="#evidence"><Inbox size={18} />Evidence library <span className="ml-auto rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-500 dark:bg-slate-800">{evidence.length}</span></a><a className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-900" href="#timeline"><Clock3 size={18} />Case timeline</a><a className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-900" href="#precedent"><Files size={18} />Verified precedents</a></nav>
          <div className="mt-8 rounded-xl border border-teal-100 bg-teal-50/70 p-4 dark:border-teal-900/80 dark:bg-teal-950/40"><ShieldCheck size={20} className="text-teal-700 dark:text-teal-400" /><p className="mt-2 text-xs font-semibold text-slate-800 dark:text-slate-200">Chain of custody</p><p className="mt-1 text-xs leading-5 text-slate-500 dark:text-slate-400">Every uploaded item receives a fingerprint before processing.</p></div>
        </aside>

        <main className="min-w-0 flex-1 px-4 py-6 sm:px-6 lg:px-9 lg:py-8" id="overview">
          <section className="flex flex-col justify-between gap-5 md:flex-row md:items-end"><div><p className="text-xs font-semibold uppercase tracking-[0.16em] text-teal-700 dark:text-teal-400">Case dashboard</p><h1 className="mt-1 font-serif text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl dark:text-white">Rao vs. Khandelwal</h1><p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Civil property dispute <span className="mx-1.5 text-slate-300">/</span> Case no. CP-2026-1847</p></div><button onClick={() => fileInput.current?.click()} className="inline-flex items-center justify-center gap-2 rounded-lg bg-teal-700 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-teal-800 focus:outline-none focus:ring-2 focus:ring-teal-600 focus:ring-offset-2 dark:focus:ring-offset-slate-950"><Plus size={18} />Add evidence</button></section>

          <section className="mt-7 grid gap-4 sm:grid-cols-2 xl:grid-cols-4"><StatCard label="Evidence items" value={String(evidence.length).padStart(2, '0')} note="4 verified" icon={<Files size={19} />} /><StatCard label="Integrity status" value="Verified" note="Last checked 10:45" icon={<ShieldCheck size={19} />} verified /><StatCard label="Custody trail" value="Complete" note="No gaps detected" icon={<CheckCircle2 size={19} />} verified /><StatCard label="Next anchor" value="12 min" note="Merkle batch pending" icon={<Clock3 size={19} />} /></section>

          <section className="mt-7 grid gap-6 xl:grid-cols-[minmax(0,1.65fr)_minmax(300px,0.85fr)]">
            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-card dark:border-slate-800 dark:bg-slate-900 sm:p-6" id="evidence">
              <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center"><div><h2 className="font-serif text-xl font-bold text-slate-900 dark:text-white">Evidence library</h2><p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Files and their current chain-of-custody state.</p></div><div className="flex items-center gap-2"><div className="relative lg:hidden"><Search className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" size={16} /><input value={query} onChange={(event) => setQuery(event.target.value)} className="w-40 rounded-md border border-slate-200 bg-slate-50 py-1.5 pl-8 text-xs dark:border-slate-700 dark:bg-slate-950" placeholder="Search" /></div><select value={filter} onChange={(event) => setFilter(event.target.value as 'All' | EvidenceStatus)} className="rounded-md border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-600 outline-none focus:border-teal-600 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-300"><option>All</option><option>Verified</option><option>Processing</option><option>Needs review</option></select></div></div>
              <div className="mt-5 overflow-x-auto"><table className="w-full min-w-[570px] text-left"><thead><tr className="border-b border-slate-100 text-[10px] font-bold uppercase tracking-[0.12em] text-slate-400 dark:border-slate-800"><th className="pb-3 pl-2">Evidence</th><th className="pb-3">Fingerprint</th><th className="pb-3">Status</th><th className="pb-3">Uploaded</th><th className="pb-3" /></tr></thead><tbody>{visibleEvidence.map((item) => { const Icon = iconForType(item.type); return <tr key={item.id} className="border-b border-slate-100 last:border-0 dark:border-slate-800"><td className="py-3.5 pl-2"><div className="flex items-center gap-3"><div className="rounded-lg bg-slate-100 p-2 text-teal-700 dark:bg-slate-800 dark:text-teal-400"><Icon size={17} /></div><div><p className="max-w-[190px] truncate text-sm font-semibold text-slate-700 dark:text-slate-200">{item.name}</p><p className="mt-0.5 text-xs text-slate-400">{item.id} · {item.type} · {item.size}</p></div></div></td><td className="py-3.5 font-mono text-xs text-slate-500 dark:text-slate-400">{item.hash}</td><td className="py-3.5"><span className={`inline-flex rounded-full px-2.5 py-1 text-[11px] font-semibold ring-1 ring-inset ${statusStyles[item.status]}`}>{item.status}</span></td><td className="py-3.5 text-xs text-slate-500 dark:text-slate-400">{item.uploaded}</td><td className="py-3.5"><button aria-label={`More actions for ${item.name}`} className="rounded p-1 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"><MoreHorizontal size={18} /></button></td></tr>})}</tbody></table>{visibleEvidence.length === 0 && <p className="py-10 text-center text-sm text-slate-400">No evidence matches this view.</p>}</div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-card dark:border-slate-800 dark:bg-slate-900 sm:p-6"><div className="flex items-start justify-between"><div><h2 className="font-serif text-xl font-bold text-slate-900 dark:text-white">Integrity check</h2><p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Latest anchored evidence batch</p></div><span className="flex h-9 w-9 items-center justify-center rounded-full bg-teal-50 text-teal-700 dark:bg-teal-500/10 dark:text-teal-400"><ShieldCheck size={20} /></span></div><div className="mt-6 rounded-lg border border-teal-100 bg-teal-50/60 p-4 dark:border-teal-900/70 dark:bg-teal-950/30"><div className="flex items-center gap-2 text-sm font-semibold text-teal-800 dark:text-teal-300"><CheckCircle2 size={17} />Evidence is intact</div><p className="mt-2 text-xs leading-5 text-slate-600 dark:text-slate-400">The current Postgres record matches the Merkle root anchored at 10:30 today.</p></div><dl className="mt-5 space-y-3 text-sm"><DetailRow label="Batch reference" value="#MC-260824-14" mono /><DetailRow label="Anchored" value="24 Aug 2026, 10:30" /><DetailRow label="Items in batch" value="126 evidence events" /></dl><button onClick={() => setToast('Integrity verification is a backend action and will be available when the verification API is connected.')} className="mt-5 w-full rounded-lg border border-teal-700 px-3 py-2 text-sm font-semibold text-teal-700 transition hover:bg-teal-50 dark:border-teal-500 dark:text-teal-400 dark:hover:bg-teal-500/10">Request verification</button></div>
          </section>

          <section className="mt-7 grid gap-6 xl:grid-cols-[minmax(0,1.65fr)_minmax(300px,0.85fr)]">
            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-card dark:border-slate-800 dark:bg-slate-900 sm:p-6" id="timeline"><div className="flex items-center justify-between"><div><h2 className="font-serif text-xl font-bold text-slate-900 dark:text-white">Case timeline</h2><p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Events are assembled from verified custody data.</p></div><button className="text-xs font-semibold text-teal-700 hover:text-teal-900 dark:text-teal-400">View full timeline</button></div><div className="mt-6 space-y-0">{timeline.map((event, index) => <div className="relative flex gap-4 pb-6 last:pb-0" key={event.date}>{index < timeline.length - 1 && <span className="absolute left-[9px] top-5 h-[calc(100%-8px)] w-px bg-slate-200 dark:bg-slate-700" />}<span className={`relative mt-1.5 h-[9px] w-[9px] shrink-0 rounded-full ring-4 ${event.tone === 'teal' ? 'bg-teal-600 ring-teal-100 dark:ring-teal-900' : event.tone === 'amber' ? 'bg-amber-500 ring-amber-100 dark:ring-amber-900' : 'bg-slate-500 ring-slate-100 dark:ring-slate-800'}`} /><div><p className="text-[10px] font-bold tracking-[0.1em] text-slate-400">{event.date}</p><p className="mt-1 text-sm font-semibold text-slate-700 dark:text-slate-200">{event.title}</p><p className="mt-0.5 text-xs leading-5 text-slate-500 dark:text-slate-400">{event.detail}</p><p className="mt-1.5 text-[11px] font-medium text-teal-700 dark:text-teal-400">{event.actor}</p></div></div>)}</div></div>
            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-card dark:border-slate-800 dark:bg-slate-900" id="precedent"><p className="text-xs font-semibold uppercase tracking-[0.14em] text-teal-700 dark:text-teal-400">On-demand research</p><h2 className="mt-1 font-serif text-xl font-bold text-slate-900 dark:text-white">Verified precedents</h2><p className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-400">Find similar real judgments. Results are checked against the indexed corpus before they appear here.</p><div className="mt-5 rounded-lg border border-dashed border-slate-300 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-950/60"><Gavel size={20} className="text-slate-400" /><p className="mt-2 text-sm font-semibold text-slate-700 dark:text-slate-200">No research requested</p><p className="mt-1 text-xs leading-5 text-slate-500 dark:text-slate-400">Search is intentionally separate from any verdict prediction.</p></div><button onClick={() => setToast('Precedent search will be available when the precedent API is connected.')} className="mt-5 w-full rounded-lg bg-slate-900 px-3 py-2.5 text-sm font-semibold text-white hover:bg-slate-700 dark:bg-white dark:text-slate-900 dark:hover:bg-slate-200">Find verified precedents</button></div>
          </section>

          <section onClick={() => fileInput.current?.click()} onDragEnter={(event) => { event.preventDefault(); setDragging(true) }} onDragOver={(event) => event.preventDefault()} onDragLeave={() => setDragging(false)} onDrop={handleDrop} className={`mt-7 cursor-pointer rounded-xl border-2 border-dashed p-7 text-center transition sm:p-9 ${dragging ? 'border-teal-600 bg-teal-50 dark:bg-teal-950/30' : 'border-slate-200 bg-white hover:border-teal-400 hover:bg-teal-50/30 dark:border-slate-800 dark:bg-slate-900 dark:hover:border-teal-700'}`}><input ref={fileInput} onChange={(event) => { if (event.target.files) addFiles(event.target.files); event.target.value = '' }} type="file" multiple className="hidden" accept=".pdf,.png,.jpg,.jpeg,.zip,.mp3,.wav,.mp4" /><span className="mx-auto flex h-11 w-11 items-center justify-center rounded-full bg-teal-50 text-teal-700 dark:bg-teal-500/10 dark:text-teal-400"><UploadCloud size={22} /></span><p className="mt-3 text-sm font-semibold text-slate-700 dark:text-slate-200">Drop evidence here or <span className="text-teal-700 dark:text-teal-400">browse files</span></p><p className="mt-1 text-xs text-slate-500 dark:text-slate-400">PDF, images, audio, video, and archive files · Uploaded files stay in this browser until intake is connected.</p></section>
        </main>
      </div>
      {toast && <div role="status" className="fixed bottom-5 right-5 z-50 flex max-w-sm items-start gap-3 rounded-xl bg-slate-900 px-4 py-3 text-sm text-white shadow-xl dark:bg-white dark:text-slate-900"><CheckCircle2 size={18} className="mt-0.5 shrink-0 text-teal-400" /><span>{toast}</span><button onClick={() => setToast(null)} aria-label="Dismiss" className="ml-1 opacity-70 hover:opacity-100"><X size={16} /></button></div>}
    </div>
  )
}

function StatCard({ label, value, note, icon, verified = false }: { label: string; value: string; note: string; icon: ReactNode; verified?: boolean }) {
  return <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-card dark:border-slate-800 dark:bg-slate-900"><div className="flex items-start justify-between"><p className="text-xs font-semibold uppercase tracking-[0.1em] text-slate-400">{label}</p><span className={verified ? 'text-teal-700 dark:text-teal-400' : 'text-slate-400'}>{icon}</span></div><p className={`mt-3 font-serif text-2xl font-bold ${verified ? 'text-teal-700 dark:text-teal-400' : 'text-slate-800 dark:text-slate-100'}`}>{value}</p><p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{note}</p></div>
}

function DetailRow({ label, value, mono = false }: { label: string; value: string; mono?: boolean }) {
  return <div className="flex items-center justify-between gap-3"><dt className="text-xs text-slate-500 dark:text-slate-400">{label}</dt><dd className={`text-right text-xs font-semibold text-slate-700 dark:text-slate-200 ${mono ? 'font-mono' : ''}`}>{value}</dd></div>
}
