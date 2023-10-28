import aiohttp
import asyncio


async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8080/") as resp:
            with open("downloaded_file.txt", "wb") as fd:
                while True:
                    chunk = await resp.content.read(1024)
                    if not chunk:
                        break
                    fd.write(chunk)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
