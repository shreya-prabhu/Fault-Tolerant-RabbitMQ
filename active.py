#!/usr/bin/env python

import pika
import sys
import os
import threading
import time
import uuid

IP = 'localhost'
server = ''

cred = pika.PlainCredentials('admin', 'password')

connection = pika.BlockingConnection(pika.ConnectionParameters(host = "localhost",port=5672,credentials=cred))
channel = connection.channel()

client_params = {"x-ha-policy": "all"}
channel.exchange_declare(exchange='logs', exchange_type='fanout')

connection2 = pika.BlockingConnection(pika.ConnectionParameters(host = "passive",port=5672,credentials=cred))
channel2 = connection2.channel()


   



def broadcast(body, props):
    channel.basic_publish(exchange='logs', routing_key='',body=body, properties = pika.BasicProperties(correlation_id=props.correlation_id,delivery_mode = 2))

def sendtopassive(body, props):
    channel2.basic_publish(exchange='', routing_key='hello', properties=pika.BasicProperties(correlation_id=props.correlation_id,body=body,delivery_mode = 2))

def messages_from_clients():
    channel.queue_declare(queue='hello',durable=True,arguments=client_params)

    def callback(ch, method, properties, body):
        print(" [x] %s" % body.decode())
        broadcast(body, properties)
        #sendtopassive(body,properties)

    channel.basic_consume(
        queue='hello', on_message_callback=callback, auto_ack=True)
    print(channel.channel_number,' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:
       receive_from_clients = threading.Thread(target=messages_from_clients)
       receive_from_clients.daemon = True
       receive_from_clients.start()
       send_to_passive = threading.Thread(target=sendtopassive)
       send_to_passive.daemon = True
       send_to_passive.start()
        

    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
