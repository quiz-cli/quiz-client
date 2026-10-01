"""Unit tests for quiz-client message receiving."""

import asyncio
import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

import pytest

from quiz_client.__main__ import receive_messages

if TYPE_CHECKING:
    from websockets.asyncio.client import ClientConnection


class StopReceivingError(Exception):
    """Stop the infinite receiving loop after the prepared message."""


@dataclass
class FakeWebSocket:
    """Return one server message and then stop the receiving loop."""

    response: str
    received: bool = False

    async def recv(self) -> str:
        """Return the prepared response once."""
        if not self.received:
            self.received = True
            return self.response
        raise StopReceivingError


@pytest.mark.parametrize(
    ("message", "expected_output"),
    [
        (
            {"type": "question_result", "correct_answer": "a", "correct": True},
            "Correct answer: a\nYour answer was correct.\n",
        ),
        (
            {"type": "question_result", "correct_answer": "a", "correct": False},
            "Correct answer: a\nYour answer was incorrect.\n",
        ),
        (
            {"type": "question_result", "correct_answer": "a", "correct": None},
            "Correct answer: a\nYou did not answer.\n",
        ),
    ],
)
def test_receive_messages_prints_question_result(
    message: dict[str, object],
    expected_output: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Print the correct answer and every possible player result."""
    websocket = FakeWebSocket(json.dumps(message))

    with pytest.raises(StopReceivingError):
        asyncio.run(receive_messages(cast("ClientConnection", websocket)))

    assert capsys.readouterr().out == expected_output
