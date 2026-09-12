



class AppError(Exception):
    """Base class for application errors."""

class ConfigurationError(AppError):
    """Raised when application configuration is invalid."""

class DatabaseError(AppError):
    """Base class for database errors."""

class DatabaseConnectionError(DatabaseError):
    """Raised when a database connection fails."""
    
class SecurityError(AppError):
    """Base class for security errors."""

class InvalidAccessToken(SecurityError):
    """Raised when an access token is invalid."""    

class UserError(AppError):
    """Base class for user errors."""

class UserAlreadyExists(UserError):
    """Raised when a user email is already registered."""