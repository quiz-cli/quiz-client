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
    state = {}
    async with connect(uri) as ws:
        await asyncio.gather(
            send_messages(ws, client_id, state), receive_messages(ws, state)
        )


async def send_messages(ws: ClientConnection, client_id: str, state: dict) -> None:
    """Prompt the user for input and send messages to the server over the websocket."""
    while True:
        user_input = await aioconsole.ainput()
        user_input = sanitization(user_input, state)
        if user_input != []:
            await ws.send(json.dumps({"client_id": client_id, "answer": user_input}))
        else:
            print("Invalid choice. Please choose again from given options.")


async def receive_messages(ws: ClientConnection, state: dict) -> None:
    """Receive messages from the server and print them to the console."""
    while True:
        response = await ws.recv()
        message = json.loads(response)

        match message.get("type"):
            case "question":
                state["length_of_question"] = len(message["options"])
                print_question(message)
            case "repeat":
                print(f"You answered: {message['text']}")
            case "question_result":
                print(f"Correct answer: {message['correct_answer']}")
                if message["correct"] is True:
                    print("Your answer was correct.")
                elif message["correct"] is False:
                    print("Your answer was incorrect.")
                else:
                    print("You did not answer.")
            case "final_results":
                print(message["results"])
            case _:
                print(message["text"])


def print_question(question: dict[str, list]) -> None:
    """Nicely print text of the question with possible answeres."""
    print(f"Question: {question['text']}")
    for letter, opt in zip(string.ascii_letters, question["options"], strict=False):
        print(f"\t{letter}) {opt}")
    print("Answer:")


def sanitization(user_input: str, state: dict) -> list[bool]:
    """Provide list of bools instead of letters."""
    user_input = user_input.replace(" ", "")
    if user_input.isalpha():
        answer = [False] * state["length_of_question"]
        for letter in user_input.upper():
            position_in_alphabet = ord(letter) - ord("A")
            if position_in_alphabet < len(answer):
                answer[position_in_alphabet] = True
            else:
                return []
        return answer
    return []


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
