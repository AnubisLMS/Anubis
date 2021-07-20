module.exports = {
  purge: ['./src/***.{js, jsx}'],
  darkMode: false,
  theme: {
    extend: {
      fontFamily: {
        gosha: ['Gosha Sans', 'Arial', 'Helvetica', 'sans-serif'],
        serif: ['Gosha Sans', 'Arial', 'Helvetica', 'sans-serif'],
      },
      backgroundImage: (theme)  => ({
        'swirl': "url('../images/swirl-bg.png')",
      }),
      colors: {
        white: '#FFFFFF',
        primary: '#FF9900',
        secondary: '#171B21',
        tertiary: '#A5A5A5',
        dark: '#1B1F23',
        light: {
          300: '#CBD4D9',
          200: '#E7F3F9',
          100: '#F7F8F9',
          400: '#9FAFB7',
          500: '#424C52',
          600: '#242C30'
        }
      },
    },
  },
  variants: {
    extend: {},
    width: ["responsive", "hover", "focus"]
  },
  plugins: [],
}
