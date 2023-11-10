"""
This modules hosts the update file for the IoT edge nodes.
Simple and demonstrative purpose.
"""
from aiohttp import web


async def handle(request):
    file_path = "./_new_file.py"
    return web.FileResponse(file_path)


def main():
    app = web.Application()
    app.router.add_get("/", handle)
    web.run_app(app)


if __name__ == "__main__":
    main()
