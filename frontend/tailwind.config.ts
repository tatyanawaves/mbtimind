import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#7B52FF", // Headspace brand purple
          hover: "#6136D7", // Darker purple hover state
          light: "#F0EBFF", // Soft purple background/tint
        },
        surface: {
          bg: "#FAF7F2", // Cozy warm cream paper color
          card: "#FFFFFF",
          border: "#E9E4DC", // Warm soft border
        },
        text: {
          dark: "#2C2638", // Soft warm purple-charcoal (less harsh than black)
          secondary: "#6E6A8A", // Slate purple
          light: "#A4A0BD", // Muted purple-grey
        },
        accent: {
          purple: "#7B52FF",
          teal: "#35B0A2",   // Peaceful Headspace teal
          yellow: "#F5C747", // Cheerful Headspace yellow
          pink: "#F299B2",   // Playful Headspace pink
          red: "#EF4444",
          green: "#22C55E",
          amber: "#F5C747",
        },
      },
      fontFamily: {
        sans: ["var(--font-jakarta)", "Inter", "system-ui", "sans-serif"],
        heading: ["var(--font-outfit)", "system-ui", "sans-serif"],
      },
      borderRadius: {
        "3xl": "1.5rem",
        "4xl": "2rem",
      },
      boxShadow: {
        "bouncy": "0 8px 30px rgba(123, 82, 255, 0.12)",
        "pop": "0 8px 0px 0px #E9E4DC",
        "pop-primary": "0 8px 0px 0px #6136D7",
        "pop-hover": "0 4px 0px 0px #6136D7",
      },
    },
  },
  plugins: [],
};

export default config;
