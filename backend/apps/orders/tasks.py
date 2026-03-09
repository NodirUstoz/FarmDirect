"""Celery tasks for order processing."""

import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_confirmation(self, order_id):
    """Send an order confirmation email to the customer."""
    from .models import Order

    try:
        order = Order.objects.select_related("customer").prefetch_related(
            "items"
        ).get(pk=order_id)
    except Order.DoesNotExist:
        logger.error("Order %s not found for confirmation email.", order_id)
        return

    customer = order.customer
    items_summary = "\n".join(
        f"  - {item.product_name} x{item.quantity} @ ${item.product_price}"
        for item in order.items.all()
    )

    subject = f"FarmDirect -- Order Confirmation #{order.order_number}"
    body = (
        f"Hi {customer.first_name},\n\n"
        f"Thank you for your order!\n\n"
        f"Order Number: {order.order_number}\n"
        f"Items:\n{items_summary}\n\n"
        f"Subtotal: ${order.subtotal}\n"
        f"Delivery Fee: ${order.delivery_fee}\n"
        f"Tax: ${order.tax}\n"
        f"Total: ${order.total}\n\n"
        f"We will notify you when your order is being prepared.\n\n"
        f"Best regards,\n"
        f"The FarmDirect Team"
    )

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[customer.email],
            fail_silently=False,
        )
        logger.info(
            "Order confirmation sent for %s to %s",
            order.order_number,
            customer.email,
        )
    except Exception as exc:
        logger.exception("Failed to send order confirmation for %s", order.order_number)
        raise self.retry(exc=exc)


@shared_task
def send_delivery_reminders():
    """
    Send a reminder to customers whose deliveries are scheduled for tomorrow.
    Runs daily via Celery Beat.
    """
    from .models import DeliverySchedule

    tomorrow = timezone.now().date() + timedelta(days=1)
    schedules = DeliverySchedule.objects.filter(
        scheduled_date=tomorrow, is_confirmed=True
    ).select_related("order__customer")

    sent_count = 0
    for schedule in schedules:
        customer = schedule.order.customer
        subject = f"FarmDirect -- Delivery Tomorrow for Order #{schedule.order.order_number}"
        body = (
            f"Hi {customer.first_name},\n\n"
            f"Just a reminder that your delivery for order "
            f"#{schedule.order.order_number} is scheduled for tomorrow "
            f"({schedule.scheduled_date}) during the "
            f"{schedule.get_time_slot_display()} window.\n\n"
            f"Best regards,\n"
            f"The FarmDirect Team"
        )
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[customer.email],
                fail_silently=False,
            )
            sent_count += 1
        except Exception:
            logger.exception(
                "Failed to send delivery reminder for order %s",
                schedule.order.order_number,
            )

    logger.info("Sent %d delivery reminders for %s.", sent_count, tomorrow)
    return sent_count


@shared_task
def auto_cancel_unpaid_orders():
    """Cancel orders that remain unpaid for more than 24 hours."""
    from .models import Order

    cutoff = timezone.now() - timedelta(hours=24)
    stale_orders = Order.objects.filter(
        status=Order.Status.PENDING,
        paid_at__isnull=True,
        created_at__lt=cutoff,
    )

    cancelled_count = 0
    for order in stale_orders:
        # Restore stock
        for item in order.items.all():
            if item.product:
                item.product.stock_quantity += item.quantity
                item.product.save(update_fields=["stock_quantity"])
        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status", "updated_at"])
        cancelled_count += 1

    logger.info("Auto-cancelled %d unpaid orders older than 24h.", cancelled_count)
    return cancelled_count
