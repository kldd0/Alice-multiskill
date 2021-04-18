from flask import Flask, request
import logging
from context_module import Context, HelloState
from alice_module import *

# базовое логирование (надо улучшить)
logging.basicConfig(
    filename='logs.log',
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    level=logging.DEBUG
)

app = Flask(__name__)
cnt = Context(HelloState())


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Req: {request.json}')

    alice_req = AliceRequest(request.json)
    alice_resp = AliceResponse(alice_req)
    cnt.handle_dialog(alice_resp, alice_req)
    logging.info(f'Resp: {alice_resp}')
    return alice_resp.to_json()


if __name__ == "__main__":
    app.run(port=8989)
