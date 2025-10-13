import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: "#2196f3", light: "#64b5f6", dark: "#1976d2" },
    secondary: { main: "#00acc1" },
    background: { default: "#121212", paper: "#1e1e1e" },
    success: { main: "#4caf50", light: "#66bb6a" },
    warning: { main: "#ff9800", light: "#ffb74d" },
    error: { main: "#f44336", light: "#ff5722" },
    info: { main: "#26c6da", light: "#64b5f6" },
  },
  typography: {
    fontFamily:
      'Inter, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Helvetica Neue, Arial, "Apple Color Emoji", "Segoe UI Emoji"',
    h1: { fontWeight: 700 },
    h2: { fontWeight: 700 },
    h3: { fontWeight: 700 },
  },
  shape: { borderRadius: 12 },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: { backgroundImage: "none" },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage:
            "linear-gradient(180deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.04) 60%)",
          backdropFilter: "blur(8px)",
          transition: "all 0.3s ease-in-out",
        },
      },
    },
    MuiDataGrid: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
    MuiButton: {
      defaultProps: { disableElevation: true },
    },
  },
});

export default theme;
