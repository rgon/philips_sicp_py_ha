import sys
from .ip_monitor import SICPIPMonitor

from .easycli import print_class_methods_as_commands, execute_command_and_return_log, CommandError

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

def main():
    """Main entry point."""
    if len(sys. argv) < 3:
        print_usage()
        sys.exit(1)
    
    monitor_arg = sys.argv[1]
    raw_command_args = sys.argv[2:]

    # Parse monitor ID(s)
    if monitor_arg.lower() == "all":
        monitors = [SICPIPMonitor(ip=ip, monitor_id=mon_id) for (ip, mon_id) in DISPLAYS.values()]
    else:
        try:
            monitor_key = int(monitor_arg)
            if monitor_key not in DISPLAYS:
                print(f"Error: Unknown monitor ID {monitor_key}")
                print(f"Available monitors: {', '. join(map(str, DISPLAYS.keys()))}")
                sys.exit(1)
            this_selection = DISPLAYS[monitor_key]
            monitors = [SICPIPMonitor(ip=this_selection[0], monitor_id=this_selection[1])]
        except ValueError:
            print("Error: Monitor ID must be a number or 'all'")
            sys.exit(1)
    
    success_count = 0
    for monitor in monitors:
        try:
            res = execute_command_and_return_log(monitor, raw_command_args[0], raw_command_args[1:])
        except CommandError as ce:
            print(f"⚠ {monitor.ip}: {ce}")
        except Exception as e:
            print(f"⚠ {monitor.ip} Error: {e}")
        else:
            success_count += 1
            print(f"✓ {monitor.ip}: {res}")

    print(f"\n{'✓' if success_count == len(monitors) else '⚠'} Command succeeded on {success_count}/{len(monitors)} displays")
