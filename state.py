import logging
import requests
import json

from abc import abstractmethod, ABC
from alice import AliceRequest, AliceResponse


EXIT_WORDS = {'выход', 'пока', 'выйти', 'уйти', 'покинуть'}
TRANSLATE_WORDS = {'переведи', 'переведите', 'перевод'}


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


class TranslatorState(State):

    def handle_dialog(self, res: AliceResponse, req: AliceRequest):
        if set(req.words).intersection(TRANSLATE_WORDS):
            req_for_translate, lang_fr, lang_to = self.get_translate_request(req.words)
            res.set_answer(self.translate(req_for_translate, lang_fr, lang_to))

        if set(req.words).intersection(EXIT_WORDS):
            self.context.transition_to(HelloState())

    def get_translate_request(self, words: list):
        to_translate_words = self.__delete_unnecessary_words(words)
        language_from, language_to = self.__get_languages(words)
        to_translate_words = self.__delete_languages(to_translate_words, language_from, language_to)

        return ' '.join(to_translate_words), language_from, language_to

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
            if words[i] == 'с' and 'ого' in words[i + 1]:
                language_from = self.__language_to_iso(f"{words[i + 1][:-3]}ий".title())
            elif words[i] == 'на' and 'ий' in words[i + 1]:
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
            if language_from in my_words:
                my_words = my_words.replace(language_from, '')
            if language_to in my_words:
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

        return response['responseData']['translatedText']


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


my_context = Context(TranslatorState())

