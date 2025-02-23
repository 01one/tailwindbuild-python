/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      // Look in temp directory with specific build ID
      process.env.TEMP_BUILD_DIR + "/**/*.{html,js}",
      // Keep the templates directory for the upload interface
      "./templates/**/*.{html,js}"
    ],
    theme: {
      extend: {},
    },
    plugins: [],
  }