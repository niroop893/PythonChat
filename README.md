# PythonChat - Bidirectional WebSocket Chat Application

A real-time bidirectional chat application with screen sharing capabilities built with Python and WebSockets.

## Features

- Real-time bidirectional text chat
- Screen sharing functionality
- Server admin broadcast capability
- Automatic reconnection on connection loss
- Keep-alive mechanism to maintain connections
- Support for multiple simultaneous clients

## Requirements

- Python 3.7+
- WebSockets library
- OpenCV (for screen sharing)
- NumPy (for image processing)
- PyAutoGUI (for screen capture)

## Installation

### 1. Set up a virtual environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
# source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install websockets pyautogui opencv-python numpy
```

## Usage

### Starting the Server

1. Activate your virtual environment if not already activated
2. Run the server:

```bash
python server.py
```

The server will start and display:
```
Server starting...
WebSocket server started on 0.0.0.0:8765
Server broadcast >
```

You can type messages at the "Server broadcast >" prompt to send messages to all connected clients.

### Starting a Client

1. Open a new terminal window
2. Activate your virtual environment
3. Run the client:

```bash
python test_chat_client.py
```

The client will connect to the server and display:
```
Starting chat client...
Attempting to connect to chat server at ws://localhost:8765...
Connected to chat server!
Type messages and press Enter to send. Type 'exit' to quit.
You >
```

### Chat Commands

- Type your message and press Enter to send it to all other connected clients
- Type 'exit' to quit the application

## Network Configuration

By default, the server listens on all interfaces (0.0.0.0) on port 8765.

- For local testing, clients connect to `localhost:8765`
- For network usage, clients should connect to the server's IP address

To change the server IP or port:
1. In `server.py`, modify the parameters in the `websockets.serve()` call
2. In client files, update the `uri` variable with the correct server address

## Advanced Features

### Screen Sharing

The application includes screen sharing functionality:

- Screen data is captured using PyAutoGUI
- Images are compressed using OpenCV
- Data is sent with the prefix "SCREEN:" to distinguish from chat messages

### Server Admin Commands

The server can broadcast messages to all connected clients:

1. Type your message at the "Server broadcast >" prompt
2. Press Enter to send the message to all clients
3. Type 'exit' at the prompt to disable the server admin chat interface

## Troubleshooting

### Connection Issues

If clients cannot connect to the server:
- Ensure the server is running
- Check if any firewall is blocking port 8765
- Verify the correct IP address is being used

### PowerShell Execution Policy

If running into PowerShell execution policy issues when activating the virtual environment:

```powershell
# Option 1: Temporarily bypass for current session
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# Option 2: Use Command Prompt instead
cmd /c "venv\Scripts\activate.bat"
```

## Architecture

The application uses a client-server architecture with WebSockets for real-time bidirectional communication:

- **Server**: Manages client connections and relays messages between clients
- **Clients**: Connect to the server, send and receive messages

Both server and client use asyncio for handling concurrent operations:
- Separate tasks for sending and receiving messages
- Threading for handling user input without blocking the event loop
- Message queues for passing data between threads and asyncio tasks

## License

This project is open source and available under the [MIT License](LICENSE).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.