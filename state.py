import json
import logging
import os
from abc import abstractmethod, ABC

import requests

from alice import AliceRequest, AliceResponse
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

EXIT_WORDS = {'выход', 'пока', 'выйти', 'уйти', 'покинуть'}
TRANSLATE_WORDS = {'переведи', 'переведите', 'перевод'}

SKILL_ID = os.getenv('SKILL_ID')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')


class Context:
    """Класс Context предназначен для управления состояниями навыка Алисы.
    ---------------------------------------------------------------------
    Методы
        transition_to(state) - переключает контекст в состояние state

        handle_dialog(res, req) - основная функция для управления диалогом с пользователем.
            res: AliceResponse - ответ для пользователя в виде класса AliceResponse
            req: AliceRequest - запрос пользователя в виде класса AliceRequest"""
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
    """Базовый абстрактный класс состояния.
     --------------------------------------
     Методы
        context - возвращает используемый данным состоянием контекст
        handle_dialog(res: req) - функция, которую вызывает контекст, для обработки диалога
        с пользователем"""

    @property
    def context(self) -> Context:
        return self._context

    @context.setter
    def context(self, context: Context) -> None:
        self._context = context

    @abstractmethod
    def handle_dialog(self, res: AliceResponse, req: AliceRequest):
        pass


