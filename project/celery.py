from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Definindo o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('weather')

# Carregando configurações do Django no Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobrindo tarefas em todos os apps instalados
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
