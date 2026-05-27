/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'voxie-pink': '#F48FB1',
        'voxie-brown': '#8D6E63',
      }
    },
  },
  plugins: [],
}