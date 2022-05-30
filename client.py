import argparse
import json
import logging
import sys
from os.path import exists
import zmq

from _json_validators import JsonValidator

_BINDING = 'tcp://127.0.0.1:5559'
parser = argparse.ArgumentParser(
    description='Process file paths',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s')


class Client:
    def __init__(self, path):
        self.logger = logging.getLogger('CLIENT')
        self.path = path
        self.context = zmq.Context()
        self.socket_client = self.context.socket(zmq.REQ)
        self.socket_client.connect(_BINDING)
        logging.info("Client connected to server")

    def read_json_file(self) -> dict:
        with open(self.path, 'r') as f:
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError:
                logging.error("File is not valid JSON")
                sys.exit(1)

        if data.get('command_type') not in ['os', 'compute']:
            logging.error("Command type is not valid")
            sys.exit(1)
        for Validator in JsonValidator.__subclasses__():
            if Validator.meet_condition(data):
                try:
                    Validator.validate(data)
                except ValueError as e:
                    logging.error(e)
                    sys.exit(1)
                break
        return data

    def run(self) -> None:
        message = self.read_json_file()
        self.socket_client.send_json(message)
        received_message = self.socket_client.recv_json()
        result = json.dumps(received_message, indent=4)
        logging.info("Received message: %s", result)
        self.socket_client.close()


if __name__ == "__main__":
    parser.add_argument(
        "--file",
        help="send file path",
    )
    args = parser.parse_args()
    config = vars(args)
    file_path = config['file']
    if file_path:
        try:
            file_exists = exists(file_path)
            client = Client(file_path)
            client.run()
        except FileNotFoundError:
            logging.error("File not found")
            sys.exit(1)
    else:
        logging.error("File path is empty")
        sys.exit(1)

