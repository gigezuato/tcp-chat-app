import socket
import os
from dotenv import load_dotenv
import threading

clientes = []
nomes_usuarios = []

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


def recebe_mensagens(client_socket, nome_usuario):
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
        broadcast(mensagem, client_socket)

    try:
        client_socket.close()
    except:
        pass

    if client_socket in clientes:
        index = clientes.index(client_socket)
        clientes.remove(client_socket)
        nomes_usuarios.pop(index)
        
    broadcast(f"{nome_usuario} saiu do chat", client_socket)


def broadcast(mensagem, sender):
    for cliente in clientes[:]:
        if cliente != sender:
            try:
                cliente.send(mensagem.encode())
            except Exception as e:
                print(f"Erro ao enviar mensagem: {e}")
                try:
                    cliente.close()
                except:
                    pass
                if cliente in clientes:
                    clientes.remove(cliente)


def main():
    host, porta = carregar_configs()
    server_socket = cria_socket_server(host, porta)

    print(f"Servidor iniciado em {host} : {porta}")

    while True:
        client_socket = aceita_cliente(server_socket)
        nome_usuario = client_socket.recv(1024).decode()

        clientes.append(client_socket)
        nomes_usuarios.append(nome_usuario)

        broadcast(f"{nome_usuario} entrou no chat", client_socket)

        thread_cliente = threading.Thread(target=recebe_mensagens, args=(client_socket, nome_usuario))
        thread_cliente.start()


if __name__ == "__main__":
    main()