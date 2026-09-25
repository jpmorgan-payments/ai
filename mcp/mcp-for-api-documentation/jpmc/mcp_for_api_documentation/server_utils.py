# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Modifications Copyright 2025 JPMorgan Chase (JPMC)
# This file has been modified from its original version.
# Significant changes include:
# - changed several naming, from AWS to JPMorgan Chase (JPMC)/Payments Developer Portal (PDP).
# - extracted read_documentation_page_raw() from read_documentation_impl() for better reuse.
# - added validate_documentation_url() as the single allowlist/SSRF guard shared by every
#   tool that dereferences a caller-supplied URL, and made read_documentation_page_raw()
#   enforce it (including on every redirect hop) instead of trusting httpx's redirect
#   follower. (RDI-159)

"""Utility functions for fetching and processing documentation pages.

This module provides helper functions for the JPMorgan Chase (JPMC)
Payments Developer Portal (PDP) API Documentation MCP Server.
"""

import httpx
import ipaddress
import os
import re
import socket
from .util import (
    extract_content_from_html,
    format_documentation_result,
    is_html_content,
)
from importlib.metadata import version
from loguru import logger
from mcp.server.fastmcp import Context
from typing import Tuple
from urllib.parse import urlparse


# Determine package version for user agent
try:
    __version__ = version('jpmc.pdp-documentation-mcp-server')
except Exception:
    from . import __version__

# Standard user agent for API requests
DEFAULT_USER_AGENT = (
    f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    f'AppleWebKit/537.36 (KHTML, like Gecko) '
    f'Chrome/91.0.4472.124 Safari/537.36 '
    f'ModelContextProtocol/{__version__} (PDP Documentation Server)'
)

# The only host any tool in this server is allowed to fetch. Every tool that
# dereferences a caller-supplied URL (read_documentation, related, ...) MUST
# route through validate_documentation_url() / read_documentation_page_raw()
# below rather than reimplementing this check, so the allowlist can't drift
# out of sync between tools again.
ALLOWED_DOC_URL_PATTERN = re.compile(r'^https?://developer\.payments\.jpmorgan\.com(/.*)?$')

# Cap on redirect hops we will follow for a single fetch.
MAX_REDIRECTS = 5


class InvalidDocumentationUrlError(ValueError):
    """Raised when a URL fails the domain allowlist or SSRF defense-in-depth checks."""


def _reject_private_address(hostname: str) -> None:
    """Resolve hostname and reject it if any resolved address is non-public.

    Defense-in-depth against DNS rebinding / misconfiguration: even though the
    allowlist restricts the host to developer.payments.jpmorgan.com, refuse to
    connect if that name (or a redirect target) ever resolves to a private,
    loopback, link-local, unspecified, reserved, or multicast address.
    """
    try:
        ip = ipaddress.ip_address(hostname)
        addresses = [ip]
    except ValueError:
        try:
            resolved = socket.getaddrinfo(hostname, None)
        except socket.gaierror as e:
            raise InvalidDocumentationUrlError(f'Could not resolve host: {hostname}') from e
        addresses = [ipaddress.ip_address(info[4][0]) for info in resolved]

    for address in addresses:
        if (
            address.is_private
            or address.is_loopback
            or address.is_link_local
            or address.is_unspecified
            or address.is_reserved
            or address.is_multicast
        ):
            raise InvalidDocumentationUrlError(
                f'Host {hostname} resolves to a disallowed address: {address}'
            )


def validate_documentation_url(url_str: str) -> None:
    """Validate a URL is safe to fetch.

    Checks for an allowlisted scheme+host, no userinfo, and no
    private/loopback/link-local resolved address.

    This is the single guard every tool that fetches a caller-supplied URL must
    call before dereferencing it. Raises InvalidDocumentationUrlError if the URL
    is not allowed.
    """
    parsed = urlparse(url_str)

    if parsed.scheme not in ('http', 'https'):
        raise InvalidDocumentationUrlError(
            f'Invalid URL: {url_str}. Only http/https URLs are allowed'
        )

    if parsed.username or parsed.password:
        raise InvalidDocumentationUrlError(
            f'Invalid URL: {url_str}. URLs with embedded credentials are not allowed'
        )

    if not ALLOWED_DOC_URL_PATTERN.match(url_str):
        raise InvalidDocumentationUrlError(
            f'Invalid URL: {url_str}. URL must be from the developer.payments.jpmorgan.com domain'
        )

    if not parsed.hostname:
        raise InvalidDocumentationUrlError(f'Invalid URL: {url_str}. Missing host')

    _reject_private_address(parsed.hostname)


