# holds cube.py state, receives {action, move}, responds with {facelets, solved}

import asyncio
import json
from websockets.asyncio.server import serve
import cube

HOST, PORT = "localhost", 8765

def state():
    return {
        "facelets": cube.get_facelets(),
        "solved": cube.is_solved(),
    }


async def handler(connection):
    print("browser connected")
    await connection.send(json.dumps(state()))

    async for raw in connection:
        message = json.loads(raw)
        action = message.get("action")

        try:
            if action == "move":
                cube.move(message["move"])
            elif action == "scramble":
                moves = cube.scramble(20)
                print("scrambled:", " ".join(moves))
            elif action == "reset":
                cube.reset()
        except ValueError as err:
            print("ignored:", err)

        await connection.send(json.dumps(state()))

async def main():
    async with serve(handler, HOST, PORT):
        print(f"cube server on ws://{HOST}:{PORT}")
        await asyncio.Future()   # run until interrupted


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nbye")
