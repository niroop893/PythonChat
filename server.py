import asyncio
import websockets
import traceback
import threading
import queue

# Queue for passing messages from input thread to asyncio
server_message_queue = queue.Queue()
clients = set()

def server_input_thread():
    """Thread for handling server admin input without blocking the asyncio loop"""
    print("Server admin chat enabled. Type messages to broadcast to all clients.")
    while True:
        try:
            message = input("Server broadcast > ")
            if message.lower() == 'exit':
                print("Server admin chat disabled.")
                break
            server_message_queue.put(message)
        except Exception as e:
            print(f"Input error: {e}")
            break

async def process_server_input():
    """Process messages from the server input queue and broadcast to all clients"""
    while True:
        try:
            # Check if there's a message in the queue (non-blocking)
            if not server_message_queue.empty():
                message = server_message_queue.get_nowait()
                
                # Broadcast to all clients
                if clients:
                    print(f"Broadcasting message to {len(clients)} clients: {message}")
                    for client in clients:
                        try:
                            await client.send("CHAT:SERVER: " + message)
                        except Exception as e:
                            print(f"Error sending to a client: {e}")
                else:
                    print("No connected clients to receive the message.")
            
            # Small sleep to prevent CPU hogging
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Error processing server input: {e}")
            await asyncio.sleep(1)

async def handler(websocket):
    # Register new client
    clients.add(websocket)
    client_id = id(websocket)
    print(f"New client connected (ID: {client_id})")
    
    # Send welcome message to the new client
    try:
        await websocket.send("CHAT:SERVER: Welcome to the chat server!")
    except Exception as e:
        print(f"Error sending welcome message: {e}")
    
    try:
        async for message in websocket:
            try:
                # Print different message types differently
                if message.startswith("CHAT:"):
                    chat_content = message.replace("CHAT:", "", 1)
                    print(f"CHAT MESSAGE from client {client_id}: {chat_content}")
                    
                    # Relay chat message to all other clients with client ID
                    relay_message = f"CHAT:Client {client_id}: {chat_content}"
                    for client in clients:
                        if client != websocket:
                            try:
                                await client.send(relay_message)
                            except Exception as e:
                                print(f"Error relaying chat: {e}")
                
                elif message.startswith("SCREEN:"):
                    print(f"SCREEN DATA from client {client_id} (not showing full content)")
                    
                    # Relay screen data to all other clients
                    for client in clients:
                        if client != websocket:
                            try:
                                await client.send(message)
                            except Exception as e:
                                print(f"Error relaying screen data: {e}")
                
                else:
                    print(f"OTHER MESSAGE from client {client_id}: {message[:50]}..." if len(message) > 50 else f"OTHER MESSAGE from client {client_id}: {message}")
                    
                    # Relay other messages to all other clients
                    for client in clients:
                        if client != websocket:
                            try:
                                await client.send(message)
                            except Exception as e:
                                print(f"Error relaying message: {e}")
                
            except Exception as e:
                print(f"Error processing message from client {client_id}: {e}")
                print(traceback.format_exc())
    
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Client {client_id} disconnected normally: {e}")
    except Exception as e:
        print(f"Unexpected error with client {client_id}: {e}")
        print(traceback.format_exc())
    finally:
        if websocket in clients:
            clients.remove(websocket)
            print(f"Client {client_id} removed from active clients")
        print(f"Number of connected clients: {len(clients)}")

async def main():
    print("Server starting...")
    
    # Start the server input thread
    input_thread_handle = threading.Thread(target=server_input_thread, daemon=True)
    input_thread_handle.start()
    
    # Start the server
    server = await websockets.serve(
        handler, 
        "0.0.0.0", 
        8765,
        ping_interval=30,  # Send ping every 30 seconds
        ping_timeout=10,   # Wait 10 seconds for pong response
        max_size=100*1024*1024  # 100MB max message size
    )
    
    print("WebSocket server started on 0.0.0.0:8765")
    
    # Start processing server input
    server_input_task = asyncio.create_task(process_server_input())
    
    # Keep the server running
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server shutting down...")
    except Exception as e:
        print(f"Server error: {e}")
        print(traceback.format_exc())