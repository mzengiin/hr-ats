/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#e8f2fe',
          100: '#d1e5fd',
          200: '#a2cbfb',
          300: '#74b1f9',
          400: '#4597f7',
          500: '#137fec',
          600: '#0f66bc',
          700: '#0b4d8d',
          800: '#08355d',
          900: '#041c2f',
        }
      },
      fontFamily: {
        'sans': ['Plus Jakarta Sans', 'Noto Sans', 'sans-serif'],
      }
    },
  },
  plugins: [],
}

