/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'chat': {
          'bg': '#ede7db',
          'surface': '#f5f1ea',
          'border': '#e8d5b7',
          'text': '#2d3748',
          'text-secondary': '#718096',
          'accent': '#ed8936',
          'accent-light': '#f6ad55',
          'accent-hover': '#dd6b20',
          'error': '#e53e3e',
          'warning': '#ed8936',
          'success': '#38a169',
          'purple': '#805ad5',
          'pink': '#d53f8c'
        }
      },
      animation: {
        'typing': 'typing 1.5s steps(40, end) infinite',
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'chat-bubble': 'chatBubble 2s ease-in-out infinite',
        'pulse-gentle': 'pulseGentle 2s ease-in-out infinite',
      },
      keyframes: {
        typing: {
          '0%, 50%': { opacity: '1' },
          '51%, 100%': { opacity: '0' },
        },
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        chatBubble: {
          '0%, 100%': { transform: 'scale(1)', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' },
          '50%': { transform: 'scale(1.02)', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' },
        },
        pulseGentle: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.8' },
        },
      },
    },
  },
  plugins: [],
}