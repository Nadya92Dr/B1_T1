import pika
import time
import logging
# from sqlmodel import create_engine, Session
from database.database import Session
from transformers import AutoModelForCausalLM, AutoTokenizer
from models.llm import prediction_task, task_status
import json


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
channel.queue_declare(queue='ml_task_queue')
channel.queue_declare(queue='result_queue')

model_name = "Qwen/Qwen2.5-0.5B-Instruct"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

prompt = "Give me a short introduction to large language model."
messages = [
    {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
    {"role": "user", "content": prompt}
]
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)
model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=512
)
generated_ids = [
    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
]

response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]



def callback(ch, method, properties, body):
    session = Session()
    task = None
    try:
        data = json.loads(body)
        task_id = data['task_id']
        input_data = data['input_data']
        llm_id = data.get("llm_id", 1)

        task = session.query(prediction_task).get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return
        
        task.status = task_status.PROCESSING
        session.commit()

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": input_data}
        ]

        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
        
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=512,
            do_sample=True
        )
        
        response = tokenizer.decode(
            generated_ids[0][len(model_inputs.input_ids[0]):],
            skip_special_tokens=True
        )

        task.result = response
        task.status = task_status.COMPLETED
        session.commit()
        
        channel.basic_publish(
            exchange='',
            routing_key='result_queue',
            body=json.dumps({
                'task_id': task_id,
                'status': task_status.COMPLETED,
                'result': response
            })
        )
        logger.info(f"Result published for task {task_id}")

    except Exception as e:
        logger.error(f"Error processing task {task_id}: {str(e)}")
        if task:
            task.status = task_status.FAILED
            task.result = f"Processing error:{str(e)}"
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