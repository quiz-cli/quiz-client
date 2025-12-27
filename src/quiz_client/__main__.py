import asyncio
import json
import string
import sys

import aioconsole
from websockets import connect, ClientConnection
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK


async def send_receive_messages(uri: str, client_id: str):
    async with connect(uri) as ws:
        await asyncio.gather(
            asyncio.create_task(send_messages(ws, client_id)),
            asyncio.create_task(receive_messages(ws)),
        )


async def send_messages(ws: ClientConnection, client_id: str):
    while True:
        user_input = await aioconsole.ainput()
        if user_input:
            await ws.send(json.dumps({"client_id": client_id, "answer": user_input}))


async def receive_messages(ws: ClientConnection):
    while True:
        response = await ws.recv()
        message = json.loads(response)

        match message.get("type"):
            case "question":
                print_question(message)
            case "repeat":
                print(f"You answered: {message['text']}")
            case _:
                print(message["text"])


def print_question(question: dict[str, list]):
    """Nicely print text of the question with possible answeres"""

    print(f"Question: {question['text']}")
    for letter, opt in zip(string.ascii_letters, question["options"]):
        print(f"\t{letter}) {opt}")
    print("Answer:")


def main():
    if len(sys.argv) not in (2, 3):
        sys.exit(f"Usage: {sys.argv[0]} <url> [<client_id>]")
    elif len(sys.argv) == 3:
        client_id = sys.argv[2]
    else:
        client_id = input("Choose your name: ")

    server_url = f"ws://{sys.argv[1]}/connect/{client_id}"

    try:
        asyncio.get_event_loop().run_until_complete(
            send_receive_messages(server_url, client_id)
        )
    except OSError:
        sys.exit("Client: cannot reach server")
    except ConnectionClosedOK as e:
        print(e.reason)
    except ConnectionClosedError:
        print("Client: server disconected")
    except KeyboardInterrupt:
        print("\nClient: exit")
        sys.exit()
