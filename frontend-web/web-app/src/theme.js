import { createTheme } from '@mui/material/styles';

// Centralized MUI theme configuration matching Login page design
// Extracted from Login.jsx: colors, typography, spacing, borderRadius

const theme = createTheme({
  palette: {
    primary: {
      main: '#2563EB', // Blue-600, matches login button background
      dark: '#1E40AF', // Blue-800, for hover states
    },
    secondary: {
      main: '#F59E0B', // Amber-500, accent color from login
    },
    background: {
      default: '#F9FAFB', // Gray-50, login background
      paper: '#FFFFFF', // White, for cards/surfaces
    },
    text: {
      primary: '#111827', // Gray-900, login title/text
      secondary: '#6B7280', // Gray-500, login subtitle/labels
    },
    error: {
      main: '#DC2626', // Red-600, for errors
    },
    success: {
      main: '#16A34A', // Green-600
    },
    divider: '#E5E7EB', // Gray-200, borders
  },
  typography: {
    fontFamily: 'Inter, system-ui, sans-serif', // Matches login font
    h1: {
      fontSize: '1.875rem', // 30px
      fontWeight: 700,
      color: 'text.primary',
    },
    h2: {
      fontSize: '1.5rem', // 24px, matches login title
      fontWeight: 600,
      color: 'text.primary',
    },
    h3: {
      fontSize: '1.25rem', // 20px
      fontWeight: 600,
      color: 'text.primary',
    },
    h4: {
      fontSize: '1.125rem', // 18px, for page titles
      fontWeight: 600,
      color: 'text.primary',
    },
    h5: {
      fontSize: '1rem', // 16px
      fontWeight: 600,
      color: 'text.primary',
    },
    h6: {
      fontSize: '0.875rem', // 14px
      fontWeight: 600,
      color: 'text.primary',
    },
    body1: {
      fontSize: '1rem', // 16px
      color: 'text.primary',
    },
    body2: {
      fontSize: '0.875rem', // 14px, matches login labels
      color: 'text.secondary',
    },
    button: {
      fontWeight: 500, // Matches login button
      textTransform: 'none', // No uppercase
    },
  },
  shape: {
    borderRadius: 8, // 0.5rem, matches login button/card radius
  },
  spacing: 8, // 8px unit, maps to theme.spacing(1) = 8px, etc.
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8, // Match login button
          fontWeight: 500,
          textTransform: 'none',
          boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)', // Subtle shadow
          '&:hover': {
            boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)', // Deeper on hover
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12, // 0.75rem, matches login card
          boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)', // Login shadow
          border: '1px solid',
          borderColor: 'divider',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8, // Match login input
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: 'primary.main',
            },
            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
              borderColor: 'primary.main',
              boxShadow: '0 0 0 3px rgb(37 99 235 / 0.1)', // Login focus shadow
            },
          },
        },
      },
    },
    MuiInputLabel: {
      styleOverrides: {
        root: {
          color: 'text.secondary',
          fontSize: '0.875rem',
          fontWeight: 500,
        },
      },
    },
  },
});

export default theme;
