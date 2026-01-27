/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // MedCase Pro Brand Colors - Neon Medical Aesthetic
        'med': {
          50: '#effef9',
          100: '#cbffee',
          200: '#98ffde',
          300: '#53fdc6',
          400: '#14f195', // Primary Neon
          500: '#00d683',
          600: '#00a86b',
          700: '#008558',
          800: '#066949',
          900: '#08563d',
          950: '#023023',
        },
        // Deep Space / Ocean - Darker and richer
        'ocean': {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
          950: '#020617', // Main background text contrast source
        },
        // Vibrant Accents
        'coral': {
          400: '#ff8FA3',
          500: '#FF6B6B',
          600: '#ee5253',
        },
        'gold': {
          400: '#ffeaa7',
          500: '#fdcb6e',
          600: '#e1b12c',
        }
      },
      fontFamily: {
        'display': ['Outfit', 'sans-serif'],
        'body': ['"Plus Jakarta Sans"', 'sans-serif'],
        'mono': ['"Space Grotesk"', 'monospace'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'mesh-gradient': 'linear-gradient(135deg, #0a1628 0%, #0f2137 50%, #152d47 100%)',
        'glow-conic': 'conic-gradient(from 180deg at 50% 50%, #14b89c 0deg, #2dd4b3 180deg, #14b89c 360deg)',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'slide-up': 'slideUp 0.5s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'fade-in': 'fadeIn 0.5s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
        'bounce-soft': 'bounceSoft 0.6s ease-out',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideDown: {
          '0%': { opacity: '0', transform: 'translateY(-10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        bounceSoft: {
          '0%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.05)' },
          '100%': { transform: 'scale(1)' },
        },
      },
      boxShadow: {
        'glow': '0 0 40px -10px rgba(20, 184, 156, 0.5)',
        'glow-lg': '0 0 60px -15px rgba(20, 184, 156, 0.6)',
        'inner-glow': 'inset 0 0 20px rgba(20, 184, 156, 0.1)',
      },
    },
  },
  plugins: [],
}
