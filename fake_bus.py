import os
import json
import random
import itertools

import trio
from sys import stderr
from trio_websocket import open_websocket_url


def generate_bus_id(route_id, bus_index):
    return f"{route_id}-{bus_index}"


def load_routes(directory_path="routes"):
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            filepath = os.path.join(directory_path, filename)
            with open(filepath, "r", encoding="utf8") as file:
                yield json.load(file)


async def send_updates(server_address, receive_channel):
    try:
        async with open_websocket_url(server_address) as ws:
            while True:
                # async with receive_channel:
                async for out_message in receive_channel:
                    await ws.send_message(out_message)
                await trio.sleep(1)
    except OSError as ose:
        print("Connection attempt failed: %s" % ose, file=stderr)


async def run_bus(send_channel, bus_id, route):
    route_name = route.get("name")
    coordinates = route.get("coordinates")
    coord_iterator = itertools.cycle(coordinates)
    start = random.randint(0, len(coordinates) - 1)

    for coordinate in itertools.islice(coord_iterator, start, None):
        latitude = coordinate[0]
        longitude = coordinate[1]

        out_message = {
            "busId": bus_id,
            "lat": latitude,
            "lng": longitude,
            "route": route_name
        }

        out_message = json.dumps(out_message, ensure_ascii=True)
        # async with send_channel:
        await send_channel.send(out_message)
        await trio.sleep(2)


async def main():
    url = "ws://127.0.0.1:8080/ws"
    send_channels = []
    receive_channels = []

    for i in range(10):
        send_channel, receive_channel = trio.open_memory_channel(0)
        send_channels.append(send_channel)
        receive_channels.append(receive_channel)

    async with trio.open_nursery() as nursery:
        for route in load_routes():
            buses_count = random.randint(1, 5)
            for bus_index in range(buses_count):
                route_id = route.get("name")
                bus_id = generate_bus_id(route_id, bus_index)
                send_channel = random.choice(send_channels)
                nursery.start_soon(run_bus, send_channel, bus_id, route)

        for receive_channel in receive_channels:
            nursery.start_soon(send_updates, url, receive_channel)

trio.run(main)
