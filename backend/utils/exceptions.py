"""Custom exception handling for the FarmDirect API."""

import logging

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that normalises all error responses to a
    consistent shape:

        {
            "error": true,
            "message": "...",
            "details": { ... }  // optional
        }
    """

    # Convert Django ValidationError to DRF ValidationError
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, "message_dict"):
            data = exc.message_dict
        elif hasattr(exc, "messages"):
            data = {"non_field_errors": exc.messages}
        else:
            data = {"non_field_errors": [str(exc)]}

        return Response(
            {"error": True, "message": "Validation error.", "details": data},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Let DRF handle the exception first
    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            "error": True,
            "message": _extract_message(response.data),
        }
        if isinstance(response.data, dict):
            custom_data["details"] = response.data
        response.data = custom_data
        return response

    # Unhandled exceptions -- log and return 500
    logger.exception(
        "Unhandled exception in %s",
        context.get("view", "unknown view"),
        exc_info=exc,
    )

    return Response(
        {
            "error": True,
            "message": "An unexpected error occurred. Please try again later.",
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _extract_message(data):
    """Try to pull a human-readable top-level message from DRF error data."""
    if isinstance(data, str):
        return data
    if isinstance(data, list) and data:
        return str(data[0])
    if isinstance(data, dict):
        if "detail" in data:
            return str(data["detail"])
        if "non_field_errors" in data:
            errors = data["non_field_errors"]
            if isinstance(errors, list) and errors:
                return str(errors[0])
        # Return the first field error
        for key, value in data.items():
            if isinstance(value, list) and value:
                return f"{key}: {value[0]}"
            if isinstance(value, str):
                return f"{key}: {value}"
    return "Request could not be processed."
