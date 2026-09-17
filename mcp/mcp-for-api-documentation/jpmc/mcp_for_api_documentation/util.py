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
# - removed several aws-specific html tags.


"""Utility functions for JPMorgan Chase (JPMC) Payments Developer Portal (PDP)
API Documentation MCP Server.

This module provides functions for processing HTML content, determining content types,
formatting documentation results, and parsing recommendation API responses.
"""

from typing import Any, Dict, List, Optional
import markdownify

from .models import RecommendationResult


def extract_content_from_html(html: str) -> str:
    """Extract and convert HTML content to Markdown format.

    Uses BeautifulSoup to identify and extract the main content area of an HTML document,
    removes navigation and non-content elements, and converts the result to Markdown.

    Args:
        html: Raw HTML content to process

    Returns:
        Simplified markdown version of the content or an error message
    """
    if not html:
        return '<e>Empty HTML content</e>'

    try:
        # Import BeautifulSoup here to avoid unnecessary imports when function isn't used
        from bs4 import BeautifulSoup

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Try to find the main content area
        main_content = None

        # Common content container selectors for JPMC-PDP documentation
        content_selectors = [
            'main',
            'article',
            '#main-content',
            '.main-content',
            '#content',
            '.content',
            "div[role='main']",
        ]

        # Try to find the main content using common selectors
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                main_content = content
                break

        # If no main content found, use the body or the entire document
        if not main_content:
            main_content = soup.body if soup.body else soup

        # Remove navigation elements that might be in the main content
        nav_selectors = [
            'noscript',
            '.prev-next',
            '#main-col-footer',
            '#quick-feedback-yes',
            '#quick-feedback-no',
            '.page-loading-indicator',
            '#tools-panel',
            '.doc-cookie-banner',
        ]

        for selector in nav_selectors:
            for element in main_content.select(selector):
                element.decompose()

        # Define tags to strip - these are elements we don't want in the output
        tags_to_strip = [
            # Standard non-content HTML elements
            'script',
            'style',
            'noscript',
            'meta',
            'link',
            'footer',
            'nav',
            'aside',
            'header',
            # JPMC-PDP specific elements
            'js-show-more-buttons',
            'js-show-more-text',
            'feedback-container',
            'feedback-section',
            'doc-feedback-container',
            'doc-feedback-section',
            'warning-container',
            'warning-section',
            'cookie-banner',
            'cookie-notice',
            'copyright-section',
            'legal-section',
            'terms-section',
        ]

        # Convert HTML to Markdown
        content = markdownify.markdownify(
            str(main_content),
            heading_style=markdownify.ATX,
            autolinks=True,
            default_title=True,
            escape_asterisks=True,
            escape_underscores=True,
            newline_style='SPACES',
            strip=tags_to_strip,
        )

        if not content:
            return '<e>Page failed to be simplified from HTML</e>'

        return content
    except Exception as e:
        return f'<e>Error converting HTML to Markdown: {str(e)}</e>'


def is_html_content(page_raw: str, content_type: str) -> bool:
    """Determine if content is HTML.

    Checks either the beginning of the content for HTML tags or the content-type header.

    Args:
        page_raw: Raw page content
        content_type: Content-Type header value

    Returns:
        True if content is HTML, False otherwise
    """
    # Check if content starts with HTML tag, has HTML content-type, or has no content-type (assume HTML)
    return (
        '<html' in page_raw[:100].lower()
        or 'text/html' in content_type.lower()
        or not content_type
    )


def format_documentation_result(url: str, content: str, start_index: int, max_length: int) -> str:
    """Format documentation result with pagination information.

    Creates a formatted result string with the appropriate portion of the content,
    handling pagination and providing information about truncated content.

    Args:
        url: Documentation URL
        content: Content to format
        start_index: Start index for pagination (0-based)
        max_length: Maximum content length to return

    Returns:
        Formatted documentation result with pagination information if needed
    """
    original_length = len(content)

    # Handle case where start_index is beyond the content length
    if start_index >= original_length:
        return f'JPMC-PDP Documentation from {url}:\n\n<e>No more content available.</e>'

    # Calculate the end index, ensuring we don't go beyond the content length
    end_index = min(start_index + max_length, original_length)
    truncated_content = content[start_index:end_index]

    # Handle case where no content was extracted
    if not truncated_content:
        return f'JPMC-PDP Documentation from {url}:\n\n<e>No more content available.</e>'

    # Calculate remaining content length
    actual_content_length = len(truncated_content)
    remaining_content = original_length - (start_index + actual_content_length)

    # Create the result with the truncated content
    result = f'JPMC-PDP Documentation from {url}:\n\n{truncated_content}'

    # Add pagination information if there's more content
    if remaining_content > 0:
        next_start = start_index + actual_content_length
        result += f'\n\n<e>Content truncated. Call the read_documentation tool with start_index={next_start} to get more content.</e>'

    return result


def parse_recommendation_results(data: Dict[str, Any]) -> List[RecommendationResult]:
    """Parse recommendation API response into RecommendationResult objects.

    Processes various recommendation types from the API response:
    - Highly rated pages
    - Journey-based recommendations
    - New content
    - Similar pages

    Args:
        data: Raw API response data

    Returns:
        List of RecommendationResult objects containing URL, title, and context information
    """
    results = []

    # Process highly rated recommendations
    if 'highlyRated' in data and 'items' in data['highlyRated']:
        for item in data['highlyRated']['items']:
            context = item.get('abstract') if 'abstract' in item else None
            results.append(
                RecommendationResult(
                    url=item.get('url', ''), title=item.get('assetTitle', ''), context=context
                )
            )

    # Process journey recommendations (organized by intent)
    if 'journey' in data and 'items' in data['journey']:
        for intent_group in data['journey']['items']:
            intent = intent_group.get('intent', '')
            if 'urls' in intent_group:
                for url_item in intent_group['urls']:
                    # Add intent as part of the context
                    context = f'Intent: {intent}' if intent else None
                    results.append(
                        RecommendationResult(
                            url=url_item.get('url', ''),
                            title=url_item.get('assetTitle', ''),
                            context=context,
                        )
                    )

    # Process new content recommendations
    if 'new' in data and 'items' in data['new']:
        for item in data['new']['items']:
            # Add "New content" label to context
            date_created = item.get('dateCreated', '')
            context = f'New content added on {date_created}' if date_created else 'New content'
            results.append(
                RecommendationResult(
                    url=item.get('url', ''), title=item.get('assetTitle', ''), context=context
                )
            )

    # Process similar recommendations
    if 'similar' in data and 'items' in data['similar']:
        for item in data['similar']['items']:
            context = item.get('abstract') if 'abstract' in item else 'Similar content'
            results.append(
                RecommendationResult(
                    url=item.get('url', ''), title=item.get('assetTitle', ''), context=context
                )
            )

    return results
