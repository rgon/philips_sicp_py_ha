"""Wake-on-LAN helper utilities built on asyncio."""

from __future__ import annotations

import asyncio
from typing import Final

__all__ = ["build_magic_packet", "async_wake_on_lan"]

_MAGIC_PREFIX: Final[bytes] = b"\xff" * 6
_HEX_DIGITS: Final[set[str]] = set("0123456789abcdefABCDEF")

def build_magic_packet(mac_address: str) -> bytes:
	"""Return the WOL magic packet for the provided MAC address."""

	hex_digits = [char for char in mac_address if char in _HEX_DIGITS]
	if len(hex_digits) != 12:
		raise ValueError("MAC address must resolve to exactly 12 hexadecimal digits")

	mac_bytes = bytes.fromhex("".join(hex_digits))
	return _MAGIC_PREFIX + mac_bytes * 16


async def async_wake_on_lan(
	mac_address: str,
	*,
	broadcast: str = "255.255.255.255",
	port: int = 9,
	repeat: int = 3,
	delay: float = 0.1,
) -> None:
	"""Send a Wake-on-LAN magic packet to the requested MAC address.

	The packet is sent ``repeat`` times: it is a single unacknowledged UDP
	datagram, and a lone loss is indistinguishable from a display that
	refused to wake.
	"""

	packet = build_magic_packet(mac_address)
	loop = asyncio.get_running_loop()
	transport, _ = await loop.create_datagram_endpoint(
		lambda: asyncio.DatagramProtocol(),
		remote_addr=(broadcast, port),
		allow_broadcast=True,
	)

	try:
		for attempt in range(repeat):
			if attempt:
				await asyncio.sleep(delay)
			transport.sendto(packet)
		await asyncio.sleep(0)  # ensure the send is flushed before closing
	finally:
		transport.close()
