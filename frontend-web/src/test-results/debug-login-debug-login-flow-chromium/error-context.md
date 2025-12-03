# Page snapshot

```yaml
- generic [ref=e5]:
  - generic [ref=e6]:
    - img [ref=e8]
    - heading "Welcome back" [level=2] [ref=e10]
    - paragraph [ref=e11]: Sign in to your account
  - generic [ref=e12]:
    - generic [ref=e13]:
      - generic [ref=e14]: Email Address
      - textbox "Email Address" [ref=e15]: demo@company.com
    - generic [ref=e16]:
      - generic [ref=e17]: Password
      - generic [ref=e18]:
        - textbox "Password" [active] [ref=e19]: password123
        - button [ref=e20] [cursor=pointer]:
          - img [ref=e21] [cursor=pointer]
    - button "Sign In" [ref=e24] [cursor=pointer]
  - paragraph [ref=e25]:
    - text: Don't have an account?
    - link "Sign Up" [ref=e26] [cursor=pointer]:
      - /url: /signup
```