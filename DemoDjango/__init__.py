from __future__ import absolute_import, unicode_literals

# Vị trí Celery sẽ được nạp khi ứng dụng Django khởi động
from .celery_app import app as celery_app

__all__ = ('celery_app',)