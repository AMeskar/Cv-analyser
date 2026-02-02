"""Structured logging configuration."""
import logging
import sys
import structlog
from opentelemetry import trace


def configure_logging(service_name: str, debug: bool = False):
    """Configure structured logging with OpenTelemetry trace context."""
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.DEBUG if debug else logging.INFO,
    )
    
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO if not debug else logging.DEBUG),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Add trace context to logs
    def add_trace_context(logger, method_name, event_dict):
        span = trace.get_current_span()
        if span and span.get_span_context().is_valid:
            ctx = span.get_span_context()
            event_dict["trace_id"] = format(ctx.trace_id, "032x")
            event_dict["span_id"] = format(ctx.span_id, "016x")
        return event_dict
    
    structlog.configure(
        processors=structlog.get_config()["processors"] + [add_trace_context],
    )


def get_logger(name: str):
    """Get a structured logger."""
    return structlog.get_logger(name)
