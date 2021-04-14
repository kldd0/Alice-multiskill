from __future__ import annotations
from abc import ABC, abstractmethod


class Context:
    _state = None

    def __init__(self, state: State) -> None:
        self.transition_to(state)

    def transition_to(self, state: State):
        self._state = state
        self._state.context = self

    def make_response(self, data):
        self._state.make_response(data)

    def handle_answer(self, data):
        self._state.handle_answer(data)


class State(ABC):

    @property
    def context(self) -> Context:
        return self._context

    @context.setter
    def context(self, context: Context) -> None:
        self._context = context

    @abstractmethod
    def make_response(self, data) -> None:
        pass

    @abstractmethod
    def handle_answer(self, data) -> None:
        pass