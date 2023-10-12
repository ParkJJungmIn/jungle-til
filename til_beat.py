from app_instance import app

from celery import Celery
from til_crawl import start_crawl

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['result_backend'],
        broker=app.config['broker_url']
    )
    celery.conf.update(app.config)
    return celery


app.config.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/1'
)

celery = make_celery(app)

from celery.schedules import crontab

celery.conf.beat_schedule = {
    'run-every-10-seconds': {
        'task': 'til_celery.run_start_crawl', # 모듈 이름을 수정해야 합니다.
        'schedule': 600.0,
    },
}
celery.conf.timezone = 'UTC'