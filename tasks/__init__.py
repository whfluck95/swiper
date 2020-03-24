import os

from celery import Celery

from tasks import config

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "swiper.settings")

celery_app = Celery('worker')
celery_app.config_from_object(config)
celery_app.autodiscover_tasks()
