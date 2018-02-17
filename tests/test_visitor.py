from .conftest import prepare


async def test_wrong_url(db, loop, client):
    response = await client.get('/')
    assert response.status == 404
    response = await client.get('/visit/')
    assert response.status == 404


async def test_wrong_method(db, loop, client):
    response = await client.put('/visit/somekey')
    assert response.status == 405
    response = await client.put('/visit/somekey/')
    assert response.status == 405


async def test_no_such_user(db, loop, client):
    await prepare(loop)
    response = await client.post('/visit/somekey')
    assert response.status == 404
    response = await client.post('/visit/somekey/')
    assert response.status == 404
