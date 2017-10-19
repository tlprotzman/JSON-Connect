#!/bin/python3

import logging
import threading 

import jsonServer as server

def getMessage(client):
    message = client.receive()["message"]
    print(message)
    client.send({"message":message})
    return


logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')
logging.info("Logging started...")

args = dict()
args["ip"] = "127.0.0.1"
args["port"] = 4285
args["startAttempts"] = 20


threadPool = list()
myServer = server.server(args)
running = True
while running:
    client = myServer.listen()
    t = threading.Thread(target=getMessage, args=(client,))
    t.start()
    threadPool.append(t)
    running = False

for thread in threadPool:
    thread.join()

myServer.stop()

