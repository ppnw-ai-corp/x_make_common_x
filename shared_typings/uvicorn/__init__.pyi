from typing import Protocol

class _ASGIApp(Protocol):
    def __call__(self, scope: object, receive: object, send: object) -> object: ...

class Config:
    app: object

    def __init__(self, app: object, **kwargs: object) -> None: ...

def run(
    app: _ASGIApp | object,
    host: str = ...,
    port: int = ...,
    log_level: str | None = ...,
    **kwargs: object,
) -> None: ...
