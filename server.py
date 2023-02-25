import json
import functools

import trio
from trio_websocket import serve_websocket, ConnectionClosed


buses = {}  # {bus_id: bus_info}


async def get_routes(request):
    ws = await request.accept()
    while True:
        try:
            message = await ws.get_message()
            bus_info = json.loads(message)
            bus_id = bus_info.get("busId")
            buses[bus_id] = bus_info
        except ConnectionClosed:
            break


async def talk_to_browser(request):
    ws = await request.accept()
    while True:
        try:
            # message = await ws.get_message()
            # print(json.loads(message))

            out_message = {
                "msgType": "Buses",
                "buses": []
            }

            for bus_id, bus_info in buses.items():
                route = bus_info.get("route")
                latitude = bus_info.get("lat")
                longitude = bus_info.get("lng")
                out_message["buses"].append({
                    "busId": bus_id,
                    "lat": latitude,
                    "lng": longitude,
                    "route": route
                })

            await ws.send_message(json.dumps(out_message))
            await trio.sleep(1)
        except ConnectionClosed:
            break


async def main():
    browser_websocket = functools.partial(
        serve_websocket, talk_to_browser, "127.0.0.1", 8000, ssl_context=None
    )

    routes_websocket = functools.partial(
        serve_websocket, get_routes, "127.0.0.1", 8080, ssl_context=None
    )

    async with trio.open_nursery() as nursery:
        nursery.start_soon(routes_websocket)
        nursery.start_soon(browser_websocket)

trio.run(main)
