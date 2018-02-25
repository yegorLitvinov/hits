from .connections.db import get_db_pool


class DBError(Exception):
    pass


class DoesNotExist(DBError):
    pass


class MultipleObjectsReturned(DBError):
    pass


class FilterMixin:
    table_name = NotImplemented

    @classmethod
    async def filter(cls, **kwargs):
        query = f'select * from {cls.table_name} '
        if kwargs:
            query += 'where ' + ' and '.join(
                [f'{key} = ${num}' for num, key in enumerate(kwargs.keys(), 1)]
            )
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, *kwargs.values())
        return [cls(**row) for row in rows]

    @classmethod
    async def get(cls, **kwargs):
        objects = await cls.filter(**kwargs)
        if not objects:
            raise DoesNotExist
        elif len(objects) > 1:
            raise MultipleObjectsReturned
        return objects[0]

    @classmethod
    async def all(cls):
        return await cls.filter()

    async def get_from_db(self):
        return await self.__class__.get(id=self.id)


class SaveMixin:
    table_name = NotImplemented

    def __init__(self, **kwargs):
        self.__dict__['kwargs'] = kwargs

    def __eq__(self, other):
        return self.id == other.id

    def __getattr__(self, attr):
        return self.__dict__['kwargs'][attr]

    def __setattr__(self, attr, value):
        self.__dict__['kwargs'][attr] = value

    async def save(self):
        pk = self.kwargs.pop('id', None)
        keys = ', '.join(self.kwargs.keys())
        values_template = ', '.join([f'${i}' for i in range(1, len(self.kwargs) + 1)])
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            if pk:
                await conn.execute(
                    'update {} set ({}) = ({}) where id = ${}'.format(
                        self.table_name,
                        keys,
                        values_template,
                        len(self.kwargs) + 1,
                    ),
                    *self.kwargs.values(),
                    pk,
                )
            else:
                await conn.execute(
                    'insert into {} ({}) values ({})'.format(
                        self.table_name,
                        keys,
                        values_template,
                    ),
                    *self.kwargs.values()
                )
                pk = await conn.fetchval(
                    "SELECT currval(pg_get_serial_sequence('{}', 'id'))".format(
                        self.table_name
                    )
                )
        self.id = pk
