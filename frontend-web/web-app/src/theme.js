import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#F59E0B', // Amber 500 - dominant color from login page
      light: '#FBBF24', // Amber 400
      dark: '#B45309',  // Amber 700
      contrastText: '#fff',
    },
    secondary: {
      main: '#2563EB', // Blue 600 - secondary color
      light: '#3B82F6', // Blue 500
      dark: '#1E40AF',  // Blue 800
      contrastText: '#fff',
    },
    error: {
      main: '#DC2626', // Red 600
    },
    warning: {
      main: '#FBBF24', // Amber 400
    },
    success: {
      main: '#16A34A', // Green 600
    },
    info: {
      main: '#2563EB', // Blue 600
    },
    text: {
      primary: '#1F2937', // Gray 800
      secondary: '#6B7280', // Gray 500
    },
    background: {
      default: '#F9FAFB', // Gray 50
      paper: '#FFFFFF',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
        containedPrimary: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: 'none',
          },
        },
      },
    },
  },
});

export default theme;
