#!/bin/bash
set -e

echo "🔍 Scanning project for inconsistent design elements..."

SRC_DIR="./src"

# Step 1: Ensure PageLayout exists
LAYOUT_FILE="$SRC_DIR/layouts/PageLayout.jsx"
mkdir -p "$(dirname "$LAYOUT_FILE")"

cat > "$LAYOUT_FILE" <<'EOF'
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";

export default function PageLayout({ children }) {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <div className="flex flex-col flex-1">
        <Navbar />
        <main className="p-6">{children}</main>
      </div>
    </div>
  );
}
EOF

echo "✅ PageLayout.jsx ensured."

# Step 2: Replace raw elements with Material Tailwind
find "$SRC_DIR" -type f -name "*.jsx" -o -name "*.js" | while read file; do
  # Replace button with Button
  sed -i '' 's/<button /<Button /g' "$file"
  sed -i '' 's/<\/button>/<\/Button>/g' "$file"

  # Replace input with Input
  sed -i '' 's/<input /<Input /g' "$file"

  # Replace card-like divs
  sed -i '' 's/<div className="[^"]*card[^"]*">/<Card>/g' "$file"
  sed -i '' 's/<\/div>/<\/Card>/g' "$file"
done

echo "✅ Replaced raw buttons, inputs, and card divs."

# Step 3: Ensure Material Tailwind imports exist
find "$SRC_DIR" -type f -name "*.jsx" -o -name "*.js" | while read file; do
  if grep -q "<Button" "$file" || grep -q "<Input" "$file" || grep -q "<Card" "$file"; then
    if ! grep -q "@material-tailwind/react" "$file"; then
      sed -i '' '1i\
import { Button, Input, Card } from "@material-tailwind/react";\
' "$file"
    fi
  fi
done

echo "✅ Ensured Material Tailwind imports."

# Step 4: Wrap all pages in PageLayout
find "$SRC_DIR/pages" -type f -name "*.jsx" | while read page; do
  if ! grep -q "PageLayout" "$page"; then
    sed -i '' '1i\
import PageLayout from "../layouts/PageLayout";\
' "$page"

    sed -i '' 's/export default function \(.*\)() {/export default function \1() {\
  return (\
    <PageLayout>/' "$page"

    sed -i '' 's/}\s*$/    <\/PageLayout>\n  );\n}/' "$page"
  fi
done

echo "✅ Wrapped pages in PageLayout."

# Step 5: Commit changes
git add "$SRC_DIR"
git commit -m "chore(design): enforce Material Tailwind design consistency (buttons, inputs, cards, layout)"

echo "🎉 Design auto-apply complete. Repo updated and committed."
