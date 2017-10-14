import logging

import client

logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')
logging.info("Logging started...")

username = ("tristan", "test")

args = dict()
args["ip"] = "127.0.0.1"
args["port"] = 4285
args["user"] = username

server = client.client(args)
server.send({"message":"Hello World!"})
message = server.receive()
print(message["message"])