from flask import Flask, request
import logging

from state import my_context
from alice import AliceRequest, AliceResponse

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f"Request {request.json}")

    alice_request = AliceRequest(request.json)
    alice_response = AliceResponse(alice_request)

    my_context.handle_dialog(alice_response, alice_request)

    logging.info(f"Response {alice_response}")
    return alice_response.to_json()


if __name__ == '__main__':
    app.run(port=5000)
