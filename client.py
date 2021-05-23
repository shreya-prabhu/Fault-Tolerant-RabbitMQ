#!/usr/bin/env python
# 1 thread for each channel
import pika
import pika.exceptions as Exceptions
import sys
import threading
import uuid

def callback(ch, method, properties, body):
    if corr_id != properties.correlation_id:
        print(" [x] %s" % body.decode())

def receive():
    global channel_receive
    try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='active',port=5672,credentials=pika.PlainCredentials("admin","password"),socket_timeout=10000))
            print('Connected to Active in Recieve Channel')
    except pika.exceptions.ConnectionClosedByBroker:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host = "passive",port=5672,credentials=pika.PlainCredentials("admin","password"),socket_timeout=10000))
            print('Connected to Passive in Recieve Channel')
    print("Thread receive dint die")
    channel_receive = connection.channel()
    result = channel_receive.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel_receive.exchange_declare('logs','fanout')
    channel_receive.queue_bind(exchange='logs', queue=queue_name)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel_receive.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel_receive.start_consuming()
    # while(1):
    #     try:
    #         channel_receive.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    #     except Exceptions:
    #         connection = check_server()
    #         channel_receive.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    #         channel_receive.start_consuming()
    #         print('Connected to Passive in Receive Channel')

def check_server():
        global connection
        try:
                connection = pika.BlockingConnection(pika.ConnectionParameters(host='active',port=5672,credentials=pika.PlainCredentials("admin","password"),socket_timeout=10000))

        except Exceptions:

                connection = pika.BlockingConnection(pika.ConnectionParameters(host = "passive",port=5672,credentials=pika.PlainCredentials("admin","password"),socket_timeout=10000))
                active= 0
        return connection

def send():
    global active,channel_send,corr_id

    corr_id = str(uuid.uuid4())
    connection = check_server()
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='active',port=5672,credentials=pika.PlainCredentials("admin","password"),socket_timeout=10000))
        print('Connected to Active in Send Channel')
    except pika.exceptions.ConnectionClosedByBroker:

        connection = pika.BlockingConnection(pika.ConnectionParameters(host = "passive",port=5672,credentials=pika.PlainCredentials("admin","password"),socket_timeout=10000))
        print('Connected to Passive in Send Channel')

    print("Thread send dint die")
    channel_send = connection.channel()
    channel_send.queue_declare(queue='hello',durable=True)
    first = username + "\thas entered the chat"
    channel_send.basic_publish(exchange='', routing_key='hello',properties=pika.BasicProperties(delivery_mode=2,correlation_id=corr_id), body=first)

    while(True):
        str1 = input()
        message = '[{}] : {}'.format(username, str1)
        try:
            channel_send.basic_publish(exchange='', routing_key='hello', properties=pika.BasicProperties(correlation_id=corr_id), body=message)

        except pika.exceptions.ConnectionClosedByBroker:
            connection = check_server()
            channel_send.basic_publish(exchange='', routing_key='hello', properties=pika.BasicProperties(correlation_id=corr_id), body=message)
            channel_send = connection.channel()
            print('Connected to Passive in Send Channel')


def main():

    print("Enter a username for the client")
    global username
    username = input()
    send_thread = threading.Thread(target=send)
    send_thread.daemon = True
    send_thread.start()

    receive_thread = threading.Thread(target=receive)
    receive_thread.daemon = True
    receive_thread.start()



if __name__ == '__main__':

    try:
        main()
        while(1):
            pass

    except KeyboardInterrupt:

        print('You have exited')
        last = username + "\thas left the chat"
        try:
            channel_send.basic_publish(exchange='', routing_key='hello', properties=pika.BasicProperties(delivery_mode=2,correlation_id=corr_id), body=last)
            sys.exit(0)
        except pika.exceptions.StreamLostError:
            print('out of channel')