class TranslatorState(State):
    """Класс TranslatorState - одно из состояний навыка Алисы.
    ----------------------------------------------------------
    Note:
        Навык работает не со всеми языками, а только с самыми основными
        Навык по умолчанию переводит с любого языка на английский, если не указан язык,
         на который нужно перевести
        Запрос должен содержать в себе слово "переведи" для работы функции.
    ----------------------------------------------------------
    Задача класса - реализовывать  основные функции голосового переводчика:
        переводить по умолчанию с русского на английский
        переводить на необходимый язык при его указании ("переведи <предложение> на японский)
        переводить с необходимого языка при его указании (переведи <предложение> с японского)
        переводить с выбранного языка на другой язык (переведи <предложение> с японского на русский)
        определять только то, что нужно перевести, и не учитывать ненужные для перевода слова.
        определять стандартные ошибки при вводе пользователя
    --------------------------------------------------------------------------------------------
    Методы
        handle_dialog(res, req) - основная функция управления диалогом с пользователем
        get_translate_request(words, foreign_words) - возвращает строку, которую необходимо
            перевести, исходный язык, язык перевода и callback (ошибку или OK)
        __delete_unnecessary_words(words) - удаляет из списка слов пользователя ненужные для
            перевода слова.
        __get_languages(words) - определяет с какого языка и на какой язык пользователь хочет
            совершить перевод. Возвращает языки в формате ISO639-1. Если язык не поддерживается,
            возвращается None.Если языки не указаны, возвращает en, ru.
        __language_to_iso(language) - возвращает язык в формате ISO639-1.
        __delete_languages(words, lang_fr, lang_to) - удаляет все языки ненужные из запроса
            для перевода
        translate(text, language_from, language_to) - переводит текст (text) с языка
            language_from на язык language_to
    ---------------------------------------------------------------------------------------------"""

    def handle_dialog(self, res: AliceResponse, req: AliceRequest):
        if set(req.words).intersection(EXIT_WORDS):
            self.context.transition_to(HelloState())
            return

        if set(req.words).intersection(TRANSLATE_WORDS):
            translate_req, lang_fr, lang_to, callback = self.get_translate_request(req.words,
                                                                                   req.foreign_words)
            if callback == 'OK':
                res.set_answer(self.translate(translate_req, lang_fr, lang_to))
                return
            res.set_answer(callback)
            return
        res.set_answer('Пиши: переведи [слово/предложение] с [языка] на [язык].\n'
                       'По умолчанию перевод производится с русского на английский\n'
                       'Для более подробной помощи перейдите в раздел "Помощь"')
        res.set_suggests([{'title': 'Выйти', 'hide': True}])

    def get_translate_request(self, words: list, foreign_words: list):
        to_translate_words = self.__delete_unnecessary_words(words)
        language_from, language_to = self.__get_languages(words)
        if not language_from:
            return None, language_from, language_to, 'Извините.' \
                                                     ' Я пока не умею переводить с этого языка'
        if not language_to:
            return None, language_from, language_to, 'Извините.' \
                                                     ' Я пока не умею переводить на этот язык'
        to_translate_words = self.__delete_languages(to_translate_words, language_from, language_to)
        if not to_translate_words:
            to_translate_words = foreign_words
        if not to_translate_words:
            return None, language_from, language_to, 'Извините. Вы не ввели то, что нужно перевести.'
        if language_from == language_to:
            if foreign_words and language_from == language_to == 'ru':
                return None, language_from, language_to, 'Извините. Я пока не умею распознавать' \
                                                         ' языки.Укажите язык пожалуйста'
            return None, language_from, language_to, 'Извините. Укажите два разных языка пожалуйста'

        return ' '.join(to_translate_words), language_from, language_to, 'OK'

    @staticmethod
    def __delete_unnecessary_words(words: list) -> list:
        unnecessary_words = {'алиса', 'переведи', 'переведите', 'перевод', 'слово', 'слова',
                             'предложение', 'предложения'}
        to_translate_words = [word for word in words if word not in unnecessary_words]
        return to_translate_words

    def __get_languages(self, words: list):
        language_from = 'ru'
        language_to = 'en'

        for i in range(len(words)):
            if words[i] == 'с' and 'ского' in words[i + 1]:
                language_from = self.__language_to_iso(f"{words[i + 1][:-3]}ий".title())
            elif words[i] == 'на' and 'ский' in words[i + 1]:
                language_to = self.__language_to_iso(words[i + 1].title())

        return language_from, language_to

    @staticmethod
    def __language_to_iso(language) -> str or None:
        with open('languages.json', 'r') as json_file:
            languages_to_iso = json.load(json_file)
            try:
                return languages_to_iso[language]
            except KeyError:
                return None

    @staticmethod
    def __delete_languages(words: list, lang_fr, lang_to) -> list:
        with open('languages.json', 'r') as json_file:
            langs = json.load(json_file)

            fr_lang = [lang for lang, cd in langs.items() if cd == lang_fr][0][:-2].lower()
            language_from = f'с {fr_lang}ого'
            to_lang = [lang for lang, cd in langs.items() if cd == lang_to][0].lower()
            language_to = f'на {to_lang}'

            my_words = ' '.join(words)
            if f'{language_from} языка' in my_words:
                my_words = my_words.replace(f'{language_from} языка', '')
            elif language_from in my_words:
                my_words = my_words.replace(language_from, '')
            if f'{language_to} язык' in my_words:
                my_words = my_words.replace(f'{language_to} язык', '')
            elif language_to in my_words:
                my_words = my_words.replace(language_to, '')
        return my_words.split()

    @staticmethod
    def translate(text, language_from='ru', language_to='en'):
        url = "https://translated-mymemory---translation-memory.p.rapidapi.com/api/get"

        params = {"langpair": f"{language_from}|{language_to}", "q": text, "mt": "1",
                  "onlyprivate": "0"}

        headers = {
            'x-rapidapi-key': "69bdf32b4cmsh23d9e9126500c48p192dfdjsnde5efcc7ffd9",
            'x-rapidapi-host': "translated-mymemory---translation-memory.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=params).json()

        translated = response['responseData']['translatedText']
        if ''.join(translated.split()) == ''.join(text.split()):
            return 'Вы указали неверный язык, перевод невозможен.'
        return translated


class MapsState(State):
    """Класс MapsState - одно из состояний навыка для Алисы для взаимодействия с API Яндекс.Карт
    ---------------------------------------------------------------------------------------------
    Note:
        На карте показывается первый введеный пользователем адрес
    ----------------------------------------------------------------------------------------------
    Основная задача состояния - показывать на карте адрес, который ввел пользователь
    ---------------------------------------------------------------------------------------------
    Методы:
        handle_dialog(res, req) - основная функция для взаимодействия с пользователем.
        get_image(geo_name) - возвращает image_id загруженной картинки Яндекс.Карт.
        delete_user_requests(ignore_id) - удаляет предыдущие картинки пользователей из памяти навыка.
        __get_all_images() - возвращает список всех изображений в памяти навыка.
        __get_place_coordinates() - возвращает координаты места, введеного текстом.
        __get_place_image() - возвращает фотографию места по координатам.
        __upload_to_resources() - загружает фотографию места в память навыка и вовзращает id.
    ------------------------------------------------------------------------------------------------
    """

    def handle_dialog(self, res: AliceResponse, req: AliceRequest):
        if req.geo_names:
            image = {
                'type': "BigImage",
                'image_id': None,
                'title': 'Вот это место на карте',
            }

            geo_name = ' '.join(val for key, val in req.geo_names[0].items())
            image_id, callback = self.get_image(geo_name)
            if callback == 'OK':
                image['image_id'] = image_id
                res.set_image(image)
                self.delete_user_requests(image_id)
            else:
                res.set_answer('Произошла ошибка')
        if set(req.words).intersection(EXIT_WORDS):
            self.delete_user_requests()
        res.set_answer('Введи любое место и я тебе его покажу!')

    def get_image(self, geo_name):
        coordinates, callback = self.__get_place_coordinates(geo_name)
        if callback == 'Error':
            return None, 'Error'

        image_url, callback = self.__get_place_image(coordinates)
        if callback == 'Error':
            return None, 'Error'

        image_id, callback = self.__upload_to_resources(image_url)
        if callback == 'Error':
            return None, 'Error'

        return image_id, 'OK'

    def delete_user_requests(self, ignore_id=None):
        delete_request = 'https://dialogs.yandex.net/api/v1/skills/' \
                         f'{SKILL_ID}/images/'
        headers = {'Authorization': f'OAuth {ACCESS_TOKEN}'}
        for image in self.__get_all_images():
            if image['id'] != ignore_id:
                requests.delete(f'{delete_request}{image["id"]}', headers=headers)

    @staticmethod
    def __get_all_images():
        get_request = 'https://dialogs.yandex.net/api/v1/skills/' \
                      f'{SKILL_ID}/images'

        headers = {'Authorization': F'OAuth {ACCESS_TOKEN}'}

        response = requests.get(get_request, headers=headers)
        if response:
            return response.json()['images']

    @staticmethod
    def __get_place_coordinates(geo_name):
        geocode_request = 'https://geocode-maps.yandex.ru/1.x/'
        geocode_params = {
            'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
            'geocode': geo_name,
            'format': 'json'
        }

        response = requests.get(geocode_request, params=geocode_params)
        if response:
            json_response = response.json()
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]
            coordinates = toponym["GeoObject"]['Point']['pos']
            return coordinates, 'OK'
        return None, 'Error'

    @staticmethod
    def __get_place_image(coordinates):
        map_request = "http://static-maps.yandex.ru/1.x/"
        map_params = {
            'll': ','.join(coordinates.split()),
            'spn': '0.002,0.002',
            'l': 'sat,skl'}

        response = requests.get(map_request, params=map_params)
        if response:
            return response.url, 'OK'
        return None, 'Error'

    @staticmethod
    def __upload_to_resources(image):
        upload_request = 'https://dialogs.yandex.net/api/v1/skills/' \
                         f'{SKILL_ID}/images'
        headers = {
            'Authorization': f'OAuth {ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }

        json_req = {'url': image}
        response = requests.post(upload_request, headers=headers, json=json_req)
        if response:
            json_response = response.json()
            image_id = json_response['image']['id']
            return image_id, 'OK'

        return None, 'Error'


class HelloState(State):

    def handle_dialog(self, res: AliceResponse, req: AliceRequest):
        res.set_answer('Привет.Вы в хеллоу стэйте!')
        self.context.transition_to(ExitState())


class ExitState(State):

    def handle_dialog(self, res: AliceResponse, req: AliceRequest):
        res.set_answer('Привет. А теперь ты в экзит стейте')
        self.context.transition_to(HelloState())


# ChooseState ?
#


my_context = Context(MapsState())
