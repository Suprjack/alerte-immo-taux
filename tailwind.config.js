/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'insider-yellow': '#FFD700',
        'insider-dark': '#1a1a2e',
        'insider-red': '#e63946',
        'insider-green': '#2a9d8f'
      },
      fontFamily: {
        'headline': ['Georgia', 'serif'],
        'body': ['Inter', 'sans-serif']
      }
    },
  },
  plugins: [],
}

