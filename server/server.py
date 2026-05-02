import socket
import os
from dotenv import load_dotenv

def carregar_configs():
    load_dotenv()
    host = os.getenv("SERVER_HOST", "127.0.0.1")
    porta = int(os.getenv("SERVER_PORT", 5000))
    return host, porta


def cria_socket_server(host, porta):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, porta))
    server_socket.listen()
    return server_socket


def aceita_cliente(server_socket):
    print(f"Aguardando conexão...")
    client_socket, client_address = server_socket.accept()
    print(f"Cliente conectado: {client_address}")
    return client_socket


def recebe_mensagens(client_socket):
    while True:
        try:
            mensagem = client_socket.recv(1024).decode()
        except Exception as e:
            print(f"Erro na conexão: {e}")
            break

        if not mensagem:
            print("Cliente desconectado")
            break

        print(f"Mensagem recebida: {mensagem}")


def main():
    host, porta = carregar_configs()
    server_socket = cria_socket_server(host, porta)

    print(f"Servidor iniciado em {host} : {porta}")

    client_socket = aceita_cliente(server_socket)
    recebe_mensagens(client_socket)

    client_socket.close()
    server_socket.close()


if __name__ == "__main__":
    main()