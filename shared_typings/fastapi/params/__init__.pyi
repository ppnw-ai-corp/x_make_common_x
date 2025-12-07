
from collections.abc import Callable
from typing import Any

__all__ = ["Depends", "Header"]

def Depends(
    dependency: Callable[..., Any] | None = ..., *args: Any, **kwargs: Any
) -> Any: ...
def Header(
    default: Any = ...,
    *,
    alias: str | None = ...,
    convert_underscores: bool = ...,
    **kwargs: Any,
) -> Any: ...
