/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        aura: {
          purple: '#7c3aed',
          dark:   '#0f0f23',
          card:   '#1a1a2e',
          border: '#2a2a4a',
        }
      },
      animation: {
        'fade-in':  'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.4s ease-out',
      },
      keyframes: {
        fadeIn:  { from: { opacity: 0 }, to: { opacity: 1 } },
        slideUp: { from: { transform: 'translateY(10px)', opacity: 0 },
                   to:   { transform: 'translateY(0)',    opacity: 1 } },
      }
    }
  },
  plugins: []
}
