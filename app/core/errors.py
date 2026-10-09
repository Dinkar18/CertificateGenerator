class ErrorCodes:
    TOO_MANY_RECIPIENTS = "TOO_MANY_RECIPIENTS"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    JOB_NOT_FOUND = "JOB_NOT_FOUND"
    CERTIFICATE_NOT_FOUND = "CERTIFICATE_NOT_FOUND"
    FILE_MISSING = "FILE_MISSING"
    CERTIFICATE_FAILED = "CERTIFICATE_FAILED"
    CERTIFICATE_PROCESSING = "CERTIFICATE_PROCESSING"

class ErrorMessages:
    TOO_MANY_RECIPIENTS = "Maximum allowed recipients exceeded."
    INTERNAL_ERROR = "Failed to create generation job."
    JOB_NOT_FOUND = "Generation job was not found."
    CERTIFICATE_NOT_FOUND = "Certificate was not found."
    FILE_MISSING = "The certificate file could not be found on the server."
    CERTIFICATE_PROCESSING = "Certificate is still being processed."
    
    @staticmethod
    def certificate_failed(reason: str) -> str:
        return f"Certificate generation failed: {reason}"
        
def get_error_detail(code: str, message: str) -> dict:
    return {"code": code, "message": message}
