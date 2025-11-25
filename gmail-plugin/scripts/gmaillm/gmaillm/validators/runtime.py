"""Runtime type validation decorators and utilities.

This module provides runtime type checking to complement Python's type hints.
Use these decorators to catch type mismatches that static type checkers miss.
"""

import functools
import inspect
from typing import Any, Callable, TypeVar, get_type_hints, get_origin, get_args

from pydantic import BaseModel, ValidationError


T = TypeVar('T')


def validate_types(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to validate function arguments against type hints at runtime.

    Usage:
        @validate_types
        def process_email(email: EmailFull, count: int) -> str:
            return f"{email.subject} - {count}"

        # This will raise TypeError:
        process_email(EmailSummary(...), "not an int")

    Note: Only validates arguments with type hints. Skips 'self' and 'cls'.
    """
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        # Bind arguments to parameters
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()

        # Check each parameter
        for param_name, param_value in bound.arguments.items():
            # Skip self/cls
            if param_name in ('self', 'cls'):
                continue

            # Skip if no type hint
            if param_name not in type_hints:
                continue

            expected_type = type_hints[param_name]

            # Validate against expected type
            if not _check_type(param_value, expected_type):
                raise TypeError(
                    f"Argument '{param_name}' expected {expected_type}, "
                    f"got {type(param_value).__name__}"
                )

        return func(*args, **kwargs)

    return wrapper


def _check_type(value: Any, expected_type: type) -> bool:
    """Check if value matches expected type, handling generics."""

    # Handle None/Optional
    if value is None:
        origin = get_origin(expected_type)
        if origin is None:
            return expected_type is type(None)  # noqa: E721
        # Check if Optional (Union[X, None])
        args = get_args(expected_type)
        return type(None) in args

    # Handle Pydantic models
    if isinstance(expected_type, type) and issubclass(expected_type, BaseModel):
        return isinstance(value, expected_type)

    # Handle Union types
    origin = get_origin(expected_type)
    if origin is Union:
        args = get_args(expected_type)
        return any(_check_type(value, arg) for arg in args)

    # Handle List, Dict, etc.
    if origin is list:
        if not isinstance(value, list):
            return False
        # Check element types if specified
        args = get_args(expected_type)
        if args:
            return all(_check_type(item, args[0]) for item in value)
        return True

    if origin is dict:
        if not isinstance(value, dict):
            return False
        args = get_args(expected_type)
        if len(args) == 2:
            key_type, val_type = args
            return all(
                _check_type(k, key_type) and _check_type(v, val_type)
                for k, v in value.items()
            )
        return True

    # Handle basic types
    return isinstance(value, expected_type)


def validate_pydantic(model_class: type[BaseModel]) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to validate that argument is a specific Pydantic model.

    Usage:
        @validate_pydantic(EmailFull)
        def format_email(email):
            # Guaranteed email is EmailFull instance
            return f"{email.subject} from {email.from_}"

        # This will raise ValidationError:
        format_email(EmailSummary(...))

    Args:
        model_class: Pydantic model class to validate against

    Returns:
        Decorator function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Get function signature to check for 'self' or 'cls' parameter
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())
        first_param_is_self_or_cls = (
            len(param_names) > 0 and param_names[0] in ('self', 'cls')
        )

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Determine which argument to validate
            if not args:
                raise ValueError(f"{func.__name__} requires at least one argument")

            # If first parameter is 'self' or 'cls', validate second argument
            if first_param_is_self_or_cls:
                if len(args) < 2:
                    raise ValueError(
                        f"{func.__name__} requires at least two arguments "
                        f"when used as a method"
                    )
                arg = args[1]
            else:
                arg = args[0]

            # Validate type
            if not isinstance(arg, model_class):
                raise TypeError(
                    f"{func.__name__} expected {model_class.__name__}, "
                    f"got {type(arg).__name__}"
                )

            return func(*args, **kwargs)

        return wrapper
    return decorator


# Import Union for type checking
try:
    from typing import Union
except ImportError:
    from types import UnionType as Union  # Python 3.10+
