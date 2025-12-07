from collections.abc import Iterable
from typing import Any

class App:
    TITLE: str
    CSS_PATH: str | None
    BINDINGS: list[tuple[str, str, str]]

    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def compose(self, *args: Any, **kwargs: Any) -> Iterable[Any]: ...
    def run(self) -> None: ...
