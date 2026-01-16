import sys
import asyncio
from typing import List
from .ip_monitor import SICPIPMonitor

from .easycli import (
    print_class_methods_as_commands,
    async_execute_command_and_return_log,
    CommandError,
)

DISPLAYS = {
    0: ("192.168.45.210", 1),
    1: ("192.168.45.211", 1),
}

def print_usage():
    """Print usage information."""
    print(f"Usage: {sys.argv[0]} <monitor_id|all> <command> [args]")
    print("\nAvailable monitors:")
    for key, (ip, mon_id) in DISPLAYS.items():
        print(f"  {key}: Monitor ID {mon_id}: {ip}")
    print("\nCommands:")
    print_class_methods_as_commands(SICPIPMonitor, ignore_methods={"send_message"})

async def _run_command_for_monitor(monitor:SICPIPMonitor, command:str, args:list[str]) -> bool:
    try:
        res = await async_execute_command_and_return_log(monitor, command, args)
    except CommandError as ce:
        print(f"⚠ {monitor.ip}: {ce}")
        return False
    except Exception as exc:
        print(f"⚠ {monitor.ip} Error: {exc}")
        return False
    else:
        print(f"✓ {monitor.ip}: {res}")
        return True


def _build_monitor_list(arg:str) -> List[SICPIPMonitor]:
    if arg.lower() == "all":
        return [SICPIPMonitor(ip=ip, monitor_id=mon_id) for (ip, mon_id) in DISPLAYS.values()]

    try:
        monitor_key = int(arg)
    except ValueError as exc:
        raise CommandError("Monitor ID must be a number or 'all'") from exc

    if monitor_key not in DISPLAYS:
        available = ', '.join(map(str, DISPLAYS.keys()))
        raise CommandError(f"Unknown monitor ID {monitor_key}. Available monitors: {available}")

    host, monitor_id = DISPLAYS[monitor_key]
    return [SICPIPMonitor(ip=host, monitor_id=monitor_id)]


async def _async_main(argv:list[str]) -> int:
    if len(argv) < 3:
        print_usage()
        return 1

    monitor_arg = argv[1]
    raw_command_args = argv[2:]
    if not raw_command_args:
        print_usage()
        return 1

    try:
        monitors = _build_monitor_list(monitor_arg)
    except CommandError as exc:
        print(f"Error: {exc}")
        return 1

    success_count = 0
    for monitor in monitors:
        ok = await _run_command_for_monitor(monitor, raw_command_args[0], raw_command_args[1:])
        if ok:
            success_count += 1

    print(f"\n{'✓' if success_count == len(monitors) else '⚠'} Command succeeded on {success_count}/{len(monitors)} displays")
    return 0 if success_count == len(monitors) else 1


def main():
    """Main entry point."""
    exit_code = asyncio.run(_async_main(sys.argv))
    if exit_code:
        sys.exit(exit_code)
