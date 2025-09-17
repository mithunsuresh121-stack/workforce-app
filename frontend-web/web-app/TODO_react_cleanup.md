# React Cleanup TODO

- [x] Cd to frontend-web/web-app
- [x] Verify Node environment: node --version
- [x] Step 1: Check installed React versions: npm ls react react-dom
- [x] Step 2: Clean existing dependencies: rm -rf node_modules package-lock.json
- [x] Step 3: Reinstall dependencies: npm install
- [x] Step 4: Deduplicate React packages: npm dedupe
- [x] Step 5: Force install React 18.2.0: npm install react@18.2.0 react-dom@18.2.0 --force
- [x] Step 6: Create Webpack alias config: webpack.fix.react.cjs
