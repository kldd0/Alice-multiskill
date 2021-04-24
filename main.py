import logging

from flask import Flask, request

from alice_module import *
from context_module import Context, HelloState

logging.basicConfig(
    filename="logs.log",
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    level=logging.INFO,
)

app = Flask(__name__)
sessions = {}


@app.route("/post", methods=["POST"])
def main():
    logging.info(f"Req: {request.json}")

    alice_req = AliceRequest(request.json)
    alice_resp = AliceResponse(alice_req)
    if alice_req.is_new_session:
        cnt = Context(HelloState())
        sessions[alice_req.user_id] = cnt
        cnt.handle_dialog(alice_resp, alice_req)
        logging.info(f"Resp: {alice_resp}")
        return alice_resp.to_json()
    sessions[alice_req.user_id].handle_dialog(alice_resp, alice_req)
    logging.info(f"Resp: {alice_resp} {sessions}")
    return alice_resp.to_json()


if __name__ == "__main__":
    app.run(port=8989)
