# SICPpy
A Python implementation of the Philips Signage Control Protocol (SICP).

## Features
Incomplete although thorough implementation. See the implemented methods in [messages.py#SICPCommand](sicppy/messages.py).

Only IP transport is implemented, although it's extensible to serial transport.

## Usage
It exposes a CLI and a programmatic API.

The CLI may be used as follows:

```bash
$: uv run python3 -m sicppy

$: uv run python3 -m sicppy all
```