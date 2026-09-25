"""Regression tests for RDI-159.

related() must not bypass the domain allowlist that read_documentation()
enforces, and the shared fetch path must reject disallowed hosts, schemes,
and redirect targets.
"""

import pytest
from jpmc.mcp_for_api_documentation.server_utils import (
    InvalidDocumentationUrlError,
    validate_documentation_url,
)


ALLOWED_URLS = [
    'https://developer.payments.jpmorgan.com/docs/foo',
    'http://developer.payments.jpmorgan.com/docs/foo',
    'https://developer.payments.jpmorgan.com/',
]

DISALLOWED_URLS = [
    'http://127.0.0.1:8931/',  # the disclosure's own local repro target
    'http://localhost:8931/',
    'http://169.254.169.254/latest/meta-data/',  # cloud metadata endpoint
    'https://evil.com/',
    'https://developer.payments.jpmorgan.com.evil.com/',  # lookalike host
    'https://user:pass@developer.payments.jpmorgan.com/',  # embedded credentials
    'file:///etc/passwd',
    'ftp://developer.payments.jpmorgan.com/',
]


@pytest.mark.parametrize('url', ALLOWED_URLS)
def test_allowed_urls_pass(url):
    """Allowlisted developer.payments.jpmorgan.com URLs pass validation."""
    validate_documentation_url(url)


@pytest.mark.parametrize('url', DISALLOWED_URLS)
def test_disallowed_urls_raise(url):
    """Non-allowlisted, private, or malformed URLs are rejected."""
    with pytest.raises(InvalidDocumentationUrlError):
        validate_documentation_url(url)
