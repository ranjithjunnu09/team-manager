/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
      },
      colors: {
        bg:        '#F8F9FA',
        surface:   '#FFFFFF',
        border:    '#E2E8F0',
        accent:    '#2563EB',
        'accent-hover': '#1D4ED8',
        success:   '#16A34A',
        warning:   '#D97706',
        danger:    '#DC2626',
        primary:   '#0F172A',
        secondary: '#475569',
        muted:     '#94A3B8',
      },
      borderRadius: {
        DEFAULT: '6px',
        md: '8px',
      },
    },
  },
  plugins: [],
}