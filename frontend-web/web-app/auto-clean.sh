#!/bin/bash
set -e

echo "🧹 Starting Auth/Theme provider auto-cleaner..."

APP_FILE="frontend-web/web-app/src/App.js"
INDEX_FILE="frontend-web/web-app/src/index.js"

# 1. Backup files before modification
cp "$APP_FILE" "$APP_FILE.bak"
cp "$INDEX_FILE" "$INDEX_FILE.bak"

# 2. Clean App.js - strip out ThemeProvider/AuthProvider
echo "🔎 Cleaning $APP_FILE ..."
sed -i.bak '/AuthProvider/d' "$APP_FILE"
sed -i.bak '/ThemeProvider/d' "$APP_FILE"

# 3. Ensure App.js exports only App without providers
if ! grep -q "function App" "$APP_FILE"; then
  echo "⚠️ WARNING: App.js does not define a function App. Please review manually."
fi

# 4. Clean imports for removed providers in App.js
sed -i.bak '/AuthContext/d' "$APP_FILE"
sed -i.bak '/@material-tailwind\/react/d' "$APP_FILE"

echo "✅ App.js providers cleaned."

# 5. Verify index.js has proper wrapping
echo "🔎 Checking $INDEX_FILE ..."
if ! grep -q "ThemeProvider" "$INDEX_FILE"; then
  echo "⚠️ ThemeProvider missing in index.js — inserting..."
  sed -i.bak 's|<App />|<ThemeProvider>\n    <AuthProvider>\n      <App />\n    </AuthProvider>\n  </ThemeProvider>|' "$INDEX_FILE"
fi

# 6. Clean duplicate wrapping in index.js (safety)
sed -i.bak 's|<ThemeProvider>||g' "$INDEX_FILE"
sed -i.bak 's|</ThemeProvider>||g' "$INDEX_FILE"
sed -i.bak 's|<AuthProvider>||g' "$INDEX_FILE"
sed -i.bak 's|</AuthProvider>||g' "$INDEX_FILE"

# Re-insert clean structure
sed -i.bak 's|<App />|<ThemeProvider>\n    <AuthProvider>\n      <App />\n    </AuthProvider>\n  </ThemeProvider>|' "$INDEX_FILE"

echo "✅ index.js now wraps App correctly with ThemeProvider → AuthProvider → App."

# 7. Reinstall & rebuild
echo "📦 Reinstalling dependencies..."
rm -rf node_modules package-lock.json
npm install

echo "🚀 Restarting dev server..."
npm start
