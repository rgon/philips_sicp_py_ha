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
            
        except socket.timeout as e:
            # print(f"✗ Connection timeout to {self.ip} (Monitor ID: {self.monitor_id})")
            # print(f"  No response within {TIMEOUT} seconds")
            raise NetworkError(e)
        except socket.error as e:
            # print(f"✗ Socket error for {self.ip} (Monitor ID: {self.monitor_id}): {e}")
            raise NetworkError(e)
        except Exception as e:
            # print(f"✗ Error for {self.ip} (Monitor ID: {self.monitor_id}): {e}")
            raise NetworkError(e)
        else:
            if not expect_data:
                return None  # No response expected for broadcast commands
            elif not response_data:
                raise NetworkError("No response received from monitor")

            # Parse response
            response = SicpResponse(response_data)
            
            # Log the action and response
            if response.is_ack:
                # print(f"✓ {action_description} - {self.ip} (Monitor {self.monitor_id})")
                return response
            elif response.is_nav:
                raise NotSupportedOrNotAvailableError("Command not supported or not available (NAV response)")
            elif response.is_nack:
                raise ChecksumOrFormatError("Checksum or format error (NACK response)")
            elif response.is_data_response:
                # print(f"✓ {action_description} - {self.ip} (Monitor {self.monitor_id})")
                return response
            else:
                # print(f"⚠ {action_description} - {self.ip} (Monitor {self.monitor_id})")
                # print(f"  Response: {response}")
                if response.error_message:
                    print(f"  Error: {response.error_message}")
                raise Exception(f"Unexpected response: {response}")