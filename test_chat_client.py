import asyncio
import websockets
import threading
import queue

# Queue for passing messages from input thread to asyncio
message_queue = queue.Queue()

def input_thread():
    """Thread for handling user input without blocking the asyncio loop"""
    while True:
        try:
            message = input("You > ")
            message_queue.put(message)
            if message.lower() == 'exit':
                break
        except Exception as e:
            print(f"Input error: {e}")
            break

async def keep_alive(websocket):
    """Send periodic keep-alive messages to maintain the connection"""
    while True:
        try:
            await websocket.ping()
            await asyncio.sleep(20)  # Send a ping every 20 seconds
        except:
            break

async def receive_messages(websocket):
    """Listen for messages from the server"""
    try:
        async for message in websocket:
            if message.startswith("CHAT:"):
                chat_content = message.replace("CHAT:", "", 1)
                print(f"\n{chat_content}")
                print("You > ", end="", flush=True)
            elif message.startswith("SCREEN:"):
                print("\nReceived screen data (not displaying)")
                print("You > ", end="", flush=True)
            else:
                print(f"\nReceived: {message[:50]}..." if len(message) > 50 else f"\nReceived: {message}")
                print("You > ", end="", flush=True)
    except Exception as e:
        print(f"\nError receiving messages: {e}")

async def process_input_queue(websocket):
    """Process messages from the input queue and send them to the server"""
    while True:
        try:
            # Check if there's a message in the queue (non-blocking)
            if not message_queue.empty():
                message = message_queue.get_nowait()
                
                if message.lower() == 'exit':
                    return
                
                # Send as chat message
                await websocket.send("CHAT:" + message)
            
            # Small sleep to prevent CPU hogging
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"\nError processing input: {e}")
            await asyncio.sleep(1)

async def main():
    uri = "ws://localhost:8765"
    print(f"Attempting to connect to chat server at {uri}...")
    
    # Start the input thread
    input_thread_handle = threading.Thread(target=input_thread, daemon=True)
    input_thread_handle.start()
    
    while True:  # Keep trying to reconnect
        try:
            async with websockets.connect(uri, max_size=None, ping_interval=None) as websocket:
                print("Connected to chat server!")
                print("Type messages and press Enter to send. Type 'exit' to quit.")
                print("You > ", end="", flush=True)
                
                # Start background tasks
                keep_alive_task = asyncio.create_task(keep_alive(websocket))
                receive_task = asyncio.create_task(receive_messages(websocket))
                input_task = asyncio.create_task(process_input_queue(websocket))
                
                # Wait for the input task to complete (when user types 'exit')
                await input_task
                
                # Clean up tasks
                keep_alive_task.cancel()
                receive_task.cancel()
                break
                
        except ConnectionRefusedError:
            print("Connection refused. Server might be down. Retrying in 5 seconds...")
            await asyncio.sleep(5)
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Unexpected error: {e}")
            print("Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    print("Starting chat client...")
    try:
        asyncio.run(main())
        print("\nClient shutting down...")
    except KeyboardInterrupt:
        print("\nClient shutting down due to keyboard interrupt...")
    except Exception as e:
        print(f"Fatal error: {e}")