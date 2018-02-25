async def test_unauthenticated(loop, client):
    response = await client.get('/api/statistic/')
    assert response.status == 401
