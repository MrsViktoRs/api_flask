from typing import Type

from aiohttp import web
import json
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from models import Posted, Session, engine, Base
from schema import CreatePosted, UpdatePosted

app = web.Application()


async def orm_context(app):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app.cleanup_ctx.append(orm_context)


def valid_json(json_data: dict, schema_class: Type[CreatePosted] | Type[UpdatePosted]):
    try:
        return schema_class(**json_data).dict(exclude_unset=True)
    except ValidationError as er:
        error = er.errors()[0]
        error.pop('ctx', None)
        raise web.json_response({'error': 'validation error'})


async def get_posted(session, posted_id: int):
    posted = await session.get(Posted, posted_id)
    if posted is None:
        response = json.dumps({'error': f'posted with id {posted_id} not Found'})
        raise web.HTTPNotFound(text=response, content_type='application/json')
    else:
        return posted


@web.middleware
async def middleware(request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response

app.middlewares.append(middleware)


async def create_posted(session, posted: Posted):
    try:
        session.add(posted)
        await session.commit()
    except IntegrityError:
        response = json.dumps({'error': f'posted already exist'})
        raise web.HTTPNotFound(text=response, content_type='application/json')


class PostedView(web.View):

    @property
    def posted_id(self):
        return int(self.request.match_info['posted_id'])

    @property
    def session(self) -> AsyncSession:
        return self.request.session

    async def post(self):
        json_data = await self.request.json()
        data_post = valid_json(json_data, CreatePosted)
        posted = Posted(**data_post)
        await create_posted(self.session, posted)
        return web.json_response({'id': posted.id})

    async def get(self):
        posted = await get_posted(self.request.session, self.posted_id)
        return web.json_response(posted.dict)

    async def patch(self):
        json_data = await self.request.json()
        posted = await get_posted(self.request.session, self.posted_id)
        for field, value in json_data.items():
            setattr(posted, field, value)
        await create_posted(self.session, posted)
        return web.json_response(posted.dict)

    async def delete(self):
        posted = await get_posted(self.request.session, self.posted_id)
        await self.session.delete(posted)
        await self.session.commit()
        return web.json_response({'status': 'delete'})


app.add_routes([
    web.post('/posted', PostedView),
    web.get('/posted/{posted_id:\d+}', PostedView),
    web.patch('/posted/{posted_id:\d+}', PostedView),
    web.delete('/posted/{posted_id:\d+}', PostedView),
])


if __name__ == '__main__':
    web.run_app(app, port=5000)
