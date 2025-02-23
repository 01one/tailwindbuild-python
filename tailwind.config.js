/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      process.env.TEMP_BUILD_DIR + "/**/*.{html,js}",
      "./templates/**/*.{html,js}"
    ],
    theme: {
      extend: {},
    },
    plugins: [],
  }
