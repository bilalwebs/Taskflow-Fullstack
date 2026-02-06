---
name: database-skill
description: Design and manage databases including table creation, migrations, and scalable schema design.
---

# Database Skill

## Instructions

1. **Schema Design**
   - Identify entities and relationships
   - Normalize data where appropriate
   - Define primary and foreign keys
   - Plan for scalability and future changes

2. **Create Tables**
   - Define clear table structures
   - Use appropriate data types
   - Add constraints (NOT NULL, UNIQUE)
   - Set indexes for performance

3. **Migrations**
   - Create version-controlled migration files
   - Apply schema changes incrementally
   - Support rollback on failure
   - Keep migrations small and reversible

4. **Relationships**
   - One-to-one, one-to-many, many-to-many
   - Enforce referential integrity
   - Use cascading rules carefully

5. **Data Integrity**
   - Use constraints and validations
   - Avoid redundant data
   - Ensure consistency across tables

## Best Practices
- Use meaningful table and column names
- Never edit production data manually
- Track all schema changes via migrations
- Index frequently queried columns
- Back up databases before migrations
- Test migrations in staging environments

## Example Structure
```sql
-- users table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- migration flow
migrate up
migrate down
