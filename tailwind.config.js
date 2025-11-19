module.exports = {
  content: ["./index.html","./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        accent: "#2563EB", // blue accent for pro look
        panel: "rgba(255,255,255,0.03)"
      },
      boxShadow: {
        soft: '0 6px 30px rgba(2,6,23,0.45)',
        card: '0 8px 30px rgba(12,18,50,0.35)'
      }
    }
  },
  plugins: []
}
