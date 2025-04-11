import pika
import time
import logging
# from sqlmodel import create_engine, Session
from database.database import SessionLocal
from app.models.llm import prediction_task, task_status

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


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

connection = pika.BlockingConnection(connection_params)
channel = connection.channel()
queue_name = 'ml_task_queue'
channel.queue_declare(queue=queue_name) 



def callback(ch, method, properties, body):
    session = SessionLocal()
    try:
        data = json.loads(body)
        task_id = data['task_id']
        input_data = data['input_data']
        task = session.query(prediction_task).get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return
        if not input_data:
            raise ValueError("Input data is empty")
        result = f"Processed: {input_data}"
        task.result = result
        task.status = task_status.COMPLETED.value
        session.commit()
        logger.info(f"Task {task_id} processed")
    except Exception as e:
        logger.error(f"Error processing task {task_id}: {str(e)}")
        if task:
            task.status = task_status.FAILED.value
            task.result = str(e)
            session.commit()
    finally:
        session.close()
        ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=False 
)

logger.info('Waiting for messages. To exit, press Ctrl+C')
channel.start_consuming()