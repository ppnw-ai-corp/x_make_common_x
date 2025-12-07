
from collections.abc import Iterable
from typing import Any, TypeAlias

class PyJWTError(Exception): ...

DefDict: TypeAlias = dict[str, Any]

def encode(payload: DefDict, key: str, *, algorithm: str) -> str: ...
def decode(token: str, key: str, *, algorithms: Iterable[str]) -> DefDict: ...
