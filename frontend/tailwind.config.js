export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#071013",
        panel: "rgba(10, 20, 24, 0.78)",
        mint: "#54f0b2",
        cyan: "#66d9ef",
        amber: "#f2b84b",
        rose: "#f25f73"
      },
      boxShadow: {
        glow: "0 20px 60px rgba(84, 240, 178, 0.12)"
      }
    }
  },
  plugins: []
};

