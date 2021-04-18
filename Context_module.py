from __future__ import annotations
from abc import ABC, abstractmethod

from Alice_module import *
import re
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

SCAN_WORDS = {'проверь', 'просканируй', 'сканируй', 'проверить', 'просканировать', 'сканировать', 'ссылка'}
EXIT_WORDS = {'выход', 'пока', 'выйти', 'уйти', 'покинуть'}
CHOICE_WORDS = {'функция', 'функции', 'возможности', 'возможность', 'варианты', 'вариант',
                'модули', 'модуль', 'умеешь'}
SKILLS_WORDS = {'переводчик', 'сканер'}
THANKS_WORDS = {'спасибо', 'класс', 'круто'}

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
        try:
            if set(req.words).intersection(EXIT_WORDS):
                self.context.transition_to(ExitState())
            if set(req.words).intersection(THANKS_WORDS):
                res.set_answer('Ага, не за что :)')
            if self.__check_url_regex(req.request_string):
                result = self.scan(req.request_string)
                if result:
                    res.set_answer(result)
                else:
                    raise UserWarning
            elif set(req.words).intersection(SCAN_WORDS):
                cleaned_request = self.__delete_unnecessary_words(req.words)
                if cleaned_request:
                    result = self.scan(cleaned_request)
                    logging.info(result)
                    if result:
                        res.set_answer(result)
                    else:
                        raise UserWarning
                else:
                    raise UserWarning
            else:
                raise UserWarning
        except UserWarning:
            res.set_answer('Что-то не так, либо Вы не ввели ссылку, либо она неправильная. '
                           'Попробуйте еще раз, либо поменяйте ссылку ;)')

    def __delete_unnecessary_words(self, words: list) -> str or dict:
        for e in words:
            if self.__check_url_regex(e):
                return e
        return False

    @staticmethod
    def __check_url_regex(url: str) -> bool:
        pattern = '^((http|https):\\/\\/)?(www\\.)?([A-Za-zА-Яа-я0-9]' \
                  '{1}[A-Za-zА-Яа-я0-9\\-]*\\.?)*\\.{1}[A-Za-zА-Яа-я0-9-]{2,8}(\\/([\\w#!:.?+=&%@!\\-\\/])*)?'
        matches = re.match(pattern, url)
        if matches:
            return True
        return False

    @staticmethod
    def __get_url_id(url: str) -> str or bool:
        params = {'x-apikey': API_KEY}
        req = requests.post(VT_URL, headers=params, data=f'url={url}')
        if req.status_code == 200:
            url_id = req.json()['data']['id']
            return url_id
        return False

    @staticmethod
    def __get_info(url_id: str) -> dict or bool:
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
            logging.info(results)
            return results
        return False

    def scan(self, url: str) -> str or bool:
        url_id = self.__get_url_id(url)
        if url_id:
            info = self.__get_info(url_id)
            if info:
                comment = ''
                if len(set(info.keys()).intersection({'clean', 'unrated'})) == 2:
                    if info['unrated'] / info['clean'] >= 1.2:
                        comment = 'Какая-то странная ссылка, будь внимателен\n'
                    elif info['unrated'] / info['clean'] <= 0.1:
                        comment = 'Все классно, должно быть безопасно!\n'
                    else:
                        comment = 'Что-то странное 0_o\n'
                elif len(set(info.keys()).intersection({'clean', 'unrated'})) == 1:
                    if 'clean' in info.keys():
                        comment = 'Все классно, должно быть безопасно!\n'
                    if 'unrated' in info.keys():
                        comment = 'Что-то странное 0_o\n'
                else:
                    comment = 'Оу, братец, как-то подозрительно не думаю, что стоит переходить, ' \
                              'либо используй защиту!\n'
                return comment + f'''Отчет антивирусов: {' '.join([f"{e} = {info[e]}" for e in info.keys()])}'''
        return False


class HelloState(State):
    def handle_dialog(self, res: AliceResponse, req: AliceRequest):
        res.set_answer('Привет. Мы сделали прикольный навык!')
        self.context.transition_to(ChoiceState())


class ChoiceState(State):
    def handle_dialog(self, res: AliceResponse, req: AliceRequest):
        if set(req.words).intersection(SKILLS_WORDS):
            # пока только scan skill
            self.context.transition_to(ScanUrlState())
            res.set_answer('Хорошо, отправь ссылку на сканирование!')
        else:
            res.set_answer('У нас есть несколько функций: переводчик и сканер. '
                           'Что хочешь попробовать?')


class ExitState(State):
    def handle_dialog(self, res: AliceResponse, req: AliceRequest):
        res.set_answer('Пока. Работа с навыком закончена :)')
        self.context.transition_to(HelloState())
