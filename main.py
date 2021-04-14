from __future__ import annotations
from flask import Flask
from flask_restful import Api
from Alice_module import *
import logging
import json
import sys
from abc import ABC, abstractmethod

# базовое логирование (надо улучшить)
logging.basicConfig(
    filename='logs.log',
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

app = Flask(__name__)
api = Api(app)
api.add_resource(Alice, '/app')

# secret key(надо настроить env)
# app.config['SECRET_KEY']


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


def main():
    # работа с Алисой
    # тут будет происходить смена состояний
    app.run()


if __name__ == "__main__":
    main()
