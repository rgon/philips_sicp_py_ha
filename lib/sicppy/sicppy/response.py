from .messages import SICPCommand, RESPONSE_ACK, RESPONSE_NAV, RESPONSE_NACK

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
        if len(data) >= 6 and data[3] == SICPCommand.COMMUNICATION_CONTROL: 
            self.command = SICPCommand.COMMUNICATION_CONTROL
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
