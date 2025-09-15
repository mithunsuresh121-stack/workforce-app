# Page snapshot

```yaml
- generic [ref=e1]:
  - generic [ref=e4]:
    - generic [ref=e5]:
      - img "App Logo" [ref=e6]
      - heading "Workforce App" [level=1] [ref=e7]
    - generic [ref=e8]:
      - generic [ref=e9]:
        - generic [ref=e10]: Email
        - textbox [ref=e11]: demo@company.com
      - generic [ref=e12]:
        - generic [ref=e13]: Password
        - textbox [ref=e14]: password123
      - button "Login" [ref=e15] [cursor=pointer]
  - iframe [active] [ref=e16]:
    - generic [ref=f1e2]:
      - generic [ref=f1e3]: "Compiled with problems:"
      - button "Dismiss" [ref=f1e4] [cursor=pointer]: ×
      - generic [ref=f1e5]:
        - generic [ref=f1e6]:
          - generic [ref=f1e7] [cursor=pointer]: ERROR in ./src/App.js 33:43-52
          - generic [ref=f1e8]: export 'default' (imported as 'Dashboard') was not found in './pages/Dashboard' (module has no exports)
        - generic [ref=f1e9]:
          - generic [ref=f1e10] [cursor=pointer]: ERROR in ./src/App.js 56:43-52
          - generic [ref=f1e11]: export 'default' (imported as 'Dashboard') was not found in './pages/Dashboard' (module has no exports)
```