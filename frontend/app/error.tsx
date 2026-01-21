'use client'

export default function Error({ reset }: { reset: () => void }) {
  return (
    <div className="min-h-screen bg-black text-white p-8 font-mono">
      <h1 className="text-2xl text-red-500 mb-4">ERROR</h1>
      <p className="text-zinc-400 mb-4">Something went wrong.</p>
      <button 
        onClick={reset}
        className="px-4 py-2 bg-zinc-800 border border-zinc-700 hover:border-amber-500 text-amber-500"
      >
        Retry
      </button>
    </div>
  )
}
