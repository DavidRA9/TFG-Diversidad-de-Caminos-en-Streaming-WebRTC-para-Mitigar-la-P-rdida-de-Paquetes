# server_ws.py
import asyncio
import websockets
import json

connected = set()
sdp_pairs = {}

async def handler(websocket):
    connected.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "offer":
                sdp_pairs["offer"] = (websocket, data["sdp"])
                # Reenviar a otro cliente
                for conn in connected:
                    if conn != websocket:
                        await conn.send(json.dumps({"type": "offer", "sdp": data["sdp"]}))

            elif data["type"] == "answer":
                # Reenviar la answer al que mandó la offer
                offer_ws, _ = sdp_pairs.get("offer", (None, None))
                if offer_ws:
                    await offer_ws.send(json.dumps({"type": "answer", "sdp": data["sdp"]}))

            elif data["type"] == "candidate":
                # Reenviar candidatos ICE al peer
                for conn in connected:
                    if conn != websocket:
                        await conn.send(json.dumps({"type": "candidate", "candidate": data["candidate"]}))

    finally:
        connected.remove(websocket)

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("WebSocket signaling server running on ws://localhost:8765")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
