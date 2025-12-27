# quiz-client

This is the client side of the client-server quiz application. It tries to
provide the quiz game experience similar to **Kahoot** but in much lighter and
open manner as a CLI program.

The client is a regular CLI application making connection to the server
counterpart through the **WebSockets**. The client-server architecture is
designed that the CLI client can be eventually replaced by a JavaScript web
client.

The **Asyncio** is used in the client to provide asynchronously gathered the
input, display the information and keep the network communication with the
server in JSON (receiving questions, sending answers).
