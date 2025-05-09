import asyncio, websockets
import pyautogui, cv2, numpy as np
import threading, base64

SERVER_IP = "localhost"  # Connect to the local server
PORT = "8765"

# SCREEN SHARING SENDER
async def screen_sender(websocket):
    while True:
        img = pyautogui.screenshot()
        frame = np.array(img)
        _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
        jpg_as_text = base64.b64encode(buf).decode('utf-8')
        await websocket.send("SCREEN:"+jpg_as_text)
        await asyncio.sleep(0.1)

# RECEIVE SCREEN AND DISPLAY
async def screen_receiver(msg):
    jpg_orig = base64.b64decode(msg)
    npimg = np.frombuffer(jpg_orig, dtype=np.uint8)
    frame = cv2.imdecode(npimg, 1)
    cv2.imshow("REMOTE SCREEN PRESS Q to EXIT", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        exit()

# CHAT SENDER
async def chat_sender(websocket):
    while True:
        msg = input("Enter message to remote user: ")
        await websocket.send("CHAT:"+msg)

# MESSAGE RECEIVER AND HANDLER
async def receiver(websocket):
    async for message in websocket:
        if message.startswith("SCREEN:"):
            imgdata = message.replace("SCREEN:", "", 1)
            await screen_receiver(imgdata)
        elif message.startswith("CHAT:"):
            chatmsg = message.replace("CHAT:", "", 1)
            print("\nREMOTE: " + chatmsg)

async def main_client():
    uri = f"ws://{SERVER_IP}:{PORT}"
    async with websockets.connect(uri, max_size=None) as websocket:
        recv_task = asyncio.create_task(receiver(websocket))
        send_screen_task = asyncio.create_task(screen_sender(websocket))
        chat_send_task = asyncio.create_task(chat_sender(websocket))
        await asyncio.gather(recv_task, send_screen_task, chat_send_task)

if __name__ == "__main__":
    asyncio.run(main_client())