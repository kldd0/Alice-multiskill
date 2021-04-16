from __future__ import annotations
from abc import ABC, abstractmethod
from Alice_module import *
import logging
from dotenv import load_dotenv
import requests
import os

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)
logging.basicConfig(
    filename='logs.log',
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    level=logging.DEBUG
)

SCAN_WORDS = {'проверь', 'просканируй', 'сканируй', 'чекни'}
EXIT_WORDS = {'выход', 'пока', 'выйти', 'уйти', 'покинуть'}
CHOICE_WORDS = {'функция', 'функции', 'возможности', 'возможность', 'варианты', 'вариант',
                'модули', 'модуль'}

API_KEY = os.getenv('API_KEY')
VT_URL = 'https://www.virustotal.com/api/v3/urls'


class Context:
    _state = None

    def __init__(self, state):
        self.transition_to(state)

    def transition_to(self, state):
        logging.info(f'Context: переключаемся в {type(state).__name__}')
        self._state = state
        self._state.context = self

    def handle_dialog(self, res: AliceResponse, req: AliceRequest):
        self._state.handle_dialog(res, req)


class State(ABC):

    @property
    def context(self) -> Context:
        return self._context

    @context.setter
    def context(self, context: Context) -> None:
        self._context = context

    @abstractmethod
    def handle_dialog(self, res: AliceResponse, req: AliceRequest):
        pass


class ScanUrlState(State):
    """
    Реализация класса сканирования для удобной работы с VirusTotal API
    """

    def handle_dialog(self, res: AliceResponse, req: AliceRequest) -> None:
        if set(req.words).intersection(SCAN_WORDS):
            cleaned_request = self.__delete_unnecessary_words(req.words)
            if type(cleaned_request) == str:
                res.set_answer(self.scan(cleaned_request))
            else:
                res.set_answer('Вы не ввели ссылку, что мне проверять?')
                self.context.transition_to(HelloState)

        if set(req.words).intersection(EXIT_WORDS):
            self.context.transition_to(HelloState())

    @staticmethod
    def __delete_unnecessary_words(words: list) -> str or dict:
        for e in words:
            if 'http' in e:
                return e
        return {'result': 'Not found'}

    @staticmethod
    def __get_url_id(url: str) -> str or json:
        params = {'x-apikey': API_KEY}
        req = requests.post(VT_URL, headers=params, data=f'url={url}')
        if req.status_code == 200:
            url_id = req.json()['data']['id']
            return url_id
        return {'status': 'error'}

    @staticmethod
    def __get_info(url_id: str) -> dict or str:
        params = {'x-apikey': API_KEY}
        response = requests.get(f'https://www.virustotal.com/api/v3/analyses/{url_id}', headers=params)
        if response.status_code == 200:
            res = dict(response.json()['data']['attributes']['results'])
            results = dict()
            for e in res.keys():
                if res[e]['result'] in results.keys():
                    results[res[e]['result']] += 1
                else:
                    results[res[e]['result']] = 1
            return results
        return {'status': 'error'}

    def scan(self, url: str) -> str:
        url_id = self.__get_url_id(url)
        if type(url) == str:
            info = self.__get_info(url_id)
            if type(info) == dict:
                return f'''Отчет антивирусов: {' '.join([f"{e} = {info[e]}" for e in info.keys()])}'''


class HelloState(State):
    def handle_dialog(self, res: AliceResponse, req: AliceRequest):
        res.set_answer('Привет. Мы сделали прикольный навык!')
        # self.context.transition_to(ChoiceState())
        self.context.transition_to(ExitState())


# class ChoiceState(State):
#     def handle_dialog(self, res: AliceResponse, req: AliceRequest):
#         res.set_answer('У нас есть несколько функций: переводчик и сканнер')


class ExitState(State):

    def handle_dialog(self, res: AliceResponse, req: AliceRequest):
        res.set_answer('Привет. Работа с навыком закончена :)')
        self.context.transition_to(HelloState())


cnt = Context(ScanUrlState())
