import {createMuiTheme} from '@material-ui/core/styles';

export default function darkTheme (){
    return  createMuiTheme({
        palette: {
          primary: {
            light: "#63ccff",
            main: "#009be5",
            dark: "#006db3"
          },
          type: "dark"
        },
        typography: {
          h5: {
            fontWeight: 500,
            fontSize: 26,
            letterSpacing: 0.5
          }
        },
        shape: {
          borderRadius: 8
        },
        props: {
          MuiTab: {
            disableRipple: true
          }
        },
        mixins: {
          toolbar: {
            minHeight: 48
          }
        }
      });     

}