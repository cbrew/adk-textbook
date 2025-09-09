# Minimal consumer example using shared ADK consumer module
import asyncio

import httpx
from adk_core import ADKConsumer


def print_data(prefix: str, response: dict | str):
    print(prefix, response)


async def main():
    async with httpx.AsyncClient(timeout=None) as client:
        adk_consumer = await ADKConsumer.create(client)
        async for et, data in adk_consumer.message(
            "make me a note about rhubarb and save it as an artifact"
        ):
            print_data(et, data)


if __name__ == "__main__":
    asyncio.run(main())
