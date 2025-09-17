// src/theme.ts
// Centralized theme configuration for Login & SignUp pages
// ⚠️ Do not override styles directly in components — extend this theme only.

export const theme = {
  colors: {
    primary: "#2563EB", // Tailwind blue-600
    primaryHover: "#1E40AF", // Tailwind blue-800
    accent: "#F59E0B", // Amber-500
    background: "#F9FAFB", // Gray-50
    surface: "#FFFFFF", // White cards
    border: "#E5E7EB", // Gray-200
    textPrimary: "#111827", // Gray-900
    textSecondary: "#6B7280", // Gray-500
    error: "#DC2626", // Red-600
    success: "#16A34A", // Green-600
  },
  typography: {
    fontFamily: "Inter, system-ui, sans-serif",
    h1: "text-3xl font-bold text-gray-900",
    h2: "text-2xl font-semibold text-gray-800",
    body: "text-base text-gray-700",
    small: "text-sm text-gray-500",
  },
  components: {
    button: "px-4 py-2 rounded-lg font-medium transition-colors shadow-sm",
    buttonPrimary:
      "bg-blue-600 text-white hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-1",
    input:
      "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
    card: "bg-white p-8 rounded-xl shadow-lg",
    link: "text-blue-600 hover:text-blue-800 font-medium",
    passwordInputWrapper: "relative",
  },
};
