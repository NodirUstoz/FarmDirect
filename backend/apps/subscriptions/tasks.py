"""Celery tasks for subscription processing."""

import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def process_pending_subscriptions():
    """
    Generate subscription orders for active subscriptions whose next
    delivery date is today or has passed.  Runs daily via Celery Beat.
    """
    from .models import SubscriptionBox, SubscriptionOrder, SubscriptionOrderItem
    from apps.products.models import FarmProduct

    today = timezone.now().date()
    active_boxes = SubscriptionBox.objects.filter(
        status=SubscriptionBox.Status.ACTIVE,
        next_delivery_date__lte=today,
    ).select_related("plan", "customer").prefetch_related(
        "preferred_categories", "preferred_farms"
    )

    created_count = 0

    for box in active_boxes:
        # Build a product queryset based on preferences
        products_qs = FarmProduct.objects.filter(
            is_active=True, stock_quantity__gt=0
        )

        if box.preferred_farms.exists():
            products_qs = products_qs.filter(farm__in=box.preferred_farms.all())

        if box.preferred_categories.exists():
            products_qs = products_qs.filter(
                category__in=box.preferred_categories.all()
            )

        # Exclude unwanted items
        exclude = box.exclude_items or []
        if exclude:
            products_qs = products_qs.exclude(name__in=exclude)

        # Select items up to the plan's item count
        selected = list(products_qs.order_by("?")[: box.plan.item_count])

        if not selected:
            logger.warning(
                "No eligible products found for subscription %s", box.pk
            )
            continue

        # Create the subscription order
        sub_order = SubscriptionOrder.objects.create(
            subscription=box,
            delivery_date=today,
            total=box.plan.price,
        )

        for product in selected:
            SubscriptionOrderItem.objects.create(
                subscription_order=sub_order,
                product=product,
                product_name=product.name,
                quantity=1,
                price=product.price,
            )

        # Advance the next delivery date
        frequency_delta = {
            "weekly": timedelta(weeks=1),
            "biweekly": timedelta(weeks=2),
            "monthly": timedelta(days=30),
        }
        box.next_delivery_date = today + frequency_delta.get(
            box.plan.frequency, timedelta(weeks=1)
        )
        box.save(update_fields=["next_delivery_date", "updated_at"])

        # Notify the customer
        _send_subscription_order_email.delay(str(sub_order.pk))
        created_count += 1

    logger.info("Created %d subscription orders.", created_count)
    return created_count


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def _send_subscription_order_email(self, order_id):
    """Send a notification email for a new subscription order."""
    from .models import SubscriptionOrder

    try:
        order = SubscriptionOrder.objects.select_related(
            "subscription__customer", "subscription__plan"
        ).get(pk=order_id)
    except SubscriptionOrder.DoesNotExist:
        logger.error("SubscriptionOrder %s not found.", order_id)
        return

    customer = order.subscription.customer
    plan = order.subscription.plan

    items_summary = "\n".join(
        f"  - {item.product_name}" for item in order.items.all()
    )

    subject = f"FarmDirect -- Your {plan.name} Box is Being Prepared!"
    body = (
        f"Hi {customer.first_name},\n\n"
        f"Great news! Your {plan.name} subscription box for "
        f"{order.delivery_date} is being prepared.\n\n"
        f"Items in this box:\n{items_summary}\n\n"
        f"Total: ${order.total}\n\n"
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
    except Exception as exc:
        logger.exception(
            "Failed to send subscription order email for %s", order_id
        )
        raise self.retry(exc=exc)
