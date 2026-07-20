from collections.abc import Callable
from dataclasses import dataclass

class ObservableList(list):
    def __init__(self, iterable=()):
        super().__init__(iterable)
        self._handlers: dict[int, Callable[[str, dict], None]] = {}
        self._next_id = 0

    # Выполняет регистрацию обработчика
    # Возвращает id обработчика
    def register_handler(self, handler: Callable[[str, dict], None]) -> int:
        hid = self._next_id
        self._next_id += 1
        self._handlers[hid] = handler
        return hid

    # Снимает регистрацию обработчика
    # Возвращает id обработчика
    def unregister_handler(self, hid: int) -> None:
        print(f"removed handler {hid}")
        self._handlers.pop(hid, None)

    def _notify(self, event: str, payload: dict) -> None:
        for h in list(self._handlers.values()):
            h(event, payload)

    def append(self, item):
        super().append(item)
        self._notify("append", {"item": item})

    def remove(self, value):
        super().remove(value)
        self._notify("remove", {"value": value})


@dataclass
class DestroyInfo:
    storage: ObservableList
    handlers: list[int]
