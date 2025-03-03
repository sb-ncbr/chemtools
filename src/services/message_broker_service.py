from celery import Celery

from conf.settings import RabbitMQSettings


class MessageBrokerService:
    def __init__(self, rabbitmq_settings: RabbitMQSettings):
        self.celery_worker = Celery(
            "worker",
            broker=rabbitmq_settings.rabbitmq_url,
            task_queues={
                "free_queue": {
                    "exchange": "free_queue",
                    "routing_key": "free_queue",
                },
                "pipeline_queue": {
                    "exchange": "pipeline_queue",
                    "routing_key": "pipeline_queue",
                },
            },
            broker_connection_retry_on_startup=True,
            worker_prefetch_multiplier=1,
        )

    def send_calculation_message(self, *args, _queue: str, **kwargs):
        self.celery_worker.send_task("worker.calculation_task", queue=_queue, args=args, kwargs=kwargs)
