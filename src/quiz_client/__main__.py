"""
Main entry point for the quiz player client.

This module allows a player to connect to the server and interactively
participate in the quiz session via a websocket connection.
"""

import asyncio
import json
import string
import sys

import aioconsole
from websockets import ClientConnection, connect
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK


async def send_receive_messages(uri: str, client_id: str) -> None:
    """
    Establish a websocket connection to the server.

    Send and receive messages concurrently.
    """
    async with connect(uri) as ws:
        await asyncio.gather(send_messages(ws, client_id), receive_messages(ws))


async def send_messages(ws: ClientConnection, client_id: str) -> None:
    """Prompt the user for input and send messages to the server over the websocket."""
    while True:
        user_input = await aioconsole.ainput()
        if user_input:
            await ws.send(json.dumps({"client_id": client_id, "answer": user_input}))


async def receive_messages(ws: ClientConnection) -> None:
    """Receive messages from the server and print them to the console."""
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


def print_question(question: dict[str, list]) -> None:
    """Nicely print text of the question with possible answeres."""
    print(f"Question: {question['text']}")
    for letter, opt in zip(string.ascii_letters, question["options"], strict=False):
        print(f"\t{letter}) {opt}")
    print("Answer:")


def main() -> None:
    """
    Script entry point.

    Connect with a provided name to the quiz server WebSocket.
    """
    if len(sys.argv) not in (2, 3):
        sys.exit(f"Usage: {sys.argv[0]} <url> [<client_id>]")
    elif len(sys.argv) == 3:  # noqa: PLR2004
        client_id = sys.argv[2]
    else:
        client_id = input("Choose your name: ")

    server_url = f"ws://{sys.argv[1]}/connect/{client_id}"

    try:
        asyncio.run(send_receive_messages(server_url, client_id))
    except OSError as e:
        sys.exit(f"Client: cannot reach server\n{e}")
    except ConnectionClosedOK as e:
        print(e.reason)
    except ConnectionClosedError as e:
        print(f"Client: server disconnected\n{e}")
    except KeyboardInterrupt:
        sys.exit("\nClient: exit")
