#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Define paths
const webAppDir = path.join('frontend-web', 'web-app');
const srcDir = path.join(webAppDir, 'src');
const indexPath = path.join(srcDir, 'index.js');
const appPath = path.join(srcDir, 'App.js');

// --- 1️⃣ Deduplicate React ---
console.log('Deduplicating React...');
try {
  execSync('npm ls react react-dom', { cwd: webAppDir, stdio: 'inherit' });
  execSync('npm dedupe', { cwd: webAppDir, stdio: 'inherit' });
  execSync('rm -rf node_modules package-lock.json', { cwd: webAppDir, stdio: 'inherit' });
  execSync('npm install', { cwd: webAppDir, stdio: 'inherit' });
  console.log('React deduped successfully.');
} catch (err) {
  console.error('Error deduping React:', err);
}

// --- 2️⃣ Move ThemeProvider + AuthProvider to index.js ---
let indexContent = fs.readFileSync(indexPath, 'utf-8');

// Ensure imports exist
if (!indexContent.includes("import { ThemeProvider }")) {
  indexContent = "import { ThemeProvider } from '@material-tailwind/react';\n" + indexContent;
}
if (!indexContent.includes("import { AuthProvider }")) {
  indexContent = "import { AuthProvider } from './contexts/AuthContext';\n" + indexContent;
}

// Wrap <App /> with providers if not already wrapped
if (!indexContent.includes('<ThemeProvider>')) {
  indexContent = indexContent.replace(
    /<App\s*\/>/,
    `<ThemeProvider>\n  <AuthProvider>\n    <App />\n  </AuthProvider>\n</ThemeProvider>`
  );
}

fs.writeFileSync(indexPath, indexContent);
console.log('ThemeProvider + AuthProvider ensured in index.js.');

// --- 3️⃣ Remove extra providers from App.js and other files ---
const removeProviders = (filePath) => {
  let content = fs.readFileSync(filePath, 'utf-8');
  const patterns = [
    /<ThemeProvider>[\s\S]*?<\/ThemeProvider>/gm,
    /<AuthProvider>[\s\S]*?<\/AuthProvider>/gm
  ];
  patterns.forEach(pattern => { content = content.replace(pattern, '') });
  fs.writeFileSync(filePath, content);
};

// Remove providers from App.js
if (fs.existsSync(appPath)) {
  removeProviders(appPath);
  console.log('Removed extra providers from App.js.');
}

// Optional: remove from all other JS/JSX files in src/
const walkSync = (dir, filelist = []) => {
  fs.readdirSync(dir).forEach(file => {
    const filepath = path.join(dir, file);
    if (fs.statSync(filepath).isDirectory()) {
      filelist = walkSync(filepath, filelist);
    } else if (filepath.endsWith('.js') || filepath.endsWith('.jsx')) {
      filelist.push(filepath);
    }
  });
  return filelist;
};

walkSync(srcDir).forEach(file => {
  if (file !== appPath && file !== indexPath) removeProviders(file);
});

console.log('Extra providers removed from other files.');

// --- 4️⃣ Commit the fix ---
try {
  execSync('git add .', { stdio: 'inherit' });
  execSync('git commit -m "Auto-fix: Deduped React, centralized ThemeProvider/AuthProvider"', { stdio: 'inherit' });
  console.log('Changes committed successfully.');
} catch (err) {
  console.error('Error committing changes:', err);
}

console.log('✅ Auto-fix completed. Please restart your dev server.');
