import './globals.css'

export const metadata = {
  title: 'Attribution Matrix',
  description: 'Behavioral Intelligence System - Markov-Shapley Hybrid Attribution',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-black font-mono">
        {children}
      </body>
    </html>
  )
}
