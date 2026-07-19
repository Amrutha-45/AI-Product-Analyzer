/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        base: {
          900: '#0A0A0B', // Deep Space (Background)
          800: '#141416', // Elevated Base (Cards)
          700: '#1F1F22', // Borders/Dividers
        },
        primary: {
          DEFAULT: '#3B82F6', // Trust Blue
          hover: '#60A5FA',
          glass: 'rgba(59, 130, 246, 0.1)',
        },
        accent: {
          DEFAULT: '#10B981', // Clean Green (Safe)
          warning: '#F59E0B', // Caution Amber (Moderate)
          danger: '#EF4444',  // Alert Red (High Risk)
        },
        text: {
          primary: '#FFFFFF',
          secondary: '#A1A1AA',
          muted: '#71717A',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        'glass': '0 4px 30px rgba(0, 0, 0, 0.5)',
        'glass-hover': '0 8px 32px rgba(59, 130, 246, 0.15)',
      },
      borderRadius: {
        'xl': '12px',
        '2xl': '16px',
        '3xl': '24px',
      },
      backdropBlur: {
        'xs': '2px',
        'sm': '4px',
        'md': '8px',
        'lg': '12px',
      }
    },
  },
  plugins: [],
}
