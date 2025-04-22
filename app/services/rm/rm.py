import pika
import json
from sqlmodel import Session

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


def setup_result_consumer():
    def callback(ch, method, properties, body):
        data = json.loads(body)
        with Session() as session:
            task = session.get(prediction_task, data['task_id'])
            task.status = data['status']
            task.result = data.get('result')
            session.commit()
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    channel.basic_consume(
        queue='result_queue',
        on_message_callback=callback,
        auto_ack=True
    )
    