import asyncio
import websockets

async def main():
    uri = "ws://localhost:8765"
    print(f"Connecting to {uri}...")
    
    async with websockets.connect(uri) as websocket:
        print("Connected! Type messages and press Enter. Type 'exit' to quit.")
        
        # Send a test message
        test_message = "Hello from simple client"
        print(f"Sending test message: {test_message}")
        await websocket.send("CHAT:" + test_message)
        
        # Main loop
        while True:
            message = input("> ")
            if message.lower() == "exit":
                break
                
            await websocket.send("CHAT:" + message)
            print(f"Sent: {message}")

if __name__ == "__main__":
    asyncio.run(main())