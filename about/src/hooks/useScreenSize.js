import { useMediaQuery } from 'react-responsive';

export const useScreenSize = () => {
  const lg = useMediaQuery({minWidth: 1280});
  const md = useMediaQuery({minWidth: 768});
  const sm = useMediaQuery({minWidth: 480});

  return lg ? 'lg': md ? 'md' : 'sm';
}