import asyncio
import inspect
from typing import Any
from enum import Enum

def snake_case_to_human_readable(name:str) -> str:
    """Convert snake_case string to human readable format."""
    return name.replace("_", " ").title()

def get_type_options(type_:Any) -> tuple[str, str|None]:
    """Get possible options for a given type."""
    if type_ is bool:
        return "true|false", None
    elif type_ is int:
        return "<0-100>", None
    elif isinstance(type_, Enum) or isinstance(type_, type) and issubclass(type_, Enum):
        enum_name = type_.__name__
        return f"<{enum_name}>", f"{enum_name}: <{'|'.join([e.name.lower() for e in type_.__dict__.values() if isinstance(e, Enum)])}>"
    else:
        return "<value>", None

def print_class_methods_as_commands(cls, ignore_methods:set[str] = set()):
    for attr in dir(cls):
        if not attr.startswith("_") and callable(getattr(cls, attr)) and attr not in ignore_methods:
            print(f"  {attr}", end="")

            enum_arg_descriptions = []
            # print args
            method = getattr(cls, attr)
            if method.__code__.co_argcount > 1:
                args = method.__code__.co_varnames[1:method.__code__.co_argcount]

                arg_list = []
                for arg in args:
                    is_optional = False
                    if method.__defaults__:
                        default_args = method.__code__.co_varnames[method.__code__.co_argcount - len(method.__defaults__):method.__code__.co_argcount]
                        if arg in default_args:
                            is_optional = True

                    type_hint = method.__annotations__.get(arg, Any)
                    type_options, these_enum_descriptions = get_type_options(type_hint)
                    enum_arg_descriptions.append(these_enum_descriptions)

                    # If arg is optional, denote with []
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

            # Print enum descriptions if any
            for enum_desc in enum_arg_descriptions:
                if enum_desc:
                    print(f"     {enum_desc}")
                

class CommandError(Exception):
    """Base class for command errors."""
    pass

def execute_command_on_class_instance(instance:Any, command_name:str, command_args:list[str]) -> Any:
    """Execute a command on a class instance with given arguments (synchronous wrapper)."""
    return asyncio.run(_execute_command(instance, command_name, command_args))


async def async_execute_command_on_class_instance(instance:Any, command_name:str, command_args:list[str]) -> Any:
    """Async variant of execute_command_on_class_instance."""
    return await _execute_command(instance, command_name, command_args)


def execute_command_and_return_log(instance:Any, command_name:str, command_args:list[str]) -> str:
    """Execute command and return a formatted log line (synchronous wrapper)."""
    return asyncio.run(_execute_command_and_format_log(instance, command_name, command_args))


async def async_execute_command_and_return_log(instance:Any, command_name:str, command_args:list[str]) -> str:
    """Async variant of execute_command_and_return_log."""
    return await _execute_command_and_format_log(instance, command_name, command_args)


def _coerce_argument(value:str, expected_type:Any):
    if expected_type is bool:
        return value.lower() in ("true", "1", "yes", "on")
    if expected_type is int:
        return int(value)
    if inspect.isclass(expected_type) and issubclass(expected_type, Enum):
        return expected_type[value.upper()]
    return value


def _prepare_command_execution(instance:Any, command_name:str, command_args:list[str]):
    if not hasattr(instance, command_name):
        raise CommandError(f"Unknown command '{command_name}'")

    command_method = getattr(instance, command_name)
    typed_args = []
    annotations = getattr(command_method, "__annotations__", {})
    for index, arg in enumerate(command_args):
        param_name = command_method.__code__.co_varnames[index + 1]
        expected_type = annotations.get(param_name, str)
        typed_args.append(_coerce_argument(arg, expected_type))

    return command_method, typed_args


async def _invoke_command(command_method, typed_args):
    result = command_method(*typed_args)
    if inspect.isawaitable(result):
        return await result
    return result


async def _execute_command(instance:Any, command_name:str, command_args:list[str]) -> Any:
    command_method, typed_args = _prepare_command_execution(instance, command_name, command_args)
    return await _invoke_command(command_method, typed_args)


def _format_log_output(readable_command_name:str, command_args:list[str], result:Any) -> str:
    res_prefix = f"{' '.join(readable_command_name.split()[1:])} = "
    if result is not None:
        return f"{res_prefix}{result}"
    return f"{readable_command_name} {' '.join(command_args)} ok"


async def _execute_command_and_format_log(instance:Any, command_name:str, command_args:list[str]) -> str:
    readable_command_name = snake_case_to_human_readable(command_name)
    result = await _execute_command(instance, command_name, command_args)
    return _format_log_output(readable_command_name, command_args, result)