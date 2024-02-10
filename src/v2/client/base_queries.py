import logging
from enum import Enum

from httpx import AsyncClient, Response

from .wrappers import log_and_raise_if_non_200, retry_on_failed_request

logger = logging.getLogger(__name__)


class Method(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


async def _call(
    method: Method,
    url: str,
    *args,
    **kwargs,
) -> Response:
    """Make a http request"""
    async with AsyncClient() as client:
        response = await client.request(method, url, *args, **kwargs)
    return response


@log_and_raise_if_non_200
@retry_on_failed_request(
    max_attempts=3,
    backoff_factor=1,
)
async def get(
    url: str,
    *args,
    **kwargs,
) -> Response:
    """Send a GET request to a server. If use_cache is True, then the cached version of
    the function will be used.

    Args:
        url (str): A url of a resource on which to perform a GET action.

    Returns:
        Response: A successful response from the server.
    """
    return await _call(Method.GET, url, *args, **kwargs)


@log_and_raise_if_non_200
@retry_on_failed_request(
    max_attempts=3,
    backoff_factor=1,
)
async def post(
    url: str,
    *args,
    **kwargs,
) -> Response:
    """Send a POST request to a server. If use_cache is True, then the cached version of
    the function will be used.

    Args:
        url (str): A url of a resource on which to perform a POST action.

    Returns:
        Response: A successful response from the server.
    """
    return await _call(Method.POST, url, *args, **kwargs)


@log_and_raise_if_non_200
@retry_on_failed_request(
    max_attempts=3,
    backoff_factor=1,
)
async def put(
    url: str,
    *args,
    **kwargs,
) -> Response:
    """Send a PUT request to a server. If use_cache is True, then the cached version of
    the function will be used.

    Args:
        url (str): A url of a resource on which to perform a PUT action.
    Returns:
        Response: A successful response from the server.
    """
    return await _call(Method.PUT, url, *args, **kwargs)


@log_and_raise_if_non_200
@retry_on_failed_request(
    max_attempts=3,
    backoff_factor=1,
)
async def patch(
    url: str,
    *args,
    **kwargs,
) -> Response:
    """Send a PATCH request to a server. If use_cache is True, then the cached version
    of the function will be used.

    Args:
        url (str): A url of a resource on which to perform a PATCH action.
    Returns:
        Response: A successful response from the server.
    """
    return await _call(Method.PATCH, url, *args, **kwargs)


@log_and_raise_if_non_200
@retry_on_failed_request(
    max_attempts=3,
    backoff_factor=1,
)
async def delete(
    url: str,
    *args,
    **kwargs,
) -> Response:
    """Send a DELETE request to the server. Does not use caching.

    Args:
        url (str): A url of a resource on which to perform a DELETE action.

    Returns:
        Response: A successful response from the server.
    """
    return await _call(Method.DELETE, url, *args, **kwargs)
