async def test_unauthenticated(loop, client):
    response = await client.get('/statistic/')
    assert response.status == 401
