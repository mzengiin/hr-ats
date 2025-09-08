# CVFlow API Documentation

## Overview

CVFlow is a comprehensive CV management and HR process automation system. This API provides authentication, user management, and role-based access control functionality.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

## Authentication Endpoints

### POST /auth/register

Register a new user account.

**Request Body:**
```json
{
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "password": "string"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "is_active": true,
  "role": {
    "id": "uuid",
    "name": "string",
    "description": "string"
  },
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid input data
- `409 Conflict`: Email already exists
- `422 Unprocessable Entity`: Validation error

### POST /auth/login

Authenticate user and get access tokens.

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response (200 OK):**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "uuid",
    "first_name": "string",
    "last_name": "string",
    "email": "string",
    "is_active": true,
    "role": {
      "id": "uuid",
      "name": "string",
      "description": "string"
    }
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid credentials
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded

### POST /auth/refresh

Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "string"
}
```

**Response (200 OK):**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired refresh token
- `422 Unprocessable Entity`: Validation error

### DELETE /auth/logout

Logout user and invalidate refresh token.

**Request Body:**
```json
{
  "refresh_token": "string"
}
```

**Response (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid refresh token
- `422 Unprocessable Entity`: Validation error

### GET /auth/me

Get current user information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "is_active": true,
  "role": {
    "id": "uuid",
    "name": "string",
    "description": "string",
    "permissions": {
      "users": ["create", "read", "update", "delete"],
      "roles": ["read"]
    }
  },
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired token

### POST /auth/change-password

Change user password.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "current_password": "string",
  "new_password": "string"
}
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid current password
- `401 Unauthorized`: Invalid or expired token
- `422 Unprocessable Entity`: Validation error

### POST /auth/logout-all

Logout from all devices.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "message": "Successfully logged out from all devices"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired token

## User Management Endpoints

### GET /users/

Get list of users with pagination and filtering.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `limit` (int, optional): Items per page (default: 10, max: 100)
- `search` (string, optional): Search term for name or email
- `role` (string, optional): Filter by role name
- `status` (string, optional): Filter by status (active/inactive)
- `sort_by` (string, optional): Sort field (default: created_at)
- `sort_order` (string, optional): Sort order (asc/desc, default: desc)

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "uuid",
      "first_name": "string",
      "last_name": "string",
      "email": "string",
      "is_active": true,
      "role": {
        "id": "uuid",
        "name": "string",
        "description": "string"
      },
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ],
  "total": 100,
  "page": 1,
  "pages": 10,
  "limit": 10
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: Insufficient permissions

### GET /users/{user_id}

Get specific user by ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "is_active": true,
  "role": {
    "id": "uuid",
    "name": "string",
    "description": "string"
  },
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: User not found

### POST /users/

Create new user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "password": "string",
  "role_id": "uuid",
  "is_active": true
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "is_active": true,
  "role": {
    "id": "uuid",
    "name": "string",
    "description": "string"
  },
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: Insufficient permissions
- `409 Conflict`: Email already exists
- `422 Unprocessable Entity`: Validation error

### PUT /users/{user_id}

Update user information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "role_id": "uuid",
  "is_active": true
}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "is_active": true,
  "role": {
    "id": "uuid",
    "name": "string",
    "description": "string"
  },
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: User not found
- `422 Unprocessable Entity`: Validation error

### DELETE /users/{user_id}

Delete user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "message": "User deleted successfully"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: User not found

### PATCH /users/{user_id}/activate

Activate user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "message": "User activated successfully"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: User not found

### PATCH /users/{user_id}/deactivate

Deactivate user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "message": "User deactivated successfully"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: User not found

## Role-Based Access Control

### Available Roles

1. **admin**: Full access to all resources
   - Users: create, read, update, delete
   - Roles: create, read, update, delete
   - Auth: read, update

2. **hr**: Limited access to user management
   - Users: create, read, update
   - Roles: read
   - Auth: read

3. **user**: Read-only access
   - Users: read
   - Roles: none
   - Auth: read

### Permission Format

Permissions are stored as JSON objects with resource names as keys and arrays of actions as values:

```json
{
  "users": ["create", "read", "update", "delete"],
  "roles": ["read"],
  "auth": ["read", "update"]
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Login attempts**: 5 attempts per minute per IP
- **Registration**: 3 attempts per minute per IP
- **Password changes**: 3 attempts per hour per user
- **Token refresh**: 10 attempts per minute per user

When rate limit is exceeded, the API returns `429 Too Many Requests`.

## Security Features

### Password Requirements

- Minimum 8 characters
- Must contain at least one letter and one number
- Special characters are allowed but not required

### Token Security

- Access tokens expire in 15 minutes
- Refresh tokens expire in 7 days
- Tokens are signed with HMAC-SHA256
- Refresh tokens are hashed before storage

### CORS Configuration

The API supports CORS for the following origins:
- `http://localhost:3000` (React development server)
- `http://localhost:3001` (Alternative React port)

### Security Headers

The API includes the following security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`

## Error Codes

| Code | Description |
|------|-------------|
| 200 | OK |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Unprocessable Entity |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

## Examples

### Complete Authentication Flow

```bash
# 1. Register new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "password": "password123"
  }'

# 2. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'

# 3. Use access token
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"

# 4. Refresh token
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<refresh_token>"
  }'

# 5. Logout
curl -X DELETE http://localhost:8000/api/v1/auth/logout \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<refresh_token>"
  }'
```

### User Management Flow

```bash
# 1. Get users list
curl -X GET "http://localhost:8000/api/v1/users/?page=1&limit=10" \
  -H "Authorization: Bearer <access_token>"

# 2. Create new user
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane@example.com",
    "password": "password123",
    "role_id": "<role_id>",
    "is_active": true
  }'

# 3. Update user
curl -X PUT http://localhost:8000/api/v1/users/<user_id> \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane@example.com",
    "role_id": "<role_id>",
    "is_active": true
  }'

# 4. Deactivate user
curl -X PATCH http://localhost:8000/api/v1/users/<user_id>/deactivate \
  -H "Authorization: Bearer <access_token>"

# 5. Delete user
curl -X DELETE http://localhost:8000/api/v1/users/<user_id> \
  -H "Authorization: Bearer <access_token>"
```

## Support

For API support and questions, please contact the development team or refer to the project documentation.



