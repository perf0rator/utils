import asyncio

class InternalStopAsyncIteration(Exception):
    def __init__(self, key):
        self.key = key

async def anext(key, gen):
    try:
        return key, await gen.__anext__()
    except StopAsyncIteration:
        raise InternalStopAsyncIteration(key)

async def combine_async_generators(**gens):
    pending = {anext(key, gen) for key, gen in gens.items()}
    while pending:
        done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
        for i in done:
            if isinstance(i.exception(), InternalStopAsyncIteration):
                gens.pop(i.exception().key)
            else:
                key, val = i.result()
                pending.add(anext(key, gens[key]))
                yield key, val

import time
async def gen(x):
    while True:
        await asyncio.sleep(x)
        yield x


async def run():
    async for k, v in combine_async_generators(a=gen(1), b=gen(2)):
        print(k, v, time.time())
        print('----')

asyncio.get_event_loop().run_until_complete(run())

