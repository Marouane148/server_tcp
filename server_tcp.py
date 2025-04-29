import socket
import json
import grpc
import game_engine_pb2
import game_engine_pb2_grpc

HOST = 'localhost'
PORT = 9999

ADMIN_HOST = 'localhost'
ADMIN_PORT = 8888  # Port du moteur d'administration
GRPC_SERVER = 'localhost:50051'  # Adresse du serveur gRPC

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
    server_sock.bind((HOST, PORT))
    server_sock.listen(5)
    print(f"Serveur TCP en écoute sur {HOST}:{PORT}")

    while True:
        conn, addr = server_sock.accept()
        with conn:
            print(f"Connexion de {addr}")
            data = conn.recv(1024)
            if not data:
                continue

            try:
                message = json.loads(data.decode('utf-8'))
                print("Message reçu:", message)

                if not isinstance(message, list) or len(message) < 1:
                    raise ValueError("Format invalide")

                msg_type = message[0]

                if msg_type == "subscribe":
                    _, pseudo, role = message

                    # Envoie au moteur d'administration
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as admin_sock:
                        admin_sock.connect((ADMIN_HOST, ADMIN_PORT))
                        csv_message = f"subscribe,{pseudo},{role}"
                        admin_sock.sendall(csv_message.encode('utf-8'))
                        admin_response = admin_sock.recv(1024).decode('utf-8')

                    response = {
                        "status": "success",
                        "message": f"Inscription envoyée à l'administration : {admin_response.strip()}"
                    }

                elif msg_type == "action":
                    _, pseudo, dx, dy = message

                    # Appel au moteur de jeu gRPC
                    with grpc.insecure_channel(GRPC_SERVER) as channel:
                        stub = game_engine_pb2_grpc.GameEngineServiceStub(channel)
                        action_request = game_engine_pb2.PlayerAction(
                            player_id=pseudo,
                            dx=int(dx),
                            dy=int(dy)
                        )
                        grpc_response = stub.Move(action_request)

                    # Construction de la réponse
                    visible = [
                        {
                            "pseudo": cell.pseudo,
                            "role": cell.role,
                            "x": cell.x,
                            "y": cell.y
                        }
                        for cell in grpc_response.visible_cells
                    ]

                    response = {
                        "status": "success" if grpc_response.success else "error",
                        "message": grpc_response.message,
                        "new_position": {"x": grpc_response.new_x, "y": grpc_response.new_y},
                        "visible_cells": visible
                    }

                else:
                    response = {"status": "error", "message": "Type de message inconnu"}

            except Exception as e:
                response = {"status": "error", "message": str(e)}

            conn.sendall(json.dumps(response).encode('utf-8'))
