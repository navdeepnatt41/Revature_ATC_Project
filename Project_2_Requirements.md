# Project 2: Python, SQL, Docker Captstone

## 1. Data Model and ERD Requirements

### The database must have at least 5 objects with:
  - 1 core entity
  - 2-3 supporting entities
  - 1 junction table

### Required Relationship Types
- One-to-Many
- Many-to-Many
- Self-relationship

### Table Requirements
- Have at least 3 non-trivial columns
- Use of appropriate data types

### Artifact Requirements
- Students will produce:
  - ERD
  - Relational Schema

## 2. Alembic
- Initial migration must:
  - Create all tables
  - Define constraints and foreign keys
- At least 2 additional migrations that demonstrate schema evolution:
  - Add/remove a column
  - Change a constraint
  - Add new table or relationship
- Students must explain:
  - Why migrations exist
  - How to use appropriate commands to manage a schema over time

## 3. Endpoint Requirements
- Minimum of 10 endpoints demonstrating:
  - GET, POST, PUT or PATCH, and DELETE
- Minimum of 2 endpoints that demonstrate relationships:
  - Return nested or aggregate data

## 4. Validation and Error Handling
- All request/response bodies must use Pydantic models
- Validation errors must:
  - Return proper HTTP status codes
  - Include helpful error messages
    - Examples: Missing resources (404), invalid input (422), constraint violations (400 or 409)

## 5. Testing
- At least 10 tests total (100% coverage not required)
  - Test: endpoints, data validation, failure cases (negative tests)
- Check out fastAPI's TestClient to:
  - assert response codes
  - assert response payload structure
- Use mocks where appropriate

## 6. Visualization
- At least 1 notebook is required
- Load data from DB or csv/json
- Include at least 3 visualizations
- Include a variety of types. i.e. scatter, bar, histogram, etc.
- There should be variety in data analysis as well. e.g. do NOT give me 3 charts that are simply counts of columns