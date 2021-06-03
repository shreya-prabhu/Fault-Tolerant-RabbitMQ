import os
import sys
import pika
import threading
import uuid

def callback(ch,method,properties,body):
    if corr_id!=properties.correlation_id:
        print("    %s" % body.decode())

def receive_active():
    connection2 = pika.BlockingConnection(pika.ConnectionParameters(host = "active",port=5672,credentials=pika.PlainCredentials("admin","password"),socket_timeout=10000))
    channel_receive = connection2.channel()
    result = channel_receive.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel_receive.exchange_declare('logs','fanout')
    channel_receive.queue_bind(exchange='logs', queue=queue_name)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel_receive.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    try:
        channel_receive.start_consuming()   #catch this
    except:
        os._exit(0)

def send_active():
    global corr_id,connection1,channel_send
    connection1 = pika.BlockingConnection(pika.ConnectionParameters(host='active',port=5672,credentials=pika.PlainCredentials("admin","password"),socket_timeout=10000))
    channel_send = connection1.channel()
    corr_id = str(uuid.uuid4())
    channel_send.queue_declare(queue='hello',durable = True)
    first = username + " has entered the chat"
    channel_send.basic_publish(exchange='', routing_key='hello', properties=pika.BasicProperties(correlation_id=corr_id),body=first)
    while(True):
        str1 = input()
        message = '[{}] : {}'.format(username, str1)
        channel_send.basic_publish(exchange='', routing_key='hello', properties=pika.BasicProperties(correlation_id=corr_id), body=message)

def receive_passive():
    connection2 = pika.BlockingConnection(pika.ConnectionParameters(host = "passive",port=5672,credentials=pika.PlainCredentials("admin","password"),socket_timeout=10000))
    channel_receive = connection2.channel()
    result = channel_receive.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel_receive.exchange_declare('logs','fanout')
    channel_receive.queue_bind(exchange='logs', queue=queue_name)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel_receive.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel_receive.start_consuming()

def send_passive():
    global corr_id,connection1,channel_send
    connection1 = pika.BlockingConnection(pika.ConnectionParameters(host='passive',port=5672,credentials=pika.PlainCredentials("admin","password"),socket_timeout=10000))
    channel_send = connection1.channel()
    corr_id = str(uuid.uuid4())
    channel_send.queue_declare(queue='hello',durable = True)
    first = username + " has entered the chat"
    channel_send.basic_publish(exchange='', routing_key='hello', properties=pika.BasicProperties(correlation_id=corr_id),body=first)
    while(True):
        str1 = input()
        message = '[{}] : {}'.format(username, str1)
        channel_send.basic_publish(exchange='', routing_key='hello', properties=pika.BasicProperties(correlation_id=corr_id), body=message)

def client():
    print("Enter a username for the client")
    global username
    username = input()

    global connection1,connection2,channel_send,channel_receive
    active_child = os.fork()
    if active_child == 0:
        try:
            connection1 = pika.BlockingConnection(pika.ConnectionParameters(host='active',port=5672,credentials=pika.PlainCredentials("admin","password"),socket_timeout=10000))
            print('Connected to Active Server',os.getpid(),os.getppid())

            try:
                send_thread = threading.Thread(target=send_active)
                send_thread.daemon = True
                send_thread.start()
                receive_thread = threading.Thread(target=receive_active)
                receive_thread.daemon = True
                receive_thread.start()
            except:
                print('Channel broke')
                os._exit(0)

        except : #Does not connect in beginning
            print('excp in client')
            print('Failed to Connect to Active Server')
            os._exit(0)


    else:
        try:

            os.wait()
            print('Connected to Passive Server',os.getpid())
            send_thread = threading.Thread(target=send_passive)
            send_thread.daemon = True
            send_thread.start()
            receive_thread = threading.Thread(target=receive_passive)
            receive_thread.daemon = True
            receive_thread.start()
        except:
            sys.exit(0)

def main():
    client()

if __name__ == '__main__':
    try:
        main()
        while(1):
            pass
    except KeyboardInterrupt:
            print('You have exited')
            last = username + "\thas left the chat"
            channel_send.basic_publish(exchange='', routing_key='hello', properties=pika.BasicProperties(delivery_mode=2,correlation_id=corr_id), body=last)
            os._exit(0)