/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#334155', // slate-700
          light: '#475569',   // slate-600
          dark: '#1e293b',    // slate-800
        },
        secondary: {
          DEFAULT: '#4B5563', // gray-600
          light: '#6B7280',   // gray-500
          dark: '#374151',    // gray-700
        },
        accent: {
          DEFAULT: '#2563EB', // blue-600
          light: '#3B82F6',   // blue-500
          dark: '#1D4ED8',    // blue-700
        },
      },
    },
  },
  plugins: [],
}
