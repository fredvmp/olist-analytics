# Error de API general
class APIError(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

# Error del servidor
class DatabaseError(APIError):
    def __init__(self, message="Database error"):
        super().__init__(message, 500)

# Errores fechas
class InvalidDateError(APIError):
    def __init__(self, message="Invalid date format. Use yyyy-mm-dd"):
        super().__init__(message, 400)

# Error validaciones
class ValidationError(APIError):
    def __init__(self, message="Invalid input"):
        super().__init__(message, 400)
