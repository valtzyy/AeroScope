/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        aviation: {
          darker: "#030712",
          dark: "#0B1120",
          card: "#0F172A",
          border: "#1E293B",
          accent: "#06B6D4",
          accentGlow: "#0891B2",
          scheduled: "#F59E0B",
          active: "#10B981",
          landed: "#3B82F6",
          cancelled: "#EF4444",
        },
      },
    },
  },
  plugins: [],
};