async def read_documentation_page_raw(
    ctx: Context,
    url_str: str,
) -> Tuple[str, str]:
    """Fetch raw HTML content from a documentation page.

    Validates url_str (and every redirect hop) against the domain allowlist and
    SSRF defense-in-depth checks in validate_documentation_url() before issuing
    any request, and does not delegate redirect-following to httpx so that each
    hop is re-validated.

    Args:
        ctx: MCP context for logging and error handling
        url_str: URL of the documentation page to fetch

    Returns:
        Tuple containing (page_content, content_type)
        If an error occurs, page_content will start with 'Failed to fetch'
    """
    logger.debug(f'Fetching documentation from {url_str}')

    try:
        validate_documentation_url(url_str)
    except InvalidDocumentationUrlError as e:
        error_msg = f'Failed to fetch {url_str}: {str(e)}'
        logger.error(error_msg)
        await ctx.error(error_msg)
        return error_msg, 'text/plain'

    # Configure proxy settings from environment variables
    proxy_url = os.getenv('HTTP_PROXY') or os.getenv('HTTPS_PROXY')
    client_kwargs = {}
    if proxy_url:
        client_kwargs['proxy'] = proxy_url
        logger.debug(f'Using proxy: {proxy_url}')

    current_url = url_str
    async with httpx.AsyncClient(**client_kwargs) as client:
        for _ in range(MAX_REDIRECTS + 1):
            try:
                response = await client.get(
                    current_url,
                    follow_redirects=False,
                    headers={
                        'User-Agent': DEFAULT_USER_AGENT,
                    },
                    timeout=30,
                )
            except httpx.HTTPError as e:
                error_msg = f'Failed to fetch {current_url}: {str(e)}'
                logger.error(error_msg)
                await ctx.error(error_msg)
                return error_msg, 'text/plain'

            if response.is_redirect:
                next_url = str(response.next_request.url) if response.next_request else None
                if not next_url:
                    error_msg = f'Failed to fetch {current_url}: redirect with no Location'
                    logger.error(error_msg)
                    await ctx.error(error_msg)
                    return error_msg, 'text/plain'

                try:
                    validate_documentation_url(next_url)
                except InvalidDocumentationUrlError as e:
                    error_msg = f'Failed to fetch {current_url}: redirected to disallowed URL {next_url}: {str(e)}'
                    logger.error(error_msg)
                    await ctx.error(error_msg)
                    return error_msg, 'text/plain'

                current_url = next_url
                continue

            if response.status_code >= 400:
                error_msg = f'Failed to fetch {current_url} - status code {response.status_code}'
                logger.error(error_msg)
                await ctx.error(error_msg)
                return error_msg, 'text/plain'

            return response.text, response.headers.get('content-type', '')

    error_msg = f'Failed to fetch {url_str}: too many redirects'
    logger.error(error_msg)
    await ctx.error(error_msg)
    return error_msg, 'text/plain'


async def read_documentation_impl(
    ctx: Context,
    url_str: str,
    max_length: int,
    start_index: int,
    session_uuid: str,
) -> str:
    """Process and format documentation page content.

    Args:
        ctx: MCP context for logging and error handling
        url_str: URL of the documentation page to fetch
        max_length: Maximum number of characters to return
        start_index: Index to start reading from for pagination
        session_uuid: Unique session identifier

    Returns:
        Formatted markdown content from the documentation page
    """
    logger.debug(f'Processing documentation from {url_str}')

    # Fetch raw page content
    page_raw, content_type = await read_documentation_page_raw(ctx, url_str)
    if not page_raw or page_raw.startswith('Failed to fetch'):
        return page_raw

    # Convert HTML to markdown if needed
    if is_html_content(page_raw, content_type):
        content = extract_content_from_html(page_raw)
    else:
        content = page_raw

    # Format the result with pagination support
    result = format_documentation_result(url_str, content, start_index, max_length)

    # Log if content was truncated
    if len(content) > start_index + max_length:
        logger.debug(
            f'Content truncated at {start_index + max_length} of {len(content)} characters'
        )

    return result
