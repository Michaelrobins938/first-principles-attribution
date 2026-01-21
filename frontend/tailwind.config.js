/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        amber: { 500: '#f59e0b' },
        zinc: { 800: '#27272a', 900: '#18181b', 950: '#09090b' }
      },
      fontFamily: { mono: ['ui-monospace', 'SFMono-Regular'] }
    },
  },
  plugins: [],
};
