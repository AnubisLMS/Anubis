module.exports = {
  purge: ['./src/***.{js, jsx}'],
  darkMode: false,
  theme: {
    extend: {
      backgroundImage: (theme)  => ({
        'swirl': "url('../images/swirl-bg.png')",
      }),
      colors: {
        white: '#FFFFFF',
        primary: '#FF9900',
        secondary: '#171B21',
        tertiary: 'A5A5A5',
      }
    },
  },
  variants: {
    extend: {},
  },
  plugins: [],
}
