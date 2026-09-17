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
# - changed recommendation() to related(), and changed the implementation
#   to use BeautifulSoup to extract links from the page, instead of calling AWS Doc API.
# - changed search API to JPMC-PDP search API; changed aws doc website to jpmc pdp website.

"""JPMorgan Chase (JPMC) Payments Developer Portal (PDP) API Documentation
MCP Server implementation.

This module implements the Model Context Protocol (MCP) server for accessing and
searching the JPMorgan Chase Payments API documentation.
"""

# Standard library imports
import json
import os
import re
import sys
import uuid

# Third-party imports
import httpx
from bs4 import BeautifulSoup
from loguru import logger
from mcp.server.fastmcp import Context, FastMCP
from pydantic import Field
from typing import Dict, List

# Local imports
from .models import (
    RecommendationResult,
    SearchResult,
)
from .server_utils import (
    DEFAULT_USER_AGENT,
    read_documentation_impl,
    read_documentation_page_raw,
)
from .util import (
    parse_recommendation_results,
)


# Set up logging
logger.remove()
logger.add(sys.stderr, level=os.getenv('FASTMCP_LOG_LEVEL', 'WARNING'))

# Constants
PDP_BASE_URL = 'https://developer.payments.jpmorgan.com'
SEARCH_API_URL = 'https://developer.payments.jpmorgan.com/console/api/search'
SESSION_UUID = str(uuid.uuid4())

# Initialize MCP server
mcp = FastMCP(
    'jpmc-pdp-doc-mcp-server',
    instructions="""
    # JPMC-PDP Documentation MCP Server

    JPMorgan Chase (JPMC) Payments Developer Portal (PDP).
    This server provides tools to access public JPMC-PDP API documentation, search for content, and get related.

    ## Tool Selection Guide

    - Use `search_documentation` to find documentation about a specific JPMC-PDP topic
    - Use `read_documentation` to fetch a specific documentation by URL
    - Use `related` to find related content to a page URL
    """,
    dependencies=[
        'pydantic',
        'httpx',
        'beautifulsoup4',
    ],
)


@mcp.tool()
async def search_documentation(
    ctx: Context,
    search_phrase: str = Field(description='Search phrase to use'),
    limit: int = Field(
        default=10,
        description='Maximum number of results to return',
        ge=1,
        le=50,
    ),
) -> List[SearchResult]:
    """Search JPMC (JPMorgan Chase) Payments API documentation using the official
    JPMC API Documentation Search API.

    ## Usage

    This tool searches across all JPMC-PDP documentation for pages matching your search phrase.
    Use it to find relevant documentation when you don't have a specific URL.

    ## Result Interpretation

    Each result includes:
    - rank_order: The relevance ranking (lower is more relevant)
    - url: The documentation page URL
    - title: The page title
    - context: A brief excerpt or summary (if available)

    Args:
        ctx: MCP context for logging and error handling
        search_phrase: Search phrase to use
        limit: Maximum number of results to return

    Returns:
        List of search results with URLs, titles, and context snippets
    """
    logger.debug(f'Searching JPMC documentation for: {search_phrase}')

    parameters = {'searchQuery': search_phrase}

    search_url_with_session = f'{SEARCH_API_URL}?searchQuery={search_phrase}'

    # Make proxy usage optional based on environment variable
    proxy_url = os.getenv('HTTP_PROXY') or os.getenv('HTTPS_PROXY')
    client_kwargs = {}
    if proxy_url:
        client_kwargs['proxy'] = proxy_url

    async with httpx.AsyncClient(**client_kwargs) as client:
        try:
            response = await client.get(
                search_url_with_session,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': DEFAULT_USER_AGENT,
                    'X-MCP-Session-Id': SESSION_UUID,
                },
                timeout=30,
            )
        except httpx.HTTPError as e:
            error_msg = f'Error searching JPMC-PDP docs: {str(e)}'
            logger.error(error_msg)
            await ctx.error(error_msg)
            return [SearchResult(rank_order=1, url='', title=error_msg, context=None)]

        if response.status_code >= 400:
            error_msg = f'Error searching JPMC-PDP docs - status code {response.status_code}'
            logger.error(error_msg)
            await ctx.error(error_msg)
            return [
                SearchResult(
                    rank_order=1,
                    url='',
                    title=error_msg,
                    context=None,
                )
            ]

        try:
            data = response.json()
        except json.JSONDecodeError as e:
            error_msg = f'Error parsing search results: {str(e)}'
            logger.error(error_msg)
            await ctx.error(error_msg)
            return [
                SearchResult(
                    rank_order=1,
                    url='',
                    title=error_msg,
                    context=None,
                )
            ]

    logger.debug("PDP Search return data: {}".format(data))
    results = []
    if 'searchResponses' in data:
        for i, suggestion in enumerate(data['searchResponses'][:limit]):
            if 'summary' in suggestion:
                text_suggestion = suggestion  # ['textExcerptSuggestion']
                context = None

                # Add context if available
                if 'summary' in text_suggestion:
                    context = text_suggestion['summary']
                elif 'suggestionBody' in text_suggestion:
                    context = text_suggestion['suggestionBody']

                results.append(
                    SearchResult(
                        rank_order=i + 1,
                        url=PDP_BASE_URL + '/' + text_suggestion.get('url', ''),
                        title=text_suggestion.get('title', ''),
                        context=context,
                    )
                )

    logger.debug(f'Found {len(results)} search results for: {search_phrase}')
    return results


