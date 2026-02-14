class APIError(Exception):
    """Custom API exception with error details."""

    def __init__(self, error_type: str, message: str, status_code: int, request_id: str = None, retry_after: int = None):
        self.error_type = error_type
        self.message = message
        self.status_code = status_code
        self.request_id = request_id
        self.retry_after = retry_after
        super().__init__(message)
