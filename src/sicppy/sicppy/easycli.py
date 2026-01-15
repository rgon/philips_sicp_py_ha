from typing import Any
from enum import Enum

def snake_case_to_human_readable(name:str) -> str:
    """Convert snake_case string to human readable format."""
    return name.replace("_", " ").title()

def get_type_options(type_:Any):
    """Get possible options for a given type."""
    if type_ is bool:
        return "true|false"
    elif type_ is int:
        return "<0-100>"
    elif isinstance(type_, Enum):
        return "|".join([e.name.lower() for e in type_.__dict__.values() if isinstance(e, Enum)])
    else:
        return "<value>"

def print_class_methods_as_commands(cls, ignore_methods:set[str] = set()):
    for attr in dir(cls):
        if not attr.startswith("_") and callable(getattr(cls, attr)) and attr not in ignore_methods:
            print(f"  {attr}", end="")
            # print args
            method = getattr(cls, attr)
            if method.__code__.co_argcount > 1:
                args = method.__code__.co_varnames[1:method.__code__.co_argcount]
                # If arg is optional, denote with []
                arg_list = []
                for arg in args:
                    is_optional = False
                    if method.__defaults__:
                        default_args = method.__code__.co_varnames[method.__code__.co_argcount - len(method.__defaults__):method.__code__.co_argcount]
                        if arg in default_args:
                            is_optional = True
                    type_hint = method.__annotations__.get(arg, Any)
                    type_options = get_type_options(type_hint)
                    if is_optional:
                        arg_list.append(f"[{arg}:{type_options}]")
                    else:
                        arg_list.append(f"{arg}:{type_options}")
                print(f" {' '.join(arg_list)}")
            else:
                print()
            
            # Print method signature
            method = getattr(cls, attr)
            if method.__doc__:
                first_line = method.__doc__.strip().splitlines()[0]
                print(f"     {first_line}")
            else:
                print()

class CommandError(Exception):
    """Base class for command errors."""
    pass

def execute_command_on_class_instance(instance:Any, command_name:str, command_args:list[str]) -> Any:
    """Execute a command on a class instance with given arguments."""
    
    if not hasattr(instance, command_name):
        raise CommandError(f"Unknown command '{command_name}'")

    command_method = getattr(instance, command_name)
    # Convert args to appropriate types based on method annotations
    typed_args = []
    method_annotations = command_method.__annotations__
    for i, arg in enumerate(command_args):
        param_name = command_method.__code__.co_varnames[i + 1]  # +1 to skip 'self'
        param_type = method_annotations.get(param_name, str)
        if param_type is bool:
            typed_arg = arg.lower() in ("true", "1", "yes", "on")
        elif param_type is int:
            typed_arg = int(arg)
        elif issubclass(param_type, Enum):
            typed_arg = param_type[arg.upper()]
        else:
            typed_arg = arg
        typed_args.append(typed_arg)

    # print(f"Calling {command_name} with args: {typed_args}")
    return command_method(*typed_args)

def execute_command_and_return_log(instance:Any, command_name:str, command_args:list[str]) -> str:
    try:
        readable_command_name = snake_case_to_human_readable(command_name)
        res_prefix = f"{' '.join(readable_command_name.split()[1:])} = "
        res = execute_command_on_class_instance(instance, command_name, command_args)
    except CommandError as ce:
        raise ce
    except Exception as e:
        raise e
    else:
        if res is not None:
            return f"{res_prefix}{res}"
        else:
            return f"{readable_command_name} {' '.join(command_args)} ok"