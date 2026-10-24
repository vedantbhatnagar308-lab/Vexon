import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        discord: {
          blurple: "#5865F2",
          dark: "#23272A",
          darker: "#1E1F22",
          panel: "#2B2D31",
        },
      },
    },
  },
  plugins: [],
};

export default config;
