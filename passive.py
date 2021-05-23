#!/usr/bin/env python
import pika
import sys,os
import time


def broadcast(channel,body, props):
    channel.basic_publish(exchange='logs', routing_key='',body=body, properties=                                                                             pika.BasicProperties(
        correlation_id=props.correlation_id,delivery_mode = 2))


def main():
    while(1):
        time.sleep(1)
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='active',port=5672,credentials=pika.PlainCredentials("admin","password"),socket_timeout=10000))
            print('Connected to Active in check Channel')
        except pika.exceptions.AMQPConnectionError:
            print('Connected to Passive in check Channel')
            connection = pika.BlockingConnection(pika.ConnectionParameters(host = "localhost",port=5672,credentials=pika.PlainCredentials("admin","password"),socket_timeout=10000))
            break

    channel = connection.channel()
    channel.exchange_declare(exchange='logs', exchange_type='fanout')
    channel.queue_declare(queue='hello',durable=True)

    def callback(channel, method,properties, body):
        print(" [x] %s" % body.decode())
        broadcast(channel,body, properties)

    channel.basic_consume(
        queue='hello', on_message_callback=callback, auto_ack=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:

        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
