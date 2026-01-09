# quiz-client

This is the client side of a client-server quiz application. It aims to
provide a quiz game experience similar to **Kahoot**, but in a much lighter
and more open form, as a CLI program.

The client is a regular CLI application that connects to the server
counterpart via **WebSocket**. The client-server architecture is designed so
that the CLI client can eventually be replaced by a JavaScript web client.

The client uses **asyncio** to gather input, display information, and maintain
JSON-based network communication with the server (receiving questions,
sending answers) concurrently.

## Usage

Get the `uv` tool.

```bash
$ uv tool install . --editable
```

Run the quiz client as a module, pointing it to the quiz server address and
port, optionally providing a player name:

```bash
$ quiz-client <host:port> [<player name>]
```

This will connect to the quiz server via WebSocket, and the client will prompt
you to answer the questions.

## Contributing

The code needs to comply with:

```bash
$ uv run ruff format
```

```bash
$ uv run ruff check
```

```bash
$ uv run ty check
```
