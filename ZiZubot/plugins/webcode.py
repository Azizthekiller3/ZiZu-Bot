from aiohttp import web as webserver
import time

routes = webserver.RouteTableDef()

_START_TIME = time.time()

async def bot_run():
    _app = webserver.Application(client_max_size=30000000)
    _app.add_routes(routes)
    return _app

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return webserver.json_response({
        "status": "ok",
        "uptime": int(time.time() - _START_TIME),
    })
