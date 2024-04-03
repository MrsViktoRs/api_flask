import asyncio

import requests
import aiohttp


async def main():
    async with aiohttp.ClientSession() as session:
        async with session.post(url='http://127.0.0.1:5000/posted',
                                json={'title': 'this two', 'description': 'this two', 'owner': 'not_my'}) as response:
            print(response.status)
            print(await response.text())

        # async with session.get(url='http://127.0.0.1:5000/posted/1') as response:
        #     print(response.status)
        #     print(await response.text())

        # async with session.patch(url='http://127.0.0.1:5000/posted/1',
        #                          json={'description': 'test patch'}) as response:
        #     print(response.status)
        #     print(await response.text())

        # async with session.delete(url='http://127.0.0.1:5000/posted/1') as response:
        #     print(response.status)
        #     print(await response.text())


asyncio.run(main())
