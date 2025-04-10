import pika
import json

connection_params = pika.ConnectionParameters(
    host='rabbitmq',  
    port=5672,         
    virtual_host='/',   
    credentials=pika.PlainCredentials(
        username='rmuser',  
        password='rmpassword'  
    ),
    heartbeat=30,
    blocked_connection_timeout=2
)

def send_task(task_data:dict):
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    
    channel.queue_declare(queue='ml_task_queue')  
    channel.basic_publish(
        exchange='',
        routing_key='ml_task_queue',
        body=json.dumps(task_data).encode('utf-8')
    )
    connection.close()