
class ChecksumOrFormatError(Exception):
    """Exception for checksum or format errors (NACK responses)."""
    pass

class NotSupportedOrNotAvailableError(Exception):
    """Exception for not supported or not available commands (NAV responses)."""
    pass

class NetworkError(Exception):
    """Exception for network-related errors."""
    pass

class ProtocolError(Exception):
    """Exception for protocol-related errors."""
    pass
