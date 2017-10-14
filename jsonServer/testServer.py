#!/bin/python3

import logging

import server

logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')
logging.info("Logging started...")

args = dict()
args["ip"] = "127.0.0.1"
args["port"] = 4285
args["startAttempts"] = 20

myServer = server.server(args)
client = myServer.listen()
message = client.receive()["message"]
print(message)
client.send({"message": message})
myServer.stop()
