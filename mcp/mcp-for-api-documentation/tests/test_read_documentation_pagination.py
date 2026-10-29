"""Regression tests for read_documentation pagination.

read_documentation() ends a truncated page with a note telling the caller to
retry with start_index=N, so the tool must accept start_index (and max_length)
and honour them.
"""

import pytest
import re
from jpmc.mcp_for_api_documentation import server, server_utils
from unittest.mock import AsyncMock


URL = 'https://developer.payments.jpmorgan.com/docs/example'
PARAGRAPHS = [f'Paragraph {i:02d} ' + 'x' * 400 for i in range(30)]


@pytest.fixture
def long_page(monkeypatch):
    """Serve a ~12k character page instead of fetching over the network."""
    html = (
        '<html><body><main>' + ''.join(f'<p>{p}</p>' for p in PARAGRAPHS) + '</main></body></html>'
    )
    monkeypatch.setattr(
        server_utils, 'read_documentation_page_raw', AsyncMock(return_value=(html, 'text/html'))
    )


async def read(**kwargs):
    """Call the tool function directly with an explicit max_length and start_index."""
    return await server.read_documentation(URL, **kwargs)


@pytest.mark.asyncio
async def test_tool_schema_exposes_pagination():
    """Agents can only page if the tool schema advertises the parameters."""
    tool = next(t for t in await server.mcp.list_tools() if t.name == 'read_documentation')
    properties = tool.input_schema['properties']
    assert properties['max_length']['default'] == 5000
    assert properties['start_index']['default'] == 0


@pytest.mark.asyncio
async def test_following_truncation_note_reaches_end_of_page(long_page):
    """Each start_index from the truncation note returns the next chunk until the page ends."""
    start_index, chunks = 0, []
    while True:
        result = await read(max_length=3000, start_index=start_index)
        chunks.append(result)
        next_index = re.search(r'start_index=(\d+)', result)
        if not next_index:
            break
        assert int(next_index.group(1)) == start_index + 3000
        start_index = int(next_index.group(1))

    assert len(chunks) > 1
    assert len(set(chunks)) == len(chunks)
    assert 'Paragraph 00' in chunks[0]
    assert 'Paragraph 29' in chunks[-1]


@pytest.mark.asyncio
async def test_start_index_past_end_reports_no_more_content(long_page):
    """A start_index beyond the page returns a clear end-of-content message."""
    result = await read(max_length=5000, start_index=1_000_000)
    assert 'No more content available' in result
