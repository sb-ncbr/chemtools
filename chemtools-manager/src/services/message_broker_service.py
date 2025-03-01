from celery import Celery

from conf.settings import RabbitMQSettings


class MessageBrokerService:
    def __init__(self, rabbitmq_settings: RabbitMQSettings):
        self.celery_worker = Celery(
            'worker',
            broker=rabbitmq_settings.rabbitmq_url,
            worker_prefetch_multiplier=1,
            task_queues={
                "bunny_tube": {
                    "exchange": "bunny_tube",
                    "routing_key": "bunny_tube",
                    "queue_arguments": {"x-max-priority": 2},
                }
            },
        )
        self.queue_name = "bunny_tube"

    def send_message(self, *args, _priority: int = 0, **kwargs):
        self.celery_worker.send_task(
            f"worker.chemtool_task", queue=self.queue_name, priority=_priority, args=args, kwargs=kwargs
        )
