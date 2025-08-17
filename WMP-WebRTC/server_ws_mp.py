import asyncio
import websockets
import json

# Conjunto de WebSockets actualmente conectados al servidor.
# Nos permite iterar y reenviar mensajes a todos los clientes activos.
connected = set()


# Diccionario que asocia un label ("path1", "path2") con el WebSocket que envió la oferta (offer).
# Esto facilita enviar respuestas (answers) y feedback solo al peer correspondiente.
offers = {}

#Recibe ofertas, respuestas, candidatos ICE y feedback, y los enruta adecuadamente.
async def handler(websocket):
    
    # Añadimos el nuevo socket al conjunto de conexiones activas
    connected.add(websocket)
    try:
        # Leemos mensajes en bucle hasta que la conexión se cierre
        async for message in websocket:
           
            
            try:
                data = json.loads(message)
               
                
                label = data.get("label")
                
                # --------------------------------------------------
                # 1) Oferta de WebRTC (offer)
                #    - Guardamos el socket en offers[label]
                #    - Reenviamos la oferta a todos los demás clientes
                # --------------------------------------------------
                
                if data["type"] == "offer":
                    
                    offers[label] = websocket
                    # Iteramos sobre todas las conexiones excepto el emisor
                    for conn in [c for c in connected if c != websocket]:
                         # Reenviamos el mensaje original (oferta) a cada peer
                        await conn.send(message)
                        
                        
                # --------------------------------------------------
                # 2) Respuesta de WebRTC (answer)
                #    - La enviamos únicamente al peer que originalmente envió la oferta
                # --------------------------------------------------
                        
                elif data["type"] == "answer":
                    
                    if label in offers:
                    # Enviar la respuesta a la conexión guardada en offers[label]
                        await offers[label].send(message)
                        
                # --------------------------------------------------
                # 3) Candidatos ICE (candidate)
                #    - Broadcast a todos los demás clientes
                # --------------------------------------------------
                        
                elif data["type"] == "candidate":
                    
                    for conn in [c for c in connected if c != websocket]:
                        await conn.send(message)
                


                # --------------------------------------------------
                # 4) Feedback de frames perdidos (feedback)
                #    - Recibimos un array lostFrames unificado
                #    - Logueamos el reporte
                #    - Broadcast del mismo feedback a todos los peers en offers
                # --------------------------------------------------   
                
                elif data["type"] == "feedback":
                    # Extraemos el array unificado de frames perdidos
                    lost = data.get("lostFrames", [])

                    print(f"[FEEDBACK] Reporte recibido: {len(lost)} frames perdidos → {lost}")
                    
                    feedback_msg = json.dumps({
                        "type": "feedback",
                        "lostFrames": lost
                    })

                    # Enviamos feedback una sola vez a cada WebSocket único(1 por cliente, por muchos canales que haya)
                    for ws_client in set(offers.values()):
                        try:
                            await ws_client.send(feedback_msg)
                            print(f"[FEEDBACK] Enviado a {ws_client.remote_address}")
                        except Exception as e:
                            print(f"[FEEDBACK ERROR] No se pudo enviar a {ws_client.remote_address}: {e}")

                
            except json.JSONDecodeError:
                print("[SERVER ERROR] Mensaje no es JSON válido")
            except Exception as e:
                print(f"[SERVER ERROR] {str(e)}")

    finally:
        connected.remove(websocket)
        print(f"[SERVER] Conexión cerrada: {websocket.remote_address}")
        

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("[SERVER] Iniciado en ws://0.0.0.0:8765")
        # Await infinito para mantener vivo el servidor
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())