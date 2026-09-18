# HTTP Status Codes

## Success

- `200 OK`: Successful read or update.
- `201 Created`: Resource was created.
- `204 No Content`: Successful deletion with no response body.

## Client Errors

- `400 Bad Request`: Malformed request.
- `401 Unauthorized`: Missing or invalid authentication.
- `403 Forbidden`: Authenticated but not allowed.
- `404 Not Found`: Resource does not exist or is not accessible.
- `409 Conflict`: Request conflicts with existing data, such as a duplicate email.
- `422 Unprocessable Entity`: FastAPI/Pydantic validation failed.

## Server Errors

- `500 Internal Server Error`: Unexpected server-side failure.