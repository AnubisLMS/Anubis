module.exports = {
  purge: ['./src/***.{js, jsx}'],
  darkMode: false,
  theme: {
    extend: {
      fontFamily: {
        gosha: ['Gosha Sans', 'Arial', 'Helvetica', 'sans-serif'],
        serif: ['Gosha Sans', 'Arial', 'Helvetica', 'sans-serif'],
      },
      backgroundImage: (theme) => ({
        swirl: "url('../images/swirl-bg.png')",
        ide: "url('../images/ide.gif')",
      }),
      height: (theme) => ({
        screen43: '43vh',
      }),
      colors: {
        white: '#FFFFFF',
        primary: '#5686F5',
        secondary: '#1B1F24',
        tertiary: '#A5A5A5',
        dark: '#1B1F23',
        light: {
          300: '#CBD4D9',
          200: '#E7F3F9',
          100: '#F7F8F9',
          400: '#9FAFB7',
          500: '#424C52',
          600: '#212428',
        },
      },
    },
  },
  variants: {
    extend: {},
    width: ['responsive', 'hover', 'focus'],
  },
  plugins: [],
};
