import pytest


pytestmark = pytest.mark.asyncio


async def test_unauthenticated(event_loop, client):
    response = await client.get('/api/statistic/')
    assert response.status == 401