@mcp.tool()
async def read_documentation(
    ctx: Context,
    url: str = Field(description='URL of the JPMC documentation page to read'),
) -> str:
    """Fetch and convert a JPMC Payments API documentation page to markdown format.

    ## Usage

    This tool retrieves the content of a JPMC documentation page and converts it to markdown format.
    For long documents, you can make multiple calls with different start_index values to retrieve
    the entire content in chunks.

    ## URL Requirements

    - Must be from the developer.payments.jpmorgan.com domain

    ## Example URLs

    - https://developer.payments.jpmorgan.com/docs/commerce/online-payments/capabilities/checkout/how-to/create-checkout-session


    ## Output Format

    The output is formatted as markdown text with:
    - Preserved headings and structure
    - Code blocks for examples
    - Lists and tables converted to markdown format

    Args:
        ctx: MCP context for logging and error handling
        url: URL of the JPMC PDP documentation page to read

    Returns:
        Markdown content of the JPMC-PDP documentation
    """
    # Validate that URL is from developer.payments.jpmorgan.com.
    url_str = str(url)
    if not re.match(r'^https?://developer\.payments\.jpmorgan\.com/', url_str):
        await ctx.error(
            f'Invalid URL: {url_str}. URL must be from the developer.payments.jpmorgan.com domain'
        )
        raise ValueError('URL must be from the developer.payments.jpmorgan.com domain')

    return await read_documentation_impl(ctx, url_str, 5000, 0, SESSION_UUID)


@mcp.tool()
async def related(
    ctx: Context,
    url: str = Field(
        description='URL of the JPMC-PDP documentation page to get related pages for'
    ),
) -> List[RecommendationResult]:
    """Get related content for a JPMC-PDP Payments API documentation page.

    ## Usage

    This tool provides related JPMC-PDP Payments API documentation pages based on a given URL.
    Use it to discover additional relevant content that might not appear in search results.

    ## When to Use

    - After reading a documentation page to find related content
    - When exploring a new JPMC-PDP service to discover important pages
    - To find alternative explanations of complex concepts
    - To discover the most popular pages for a service
    - To find newly released information by using a service's welcome page URL and checking the **New** recommendations

    ## Result Interpretation

    Each recommendation includes:
    - url: The documentation page URL
    - title: The page title
    - context: A brief description (if available)

    Args:
        ctx: MCP context for logging and error handling
        url: URL of the JPMC-PDP documentation page to get recommendations for

    Returns:
        List of recommended pages with URLs, titles, and context
    """

    url_str = str(url)
    logger.debug(f'Getting related pages for: {url_str}')

    # Fetch the HTML content of the page
    raw_html, content_type = await read_documentation_page_raw(ctx, url_str)
    if not raw_html or raw_html.startswith('Failed to fetch'):
        logger.warning(f'Could not fetch content from {url_str}')
        await ctx.error(f'Failed to retrieve content from {url_str}')
        return []

    # Parse HTML with BeautifulSoup and extract related links
    try:
        soup = BeautifulSoup(raw_html, 'html.parser')

        # Find the main content area (typically has id='main-content')
        main_content = soup.find(id='main-content')
        if not main_content:
            logger.warning(f'Could not find main-content in {url_str}')
            await ctx.error(f'Could not find main content area in the page: {url_str}')
            return []

        # Store unique results in a dictionary keyed by href to avoid duplicates
        results = {}

        # Find all links in the main content
        for a in main_content.find_all('a', href=True):
            href = a['href']
            title = a.text.strip()

            # Only include internal documentation links
            if href.startswith('/docs/'):
                logger.debug(f'Found related link: {title} ({href})')

                # Use href as key to avoid duplicates
                results[href] = RecommendationResult(
                    url=PDP_BASE_URL + href, title=title or 'Untitled Link', context=None
                )

        logger.debug(f'Found {len(results)} related pages for: {url_str}')
        return list(results.values())

    except Exception as e:
        error_msg = f'Error extracting related links: {str(e)}'
        logger.error(error_msg)
        await ctx.error(error_msg)
        return []


def main():
    """Run the MCP server with CLI argument support."""
    logger.info('Starting JPMC-PDP Documentation MCP Server')
    mcp.run()


if __name__ == '__main__':
    main()
