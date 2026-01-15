#!/usr/bin/env python3

import socket

from .response import SicpResponse
from .protocol import SICPProtocol


DEFAULT_PORT = 5000
TIMEOUT = 2

class ChecksumOrFormatError(Exception):
    """Exception for checksum or format errors (NACK responses)."""
    pass

class NotSupportedOrNotAvailableError(Exception):
    """Exception for not supported or not available commands (NAV responses)."""
    pass

class NetworkError(Exception):
    """Exception for network-related errors."""
    pass

class SICPIPMonitor(SICPProtocol):
    def __init__(self, ip:str, monitor_id=1, port=DEFAULT_PORT) -> None:
        super().__init__(monitor_id=monitor_id)
        self.ip = ip
        self.port = port

    def send_message(self, message, expect_data=False) -> SicpResponse | None:
        """
        Send SICP message to display and return parsed response.
        
        Args:
            monitor_id: Monitor ID
            ip: IP address
            message: Message bytes to send
            expect_data: True if expecting data response (GET command), False for ACK (SET command)
        
        Returns:
            SicpResponse object or None on error
        """
        try: 
            response_data = None
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(TIMEOUT)
                sock.connect((self.ip, self.port))
                sock.sendall(message)
                
                # Receive response
                if expect_data:
                    response_data = sock.recv(1024)
            
        except socket.timeout as exc:
            raise NetworkError(exc) from exc
        except socket.error as exc:
            raise NetworkError(exc) from exc
        except Exception as exc:
            raise NetworkError(exc) from exc
        else:
            if not expect_data:
                return None  # No response expected for broadcast commands
            if not response_data:
                raise NetworkError("No response received from monitor")

            response = SicpResponse(response_data)

            if response.is_nav:
                raise NotSupportedOrNotAvailableError("Command not supported or not available (NAV response)")
            if response.is_nack:
                raise ChecksumOrFormatError("Checksum or format error (NACK response)")
            if not response.valid:
                raise RuntimeError("Invalid response received from monitor")

            command = message[3] if len(message) > 3 else None
            payload = response.data_payload or []
            if command is not None and payload and payload[0] == command and len(payload) > 1:
                response.data_payload = payload[1:]
            else:
                response.data_payload = payload

            return response