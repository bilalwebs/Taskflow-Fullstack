---
name: backend-skill
description: Build backend services by generating routes, handling requests and responses, and connecting to databases.
---

# Backend Skill

## Instructions

1. **Route Generation**
   - Define RESTful or RPC-style routes
   - Use clear and consistent URL patterns
   - Separate routes by feature or module
   - Support CRUD operations

2. **Request Handling**
   - Parse request parameters, body, and headers
   - Validate incoming data
   - Handle query and path parameters
   - Manage authentication and authorization context

3. **Response Handling**
   - Return consistent response formats
   - Use appropriate HTTP status codes
   - Handle success and error responses
   - Provide meaningful error messages

4. **Database Connection**
   - Configure database clients or ORMs
   - Manage connection pooling
   - Execute queries safely
   - Handle connection errors gracefully

5. **Business Logic**
   - Keep controllers thin
   - Move logic to services or use-cases
   - Avoid coupling routes directly to database logic

## Best Practices
- Follow REST standards and naming conventions
- Validate all incoming requests
- Centralize error handling
- Use environment variables for configuration
- Log requests and errors
- Keep code modular and testable

## Example Structure
```ts
// Routes
GET    /api/users
POST   /api/users
PUT    /api/users/:id
DELETE /api/users/:id

// Flow
Request → Route → Controller → Service → Database → Response
