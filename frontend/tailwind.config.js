/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        amber: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
          950: '#451a03',
        },
        zinc: {
          50: '#fafafa',
          100: '#f4f4f5',
          200: '#e4e4e7',
          300: '#d4d4d8',
          400: '#a1a1aa',
          500: '#71717a',
          600: '#52525b',
          700: '#3f3f46',
          800: '#27272a',
          900: '#18181b',
          950: '#09090b',
        },
      },
      animation: {
        'pulse-tactical': 'pulse-tactical 2s ease-in-out infinite',
        'shimmer-tactical': 'shimmer-tactical 2s ease-in-out infinite',
        'fade-in': 'fade-in 0.3s ease-out',
      },
      keyframes: {
        'pulse-tactical': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
        'shimmer-tactical': {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
        'fade-in': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      backgroundImage: {
        'carbon-fiber': `repeating-linear-gradient(45deg, transparent, transparent 2px, rgba(24, 24, 27, 0.4) 2px, rgba(24, 24, 27, 0.4) 4px), repeating-linear-gradient(-45deg, transparent, transparent 2px, rgba(24, 24, 27, 0.4) 2px, rgba(24, 24, 27, 0.4) 4px)`,
        'tactical-grid': `linear-gradient(rgba(24, 24, 27, 0.8) 1px, transparent 1px), linear-gradient(90deg, rgba(24, 24, 27, 0.8) 1px, transparent 1px)`,
      },
    },
  },
  plugins: [],
};
