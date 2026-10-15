"""read_documentation must accept the start_index its truncation note tells agents to use."""

import pytest
from jpmc.mcp_for_api_documentation import server
from unittest.mock import AsyncMock, patch


URL = 'https://developer.payments.jpmorgan.com/docs/foo'
PAGE = '<html><body><main><p>' + 'a' * 6000 + 'END</p></main></body></html>'


async def _fake_fetch(ctx, url):
    return PAGE, 'text/html'


async def _read(**kwargs):
    with (
        patch.object(server, 'validate_documentation_url'),
        patch(
            'jpmc.mcp_for_api_documentation.server_utils.read_documentation_page_raw', _fake_fetch
        ),
    ):
        return await server.read_documentation(AsyncMock(), URL, **kwargs)


@pytest.mark.asyncio
async def test_schema_exposes_pagination_params():
    """The tool schema advertises max_length and start_index to the agent."""
    tools = {t.name: t for t in await server.mcp.list_tools()}
    props = tools['read_documentation'].inputSchema['properties']
    assert {'max_length', 'start_index'} <= props.keys()


@pytest.mark.asyncio
async def test_long_page_can_be_read_to_the_end():
    """Following the truncation note returns the rest of the page."""
    first = await _read(max_length=5000, start_index=0)
    assert 'start_index=5000' in first
    assert 'END' not in first

    rest = await _read(max_length=5000, start_index=5000)
    assert 'END' in rest
    assert 'Content truncated' not in rest
