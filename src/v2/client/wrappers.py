"""
Implementation adapted from:
https://github.com/encode/httpx/issues/108#issuecomment-1434439481
"""

import asyncio
import logging
from datetime import datetime
from http import HTTPStatus
from typing import Any, Awaitable, Callable, Mapping, Union

import httpx

logger = logging.getLogger(__name__)

RETRYABLE_STATUS_CODES = frozenset(
    [
        HTTPStatus.TOO_MANY_REQUESTS,
        HTTPStatus.BAD_GATEWAY,
        HTTPStatus.SERVICE_UNAVAILABLE,
        HTTPStatus.GATEWAY_TIMEOUT,
    ]
)


# wrapper that raises on error response from httpx call and logs things as well
def log_and_raise_if_non_200(func: Callable[[Any], Awaitable[httpx.Response]]):
    async def wrapper(*args, **kwargs):
        response = await func(*args, **kwargs)
        # log request/response information
        logger.debug(
            f"{response.request.method} {response.request.url} returned {response.status_code}. {response.elapsed} elapsed. |\n"  # noqa
            + f"REQ HEADERS: {response.request.headers} |\n"
            + f"REQ BODY: {response.request.content} |\n"
            + f"RESP HEADERS: {response.headers} |\n"
            + f"RESPONSE: {response.text}"
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Error making {response.request.method} request to {response.request.url}: {response.status_code}"  # noqa
            )
            raise e
        return response

    return wrapper


def retry_on_failed_request(
    max_attempts: int = 3,
    max_backoff_wait: float = 30,
    backoff_factor: float = 0.1,
):
    """Decorator to retry a request if it fails.

    Args:
        max_attempts (int, optional): _description_. Defaults to 3.
        max_backoff_wait (float, optional): _description_. Defaults to 30.
        backoff_factor (float, optional): _description_. Defaults to 0.1.
    """

    def wrap(fn: Callable[..., Awaitable[httpx.Response]]):
        async def wrapper(*args, **kwargs):
            remaining_attempts = max_attempts
            attempts_made = 0
            while True:
                if attempts_made > 0:
                    await asyncio.sleep(
                        _calculate_sleep(
                            attempts_made,
                            {},
                            max_backoff_wait,
                            backoff_factor,
                        )
                    )
                response = await fn(*args, **kwargs)
                if (
                    remaining_attempts < 1
                    or response.status_code not in RETRYABLE_STATUS_CODES
                ):
                    return response
                attempts_made += 1
                remaining_attempts -= 1
                logger.warning(
                    f"Retrying {response.request.method} request to {response.url}. Received {response.status_code} response. Attempts made: {attempts_made}, Attempts remaining: {remaining_attempts}"  # noqa
                )

        return wrapper

    return wrap


def _calculate_sleep(
    attempts_made: int,
    headers: Union[httpx.Headers, Mapping[str, str]],
    max_backoff_wait: float = 30,
    backoff_factor: float = 0.1,
) -> float:
    # Retry-After
    # The Retry-After response HTTP header indicates how long the user agent should
    # wait before making a follow-up request. There are three main cases this header
    # is used:
    # - When sent with a 503 (Service Unavailable) response, this indicates how
    #   long the service is expected to be unavailable.
    # - When sent with a 429 (Too Many Requests) response, this indicates how long
    #   to wait before making a new request.
    # - When sent with a redirect response, such as 301 (Moved Permanently), this
    #   indicates the minimum time that the user agent is asked to wait before
    #   issuing the redirected request.
    retry_after_header = (headers.get("Retry-After") or "").strip()
    if retry_after_header:
        if retry_after_header.isdigit():
            return float(retry_after_header)
        try:
            parsed_date = datetime.fromisoformat(
                retry_after_header
            ).astimezone()  # converts to local time
            diff = (parsed_date - datetime.now().astimezone()).total_seconds()
            if diff > 0:
                return min(diff, max_backoff_wait)
        except ValueError:
            pass
    backoff = backoff_factor * (2 ** (attempts_made - 1))
    return min(backoff, max_backoff_wait)
