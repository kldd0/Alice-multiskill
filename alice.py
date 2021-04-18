import json


class AliceRequest:
    """   Класс AliceRequest предназначен для реализации удобного интерфейса
   взаимодействия с запросом Алисы.
    ------------------------------------------------------------------------------------
    Задача класса - удобно предоставлять доступ к компонентам запроса пользователя Алисы.
    --------------------------------------------------------------------------------------
    Методы
        user_id - возвращает user_id пользователя, который отправил запрос.
        words - возвращает все слова, произнесенные пользователем.
        is_new_session - возвращает True если пользователь только начал диалог, иначе False.
        session - возвращает текущую сессия пользователя.
        version - возвращает текушую версию Алисы.

        names - возвращает полный список имен, которые написал пользователь.
        geo_names - возвращает список гео объектов, которые написал пользователь.
        numbers - возращает список чисел, которые написал пользователь.
        dates  - возвращает список дат, которые написал пользователь.

        foreign_words - возвращает список слов, написанных не на русском языке, для переводчика."""

    def __init__(self, request) -> None:
        self._request = request

    def __get_entity(self, entity_type) -> list:
        """Функця для получения определенных сущностей в зависимости от аргумента функции.
        -----------------------------------------------------------------------------------
        entity_type - тип сущности, которую нужно получить
        Типы сущностей:
            YANDEX.FIO
            YANDEX.GEO
            YANDEX.NUMBER
            YANDEX.DATETIME
        ----------------------------------------------------------------------------------------
        Возвращает список сущностей, у которых тип совпадает с заданным, или пустой список, если
        таких сущностей не найдено."""
        entities = []
        for entity in self._request['request']['nlu']['entities']:
            if entity['type'] == entity_type:
                entities.append(entity['value'])
        return entities

    @property
    def user_id(self) -> str:
        return self.session['user_id']

    @property
    def words(self) -> list:
        return self._request['request']['nlu']['tokens']

    @property
    def is_new_session(self) -> bool:
        return bool(self._request['session']['new'])

    @property
    def session(self) -> dict:
        return self._request['session']

    @property
    def version(self) -> str:
        return self._request['version']

    @property
    def names(self) -> list:
        return self.__get_entity('YANDEX.FIO')

    @property
    def geo_names(self) -> list:
        return self.__get_entity('YANDEX.GEO')

    @property
    def numbers(self) -> list:
        return self.__get_entity('YANDEX.NUMBER')

    @property
    def dates(self) -> list:
        return self.__get_entity('YANDEX.DATETIME')

    @property
    def foreign_words(self) -> list:
        """Функция возвращает список слов, написанных не на русском языке, или пустой список,
        если таких слов не найдено."""
        foreign = []
        for word in self._request['request']['original_utterance'].split():
            if not 1039 < (ord(word[0])) < 1105:
                foreign.append(word)
        return foreign

    def __str__(self):
        return json.dumps(self._request)

    def __repr__(self):
        return self.__str__()


class AliceResponse:
    """    Класс AliceResponse предназначен для реализации удобного интерфейса взаимодействия
    с ответом Алисы.
    -------------------------------------------------------------------------------------
    Задача класса - предоставлять удобный доступ к компонентам ответа Алисы.
    -------------------------------------------------------------------------------------
    Методы
        set_answer() - задает ответ Алисы в текстовом формате.
        end_session() - закрывает сессию с пользователем.
        to_json() - возвращает ответ Алисы в json формате.
        set_suggests() - прикрепляет варианты ответа для пользователя (кнопки).
        set_image() - прикрепляет картинку к ответу.
    """
    def __init__(self, request: AliceRequest):
        """Конструктор класса принимает аргумента класса AliceRequest для установки версии и сессии
        для ответа."""
        self._response = {
            "version": request.version,
            "session": request.session,
            "response": {
                "end_session": False
            }
        }

    def set_answer(self, answer):
        self._response['response']['text'] = answer

    def end_session(self):
        self._response['response']['end_session'] = True

    def to_json(self):
        return json.dumps(self._response)

    def set_suggests(self, suggests):
        self._response['response']['buttons'] = suggests

    def set_image(self, image):
        self._response['response']['card'] = image

    def __str__(self):
        return self.to_json()

    def __repr__(self):
        return self.to_json()
