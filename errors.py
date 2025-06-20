# errors.py

class OzHashError(Exception):
    """Base class for all OzHash-related errors."""
    pass

class ConfigurationError(OzHashError):
    """Raised when there is an issue with the provided configuration."""
    def __init__(self, message="Invalid configuration provided."):
        self.message = message
        super().__init__(self.message)

class MemoryError(OzHashError):
    """Raised when there is an issue with memory allocation or access."""
    def __init__(self, message="Memory access or allocation failed."):
        self.message = message
        super().__init__(self.message)

class EncryptionError(OzHashError):
    """Raised when there is an issue during the encryption process."""
    def __init__(self, message="Encryption process encountered an error."):
        self.message = message
        super().__init__(self.message)

class VerificationError(OzHashError):
    """Raised when verification fails or encounters an error."""
    def __init__(self, message="Verification process failed."):
        self.message = message
        super().__init__(self.message)

if __name__ == "__main__":
    try:
        raise ConfigurationError("Matrix size must be a positive integer.")
    except ConfigurationError as e:
        print(f"Configuration Error: {e}")

    try:
        raise MemoryError("Failed to access memory block at index 10.")
    except MemoryError as e:
        print(f"Memory Error: {e}")
