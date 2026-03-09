"""
Celery configuration for FarmDirect project.
"""

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

app = Celery("farmdirect")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# ---------------------------------------------------------------------------
# Periodic task schedule
# ---------------------------------------------------------------------------
app.conf.beat_schedule = {
    "process-pending-subscriptions": {
        "task": "apps.subscriptions.tasks.process_pending_subscriptions",
        "schedule": crontab(hour=6, minute=0),  # Daily at 6 AM UTC
    },
    "send-delivery-reminders": {
        "task": "apps.orders.tasks.send_delivery_reminders",
        "schedule": crontab(hour=8, minute=0),  # Daily at 8 AM UTC
    },
    "update-seasonal-availability": {
        "task": "apps.products.tasks.update_seasonal_availability",
        "schedule": crontab(hour=0, minute=0, day_of_week=1),  # Weekly on Monday
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Verify Celery worker is operational."""
    print(f"Request: {self.request!r}")
