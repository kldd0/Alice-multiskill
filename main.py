from flask import Flask
import logging
import json
import sys
import os

# базовое логирование (надо улучшить)
logging.basicConfig(
    filename='logs.log',
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

app = Flask(__name__)


def main():
    # работа с Алисой
    # тут будет происходить смена состояний
    app.run()


if __name__ == "__main__":
    main()
