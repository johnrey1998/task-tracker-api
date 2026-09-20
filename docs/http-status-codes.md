# HTTP Status Codes

This guide describes the statuses currently returned by the API and the common statuses reserved for future behavior.

## Statuses Used By This API

### Success

- `200 OK`: The request succeeded. Used for login, task reads, and task updates.
- `201 Created`: A resource was created. Used for user registration and task creation.
- `204 No Content`: A task was deleted successfully. The response has no body.

### Client Errors

- `401 Unauthorized`: Authentication is missing or invalid. Protected task routes return this status when the bearer token is missing or invalid, and login returns it for invalid credentials.
- `404 Not Found`: The requested task does not exist or is not accessible to the authenticated user.
- `409 Conflict`: Registration conflicts with existing data, such as a duplicate email address.
- `422 Unprocessable Entity`: FastAPI/Pydantic validation failed, such as a missing field, invalid email, invalid task ID, or password that does not meet the schema requirements.

## Common Framework Or Future Statuses

- `400 Bad Request`: A malformed request that cannot be processed. No route currently raises this status explicitly.
- `403 Forbidden`: An authenticated user is not allowed to perform an action. No route currently raises this status explicitly; inaccessible tasks currently result in `404`.
- `405 Method Not Allowed`: The HTTP method is not supported for a matching path. FastAPI can return this automatically.
- `500 Internal Server Error`: An unexpected server-side failure. FastAPI can return this for an unhandled exception.

## Endpoint Summary

| Endpoint | Success | Documented errors |
| --- | --- | --- |
| `POST /api/v1/users/` | `201 Created` | `409`, `422` |
| `POST /api/v1/auth/login` | `200 OK` | `401`, `422` |
| `GET /api/v1/tasks/` | `200 OK` | `401` |
| `POST /api/v1/tasks/` | `201 Created` | `401`, `422` |
| `GET /api/v1/tasks/{task_id}` | `200 OK` | `401`, `404`, `422` |
| `PATCH /api/v1/tasks/{task_id}` | `200 OK` | `401`, `404`, `422` |
| `DELETE /api/v1/tasks/{task_id}` | `204 No Content` | `401`, `404`, `422` |