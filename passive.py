import pika
import sys
import os
import threading

IP = 'localhost'
server = ''

cred = pika.PlainCredentials('admin', 'password')
connection = pika.BlockingConnection(pika.ConnectionParameters(host = "localhost",port=5672,credentials=cred))
channel = connection.channel()


client_params = {"x-ha-policy": "all"}
channel.exchange_declare(exchange='logs', exchange_type='fanout')

def broadcast(body, props):
    channel.basic_publish(exchange='logs', routing_key='',body=body, properties= pika.BasicProperties(correlation_id=props.correlation_id,delivery_mode = 2))

def from_active():
      try:
        connection2 = pika.BlockingConnection(pika.ConnectionParameters(host = "active",port=5672,credentials=cred))
        channel2 = connection2.channel()
        channel2.queue_declare(queue='active-passive',durable=True,arguments=client_params)
        def callback(ch, method, properties, body):
             print(" [x] %s" % body.decode())
        channel2.basic_consume(
            queue='active-passive', on_message_callback=callback, auto_ack=True)
        channel2.start_consuming()
      except:
        print("Active server has crashed!")

def from_client():
    channel.queue_declare(queue='hello',durable=True,arguments=client_params)
    def callback(ch, method, properties, body):
        print(" [x] %s" % body.decode())
        broadcast(body, properties)
    channel.basic_consume(queue='hello', on_message_callback=callback, auto_ack=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        receive_from_active = threading.Thread(target=from_active)
        receive_from_active.daemon = True
        receive_from_active.start()
        receive_from_client = threading.Thread(target=from_client)
        receive_from_client.daemon = True
        receive_from_client.start()
        receive_from_active.join()
        receive_from_client.join()

    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
