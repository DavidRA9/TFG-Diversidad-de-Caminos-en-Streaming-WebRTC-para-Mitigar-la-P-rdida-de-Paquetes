import asyncio
import websockets
import json

# Conjunto global de clientes WebSocket conectados
connected = set()

# Diccionario para guardar la conexión WebSocket que envió cada oferta, usando su etiqueta (label)
offers = {}

# Función que maneja cada conexión WebSocket
async def handler(websocket):
    connected.add(websocket)  # Añadimos el cliente actual al conjunto de conectados
    try:
        # Esperamos mensajes del cliente en un bucle asincrónico
        async for message in websocket:
            data = json.loads(message)  # Convertimos el mensaje JSON a diccionario
            label = data.get("label")   # Extraemos la etiqueta del mensaje (por ejemplo, "path1")

            if not label:
                continue  # Si no hay etiqueta, ignoramos el mensaje

            if data["type"] == "offer":
                # Guardamos esta conexión WebSocket como la que ha enviado la oferta
                offers[label] = websocket

                # Reenviamos la oferta a todos los demás clientes conectados, excepto al emisor
                for conn in connected:
                    if conn != websocket:
                        await conn.send(json.dumps({
                            "type": "offer",
                            "sdp": data["sdp"],
                            "label": label
                        }))

            elif data["type"] == "answer":
                # Recuperamos la conexión que originalmente envió la oferta
                offer_ws = offers.get(label)
                if offer_ws:
                    # Le enviamos la respuesta (answer) a esa conexión
                    await offer_ws.send(json.dumps({
                        "type": "answer",
                        "sdp": data["sdp"],
                        "label": label
                    }))

            elif data["type"] == "candidate":
                # Reenviamos el candidato ICE a todos los clientes conectados excepto al emisor
                for conn in connected:
                    if conn != websocket:
                        await conn.send(json.dumps({
                            "type": "candidate",
                            "candidate": data["candidate"],
                            "label": label
                        }))
    finally:
        # Cuando el cliente se desconecta, lo eliminamos del conjunto de conectados
        connected.remove(websocket)

# Función principal que lanza el servidor WebSocket
async def main():
    # Inicia el servidor en todas las interfaces (0.0.0.0) y puerto 8765
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("WebSocket signaling server running on ws://localhost:8765")
        await asyncio.Future()  # El servidor se mantiene en ejecución indefinidamente

# Si se ejecuta como programa principal, arranca el servidor
if __name__ == "__main__":
    asyncio.run(main())

