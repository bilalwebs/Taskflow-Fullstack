---
name: auth-skill
description: Implement secure authentication systems including signup, signin, password hashing, JWT tokens, and Better Auth integration.
---

# Authentication Skill

## Instructions

1. **User Signup**
   - Collect user credentials (email, password)
   - Validate input (email format, password strength)
   - Hash passwords before storing
   - Prevent duplicate accounts

2. **User Signin**
   - Verify user credentials
   - Compare hashed passwords
   - Handle invalid login attempts
   - Return authentication response

3. **Password Hashing**
   - Use strong hashing algorithms (bcrypt, argon2)
   - Apply salting for extra security
   - Never store plain-text passwords

4. **JWT Tokens**
   - Generate access tokens on successful login
   - Include user identity in payload
   - Set token expiration
   - Verify tokens for protected routes

5. **Better Auth Integration**
   - Configure authentication provider
   - Enable session and token handling
   - Integrate with frontend securely
   - Manage refresh tokens if supported

## Best Practices
- Enforce strong password rules
- Use HTTPS for all auth requests
- Store JWTs securely (httpOnly cookies preferred)
- Implement token expiration & refresh
- Add rate limiting to auth endpoints
- Log authentication events for monitoring

## Example Structure
```ts
// Signup
POST /api/auth/signup

// Signin
POST /api/auth/signin

// Protected Route
GET /api/user/profile
Authorization: Bearer <JWT_TOKEN>
