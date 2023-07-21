import React, {useState} from 'react';
import {Box, Button, DialogTitle, DialogContent, Input, IconButton} from '@mui/material';
import ImageIcon from '@mui/icons-material/Image';
import {makeStyles} from '@mui/styles';
import Popover from '@mui/material/Popover';

export const useStyles = makeStyles((theme) => ({
  button: {
    margin: theme.spacing(0.5),
  },
}));

export default function EmbedImage({embedImage}) {
  const [clicked, setClicked] = useState(false);
  const [imageURL, setImageURL] = useState('');
  const [anchorEl, setAnchorEl] = React.useState(null);
  const classes = useStyles();

  const closeModal = () => {
    setClicked(false);
    setImageURL('');
    setAnchorEl(null);
  };

  const openModal = (e) => {
    setClicked(true);
    setAnchorEl(e.currentTarget);
  };

  const handleEmbedImage = () => {
    if (!imageURL) {
      return;
    }
    embedImage(imageURL);
    closeModal();
  };

  const uploadImage = (file) => {
    const data = new FormData();
    data.append('file', file);
    axios.post(`/api/public/forums/image`, data)
      .then((image_url) => {
        // Wait for image url of uploaded image to be returned
        return image_url.data;
      })
      .catch(standardErrorHandler(enqueueSnackbar));
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) {
      return;
    }
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onloadend = () => {
      const image_url = uploadImage(file);
      embedImage(image_url);
    };
    closeModal();
  };

  return (
    <Box sx={{position: 'relative'}}>
      <IconButton
        color= {clicked ? 'primary' : 'inherit'}
        size="small"
        onClick={openModal} // Open modal for image
        onMouseDown={(e) => e.preventDefault()}
      >
        <ImageIcon />
      </IconButton>

      <Popover open={clicked}
        onClose={closeModal}
        anchorEl={anchorEl}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'center',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'center',
        }}>
        <DialogTitle>{'Embed Image'}</DialogTitle>
        <DialogContent>
          <Box flex={1} display="flex" flexDirection="column">
            <Box display="flex" flexDirection="row" justifyContent="flex-end">
              <Input
                placeholder="Image URL"
                margin="dense"
                label="Image URL"
                type="text"
                onChange={(e) => setImageURL(e.target.value)}
              />
              <Button className={classes.button} variant="outlined" onClick={() => handleEmbedImage()}>
                Embed
              </Button>
            </Box>
            <p style={{textAlign: 'center', margin: '1rem'}}>OR</p>
            <Button variant="outlined" className={classes.button} component="label">
                Upload
              <input hidden accept="image/*" multiple type="file" onChange={handleFileUpload} />
            </Button>
          </Box>
        </DialogContent>
      </Popover>
    </Box>
  );
};
