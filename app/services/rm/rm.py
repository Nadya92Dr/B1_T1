import pika


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

def send_task(message:str):
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    
   
    queue_name = 'ml_task_queue'

   
    channel.queue_declare(queue=queue_name)  

    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=message
    )

  
    connection.close()