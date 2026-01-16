#!/usr/bin/env python3

import asyncio

from .response import SicpResponse
from .protocol import SICPProtocol
from .errors import NetworkError, ProtocolError, NotSupportedOrNotAvailableError, ChecksumOrFormatError

DEFAULT_PORT = 5000
TIMEOUT = 2

class SICPIPMonitor(SICPProtocol):
    def __init__(self, ip:str, monitor_id=1, port=DEFAULT_PORT, timeout=TIMEOUT) -> None:
        super().__init__(monitor_id=monitor_id)
        self.ip = ip
        self.port = port
        self.timeout = timeout

    async def send_message(self, message, expect_data=False) -> SicpResponse | None:
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
        reader = None
        writer = None
        response_data = None

        try:
            connect_coro = asyncio.open_connection(self.ip, self.port)
            # connection timeout
            reader, writer = await asyncio.wait_for(connect_coro, timeout=self.timeout)

            writer.write(message)
            # write timeout
            await asyncio.wait_for(writer.drain(), timeout=None) #self.timeout)

            if expect_data:
                response_data = await asyncio.wait_for(reader.read(1024), timeout=self.timeout) # read timeout

        except asyncio.TimeoutError as exc:
            raise NetworkError("Communication timed out") from exc
        except OSError as exc:
            raise NetworkError(exc) from exc
        except Exception as exc:
            raise Exception(exc) from exc
        finally:
            if writer is not None:
                writer.close()
                try:
                    await writer.wait_closed()
                except Exception:
                    pass

        if not expect_data:
            return None  # No response expected for broadcast commands
        if not response_data:
            raise ProtocolError("No response received from monitor")

        try:
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
        except IndexError as exc:
            raise ProtocolError("Malformed response payload") from exc