import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          green: "#4BAA73",
          deep: "#357951",
          gold: "#FFCC00"
        }
      }
    }
  },
  plugins: []
};

export default config;
