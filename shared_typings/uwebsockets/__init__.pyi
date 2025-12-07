
from collections.abc import Awaitable
from typing import Protocol

class WebSocketLike(Protocol):
    async def send(self, data: str) -> None: ...
    async def close(self) -> None: ...

class ClientModule(Protocol):
    def connect(
        self, endpoint: str, headers: dict[str, str]
    ) -> Awaitable[WebSocketLike]: ...

client: ClientModule
