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
# Significant changes include: changed comments.


"""Data models for JPMorgan Chase (JPMC) Payments Developer Portal (PDP)
API Documentation MCP Server.

This module defines the Pydantic models used for structured data representation
throughout the MCP server. These models ensure type safety and proper validation
for search results and content recommendations.
"""

from pydantic import BaseModel, Field
from typing import Optional


class SearchResult(BaseModel):
    """Search result from PDP documentation search API.

    Represents a single result item returned from the Payments Developer Portal
    search API. Includes ranking, URL, title, and optional contextual excerpt.

    Attributes:
        rank_order: Relevance ranking (lower is more relevant)
        url: Documentation page URL
        title: Page title
        context: Optional excerpt or summary from the document
    """

    rank_order: int = Field(description='Relevance ranking (lower is more relevant)')
    url: str = Field(description='Documentation page URL')
    title: str = Field(description='Page title')
    context: Optional[str] = Field(
        default=None, description='Excerpt or summary from the document'
    )


class RecommendationResult(BaseModel):
    """Recommendation result from PDP documentation.

    Represents a related content recommendation from the Payments Developer Portal.
    Includes URL, title, and optional contextual information about the relationship.

    Attributes:
        url: Documentation page URL
        title: Page title
        context: Optional description of why this page is recommended
    """

    url: str = Field(description='Documentation page URL')
    title: str = Field(description='Page title')
    context: Optional[str] = Field(
        default=None, description='Description of why this page is recommended'
    )
