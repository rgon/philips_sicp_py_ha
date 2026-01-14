#!/usr/bin/env python3

import socket

from .messages import CMD_COMMUNICATION_CONTROL, RESPONSE_ACK, RESPONSE_NAV, RESPONSE_NACK

# from .protocol import SICPProtocol
# class SICPIPMonitor(SICPProtocol):
#     pass


PORT = 5000
TIMEOUT = 2

class SicpResponse:
    """Parse and represent a SICP response."""
    
    def __init__(self, data):
        self.raw_data = data
        self. valid = False
        self.is_ack = False
        self.is_nav = False
        self.is_nack = False
        self.is_data_response = False
        self.command = None
        self.data_payload = []
        self.error_message = None
        
        if not data or len(data) < 5:
            self.error_message = "Response too short"
            return
        
        self.size = data[0]
        self.monitor_id = data[1]
        
        # Check if this is a Communication Control response (ACK/NAV/NACK)
        if len(data) >= 6 and data[3] == CMD_COMMUNICATION_CONTROL: 
            self.command = CMD_COMMUNICATION_CONTROL
            response_code = data[4]
            
            if response_code == RESPONSE_ACK:
                self. is_ack = True
                self.valid = True
            elif response_code == RESPONSE_NAV:
                self.is_nav = True
                self. valid = True
                self.error_message = "Command not supported/available (NAV)"
            elif response_code == RESPONSE_NACK:
                self.is_nack = True
                self.valid = True
                self.error_message = "Checksum or format error (NACK)"
            else:
                self.error_message = f"Unknown response code: 0x{response_code:02x}"
        
        # Otherwise it's a data response (e.g., from a GET command)
        elif len(data) >= 5:
            self.is_data_response = True
            self.valid = True
            self.command = data[3]
            # Data payload starts at byte 4 and goes until checksum (last byte)
            self.data_payload = list(data[4:-1])
    
    def __str__(self):
        hex_data = ' '.join(f'{b:02x}' for b in self.raw_data)
        if self.is_ack:
            return f"ACK - {hex_data}"
        elif self.is_nav:
            return f"NAV (Not Available) - {hex_data}"
        elif self.is_nack:
            return f"NACK (Error) - {hex_data}"
        elif self.is_data_response:
            return f"DATA (cmd=0x{self.command:02x}) - {hex_data}"
        else:
            return f"UNKNOWN - {hex_data}"

def send_message(monitor_id, ip, message, action_description, expect_data=False):
    """
    Send SICP message to display and return parsed response.
    
    Args:
        monitor_id: Monitor ID
        ip: IP address
        message: Message bytes to send
        action_description: Description for logging
        expect_data: True if expecting data response (GET command), False for ACK (SET command)
    
    Returns:
        SicpResponse object or None on error
    """
    try: 
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(TIMEOUT)
            sock.connect((ip, PORT))
            sock.sendall(message)
            
            # Receive response
            response_data = sock.recv(1024)
            
        # Parse response
        response = SicpResponse(response_data)
        
        # Log the action and response
        if response.is_ack:
            print(f"✓ {action_description} - {ip} (Monitor {monitor_id})")
            # print(f"  Response: {response}")
        elif response.is_nav:
            print(f"⚠ {action_description} - {ip} (Monitor {monitor_id})")
            # print(f"  Response: {response}")
            print("  Error: Command not supported by this display")
            return None
        elif response.is_nack:
            print(f"✗ {action_description} - {ip} (Monitor {monitor_id})")
            print(f"  Response: {response}")
            print("  Error: Checksum or format error")
            return None
        elif response.is_data_response:
            print(f"✓ {action_description} - {ip} (Monitor {monitor_id})")
            # print(f"  Response: {response}")
        else:
            print(f"⚠ {action_description} - {ip} (Monitor {monitor_id})")
            print(f"  Response: {response}")
            if response.error_message:
                print(f"  Error: {response.error_message}")
        
        return response
        
    except socket.timeout:
        print(f"✗ Connection timeout to {ip} (Monitor ID: {monitor_id})")
        print(f"  No response within {TIMEOUT} seconds")
        return None
    except socket.error as e:
        print(f"✗ Socket error for {ip} (Monitor ID: {monitor_id}): {e}")
        return None
    except Exception as e:
        print(f"✗ Error for {ip} (Monitor ID: {monitor_id}): {e}")
        return None

