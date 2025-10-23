# Page snapshot

```yaml
- generic [ref=e5]:
  - generic [ref=e6]:
    - img [ref=e8]
    - heading "Welcome back" [level=2] [ref=e10]
    - paragraph [ref=e11]: Sign in to your account
  - paragraph [ref=e13]: Invalid email or password
  - generic [ref=e14]:
    - generic [ref=e15]:
      - generic [ref=e16]: Email Address
      - textbox "Email Address" [ref=e17]: manager@test.com
    - generic [ref=e18]:
      - generic [ref=e19]: Password
      - generic [ref=e20]:
        - textbox "Password" [ref=e21]: password123
        - button [ref=e22] [cursor=pointer]:
          - img [ref=e23] [cursor=pointer]
    - button "Sign In" [active] [ref=e26] [cursor=pointer]
  - paragraph [ref=e27]:
    - text: Don't have an account?
    - link "Sign Up" [ref=e28] [cursor=pointer]:
      - /url: /signup
```