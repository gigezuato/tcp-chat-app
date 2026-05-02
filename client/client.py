import socket
import os
from dotenv import load_dotenv

def carregar_configs():
    load_dotenv()

    host = os.getenv("SERVER_HOST", "127.0.0.1")
    porta = int(os.getenv("SERVER_PORT", 5000))
    return host, porta


def cria_socket_cliente():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def conecta_servidor(client_socket, host, porta):
    client_socket.connect((host, porta))
    print("Conectado ao servidor")


def envia_mensagens(client_socket):
    while True:
        mensagem = input("Digite uma mensagem: ")

        if mensagem.lower() == "sair":
            break

        client_socket.send(mensagem.encode())


def main():
    host, porta = carregar_configs()
    client_socket = cria_socket_cliente()

    conecta_servidor(client_socket, host, porta)
    envia_mensagens(client_socket)
    
    client_socket.close()


if __name__ == "__main__":
    main()