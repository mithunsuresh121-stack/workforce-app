#!/bin/bash
# Auto-clean unused imports flagged by ESLint
# Then auto-commit changes to git

echo "🔍 Scanning for unused imports in ./src..."

# Ensure eslint is installed
if ! npx eslint -v > /dev/null 2>&1; then
  echo "⚠️ ESLint not found. Installing locally..."
  npm install eslint --save-dev
fi

# Run ESLint with JSON output so we can parse
eslint_report=$(npx eslint ./src --format json)

# Extract files with issues
files=$(echo "$eslint_report" | jq -r '.[] | select(.messages != null) | .filePath')

if [ -z "$files" ]; then
  echo "✅ No unused imports found. Codebase is clean!"
  exit 0
fi

echo "🧹 Cleaning unused imports in the following files:"
echo "$files" | sort -u

# Fix each file
for file in $(echo "$files" | sort -u); do
  echo "   ➤ Fixing $file"
  npx eslint --fix "$file"
done

# Final check
echo "🔁 Re-running ESLint to verify cleanup..."
npx eslint ./src --quiet

# Auto-commit changes
if [ -n "$(git status --porcelain)" ]; then
  echo "💾 Staging changes..."
  git add ./src

  echo "📝 Committing cleanup..."
  git commit -m "chore: auto-clean unused imports with Blackbox script"

  echo "✅ Cleanup committed successfully!"
else
  echo "✅ No changes to commit."
fi
