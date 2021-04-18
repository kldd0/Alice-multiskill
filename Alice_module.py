import json


class AliceRequest:
    def __init__(self, request) -> None:
        self._request = request

    def __get_entity(self, entity_type) -> list:
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
    def request_string(self):
        return self._request['request']['original_utterance']

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

    def __str__(self):
        return json.dumps(self._request)

    def __repr__(self):
        return self.__str__()


class AliceResponse:
    def __init__(self, request: AliceRequest):
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
