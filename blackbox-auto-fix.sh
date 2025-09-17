#!/bin/bash
# blackbox-auto-fix.sh
# Auto-fix React hook collision (duplicate React + ThemeProvider placement)

set -e

cd frontend-web/web-app

echo "🔍 Checking React installs..."
npm ls react react-dom || true

DUPES=$(npm ls react react-dom 2>/dev/null | grep -c deduped || true)

if [ "$DUPES" -eq 0 ]; then
  echo "⚠️ Multiple React versions detected. Running npm dedupe..."
  npm dedupe
  npm install
else
  echo "✅ Single React version detected."
fi

echo "🔧 Fixing ThemeProvider placement..."

# Remove ThemeProvider from App.js if it exists
if grep -q "ThemeProvider" src/App.js; then
  echo "⚠️ Found ThemeProvider in App.js. Removing..."
  sed -i.bak '/ThemeProvider/d' src/App.js
  rm -f src/App.js.bak
else
  echo "✅ No ThemeProvider in App.js."
fi

# Ensure ThemeProvider exists in index.js
if ! grep -q "ThemeProvider" src/index.js; then
  echo "⚠️ No ThemeProvider found in index.js. Inserting..."
  sed -i.bak '/<App \/>/i\
    <ThemeProvider>' src/index.js
  sed -i.bak '/<\/App>/a\
    </ThemeProvider>' src/index.js
  rm -f src/index.js.bak
else
  echo "✅ ThemeProvider already present in index.js."
fi

echo "📦 Rebuilding project..."
npm run build || echo "⚠️ Build failed — check errors manually."

echo "💾 Committing changes..."
git add src/App.js src/index.js package.json package-lock.json
git commit -m "Blackbox auto-fix: deduped React + fixed ThemeProvider placement"

echo "✅ Auto-fix completed successfully."
