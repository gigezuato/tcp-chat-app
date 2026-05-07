import socket
import os
from dotenv import load_dotenv
import threading


def carregar_configs():
    load_dotenv()

    host = os.getenv("SERVER_HOST", "127.0.0.1")
    porta = int(os.getenv("SERVER_PORT", 5000))
    return host, porta


def cria_socket_cliente():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def conecta_servidor(client_socket, host, porta):
    client_socket.connect((host, porta))
    print(f"Conectado ao servidor")


def envia_mensagens(client_socket, nome_usuario):
    while True:
        try:
            mensagem = input("> ")

            if mensagem.lower() == "/ajuda":
                print("Comandos disponíveis:")
                print("/sair - sair do chat")
                print("/ajuda - mostrar comandos")
                print("/saldo - mostrar saldo atual")
                print("/definir_saldo valor - definir saldo inicial")
                print("/gasto valor descrição - registrar gasto")
                print("/entrada valor descrição - registrar entrada")
                print("/resumo - mostrar resumo das transações")
                print("/usuarios - mostrar usuários conectados")
                continue
            if mensagem.lower() == "/sair":
                client_socket.shutdown(socket.SHUT_RDWR)
                break
            if mensagem.startswith("/"):
                client_socket.send(mensagem.encode())
                continue
            if not mensagem.strip():
                continue
            
            mensagem_formatada = f"[{nome_usuario}]: {mensagem}"
            client_socket.send(mensagem_formatada.encode())

        except OSError:
            break
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")
            break


def recebe_mensagens(client_socket):
    while True:
        try:
            mensagem = client_socket.recv(1024).decode()

            if not mensagem:
                print("Servidor encerrou a conexão")
                break

            print(f"\n{mensagem}\n")
            
        except OSError:
            break
        except Exception as e:
            print(f"Erro ao receber mensagem: {e}")
            break   


def main():
    host, porta = carregar_configs()
    client_socket = cria_socket_cliente()

    nome_usuario = input("Digite seu nome: ")
    if not nome_usuario:
        nome_usuario = "Usuário"

    conecta_servidor(client_socket, host, porta)
    client_socket.send(nome_usuario.encode())
    thread_receber = threading.Thread(target=recebe_mensagens, args=(client_socket,), daemon=True)
    thread_receber.start()
    envia_mensagens(client_socket, nome_usuario)
    
    client_socket.close()
    print(f"Conexão encerrada")


if __name__ == "__main__":
    main()