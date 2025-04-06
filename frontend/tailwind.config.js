/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      animation: {
        'gradient': 'gradient 15s ease infinite',
        'float': 'float 6s ease-in-out infinite',
        'pulse': 'pulse 4s ease-in-out infinite',
      },
      backgroundImage: {
        'cyber-gradient': 'linear-gradient(45deg, #7c3aed, #8b5cf6, #a78bfa)',
      },
    },
  },
  plugins: [],
}