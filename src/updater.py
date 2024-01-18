"""
This modules hosts the update file for the IoT edge nodes.
Simple and demonstrative purpose.
"""
import argparse

from aiohttp import web


async def handle(request):
    file_path = "./_new_file.py"
    return web.FileResponse(file_path)


def main():
    parser = argparse.ArgumentParser(description="aiohttp server example")

    # parser.add_argument('--path')
    parser.add_argument("--port")
    args = parser.parse_args()

    app = web.Application()
    app.router.add_get("/", handle)

    web.run_app(app, port=args.port)


if __name__ == "__main__":
    main()
