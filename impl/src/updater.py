from aiohttp import web


async def handle(request):
    file_path = "./_new_file.py"
    return web.FileResponse(file_path)


app = web.Application()
app.router.add_get("/", handle)

if __name__ == "__main__":
    web.run_app(app)
