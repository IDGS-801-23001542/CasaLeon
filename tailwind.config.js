module.exports = {
  content: [
    "./templates/**/*.{html,js}",
    "./static/**/*.{js}",
    "./node_modules/flowbite/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        cl: {
          white: "#FFFFFF",
          cream: "#F7F4EE",
          green: "#0E6B3B",
          green2: "#12824A",
          line: "#E6DDCF",
          brown: "#7A5C3E" // café mínimo (bordes/acento leve)
        }
      }
    }
  },
  plugins: [require("flowbite/plugin")]
};