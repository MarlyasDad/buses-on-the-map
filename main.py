import json

import trio
from trio_websocket import serve_websocket, ConnectionClosed


async def echo_server(request):
    with open("156.json", "r", encoding="utf8") as file:
        routes_file = file.read()

    coordinates = json.loads(routes_file).get("coordinates")

    ws = await request.accept()
    while True:
        try:
            # message = await ws.get_message()

            for coordinate in coordinates:
                latitude = coordinate[0]
                longitude = coordinate[1]
                out_message = {
                    "msgType": "Buses",
                    "buses": [
                        {"busId": "a134aa", "lat": latitude, "lng": longitude, "route": "156"},
                    ]
                }
                await ws.send_message(json.dumps(out_message))
                await trio.sleep(2)
            # out_message = {
            #     "msgType": "Buses",
            #     "buses": [
            #       {"busId": "c790сс", "lat": 55.7500, "lng": 37.600, "route": "120"},
            #       {"busId": "a134aa", "lat": 55.7494, "lng": 37.621, "route": "670к"},
            #     ]
            # }
            await ws.send_message(json.dumps(out_message))
        except ConnectionClosed:
            break


async def main():
    await serve_websocket(echo_server, '127.0.0.1', 8000, ssl_context=None)

trio.run(main)
