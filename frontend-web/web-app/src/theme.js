// src/theme.js
// Centralized theme configuration for Linear-style design system
// Minimal, modern, clean - no heavy frameworks

export const theme = {
  colors: {
    primary: "#2563EB", // Blue-600
    primaryHover: "#1E40AF", // Blue-800
    accent: "#F59E0B", // Amber-500
    background: "#F9FAFB", // Gray-50
    surface: "#FFFFFF", // White cards
    border: "#E5E7EB", // Gray-200
    textPrimary: "#111827", // Gray-900
    textSecondary: "#6B7280", // Gray-500
    error: "#DC2626", // Red-600
    success: "#16A34A", // Green-600
    danger: "#DC2626",
    neutral: "#6B7280",
  },
  typography: {
    fontFamily: "Inter, system-ui, sans-serif",
    h1: "font-size: 1.875rem; font-weight: 700; color: var(--text-primary);",
    h2: "font-size: 1.5rem; font-weight: 600; color: var(--text-primary);",
    body: "font-size: 1rem; color: var(--text-secondary);",
    small: "font-size: 0.875rem; color: var(--text-secondary);",
  },
  components: {
    button: "padding: 0.5rem 1rem; border-radius: 0.5rem; font-weight: 500; transition: all 0.2s; box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);",
    buttonPrimary: "background-color: var(--primary); color: white; border: none;",
    buttonPrimaryHover: "background-color: var(--primary-hover);",
    input: "width: 100%; padding: 0.5rem 0.75rem; border: 1px solid var(--border); border-radius: 0.5rem; outline: none; transition: border-color 0.2s;",
    inputFocus: "border-color: var(--primary); box-shadow: 0 0 0 3px rgb(37 99 235 / 0.1);",
    card: "background-color: var(--surface); padding: 2rem; border-radius: 0.75rem; box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);",
    link: "color: var(--primary); text-decoration: none; font-weight: 500;",
    linkHover: "color: var(--primary-hover); text-decoration: underline;",
    passwordInputWrapper: "position: relative;",
  },
  spacing: {
    xs: "0.25rem",
    sm: "0.5rem",
    md: "1rem",
    lg: "1.5rem",
    xl: "2rem",
  },
  borderRadius: {
    sm: "0.25rem",
    md: "0.5rem",
    lg: "0.75rem",
    xl: "1rem",
  },
};
