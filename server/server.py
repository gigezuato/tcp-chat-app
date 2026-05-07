import socket
import os
from dotenv import load_dotenv
import threading

clientes = []
nomes_usuarios = []
saldo = 0.0
transacoes = []

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


def formatar_valor(valor):
    return f"R$ {valor:.2f}".replace(".", ",")


def processa_comando_financeiro(mensagem, nome_usuario):
    global saldo
    partes = mensagem.split(maxsplit=2)
    comando = partes[0].lower()

    if comando == "/saldo":
        return f"Saldo atual: {formatar_valor(saldo)}"
    
    if comando == "/definir_saldo":
        if len(partes) < 2:
            return "Informe um valor! Exemplo: /definir_saldo 1000"
        try:
            novo_saldo = float(partes[1].replace(",", "."))
        except ValueError:
            return "Valor inválido! Siga o exemplo: /definir_saldo 1000"
        saldo = novo_saldo
        transacoes.append({
            "tipo": "Definição de saldo",
            "valor": novo_saldo,
            "descricao": "Saldo inicial definido",
            "usuario": nome_usuario
        })
        return f"Saldo definido por {nome_usuario}: {formatar_valor(saldo)}"
    
    if comando in ["/gasto", "/entrada"]:
        if len(partes) < 2:
            return f"Informe um valor! Exemplo: {comando} 50 mercado"
        try:
            valor = float(partes[1].replace(",", "."))
        except ValueError:
            return f"Valor inválido! Siga o exemplo: {comando} 50 mercado"
        if valor <= 0:
            return "O valor deve ser maior que zero!"
        descricao = partes[2] if len(partes) >= 3 else "sem descrição"

        if comando == "/gasto":
            saldo -= valor
            tipo = "gasto"
            resposta = f"Gasto registrado por {nome_usuario}: {formatar_valor(valor)} - {descricao}\nSaldo atual: {formatar_valor(saldo)}"
        else:
            saldo += valor
            tipo = "entrada"
            resposta = f"Entrada registrada por {nome_usuario}: {formatar_valor(valor)} - {descricao}\nSaldo atual: {formatar_valor(saldo)}"
        
        transacoes.append({
            "tipo": tipo,
            "valor": valor,
            "descricao": descricao,
            "usuario": nome_usuario
        })
        return resposta
    
    if comando == "/resumo":
        if not transacoes:
            return "Nenhuma transação registrada ainda."
        
        linhas = ["Resumo das transações:"]
        for indice, transacao in enumerate(transacoes, start=1):
            linhas.append(
                f"{indice}) {transacao['tipo']} - {formatar_valor(transacao['valor'])} "
                f"- {transacao['descricao']} por {transacao['usuario']}"
            )
        linhas.append(f"Saldo atual: {formatar_valor(saldo)}")
        return "\n".join(linhas)

    if comando == "/usuarios":
        return f"Usuários conectados: " + ", ".join(nomes_usuarios)
    
    return "Comando não reconhecido. Digite /ajuda para ver os comandos disponíveis."



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
        if mensagem.startswith("/"):
            resposta = processa_comando_financeiro(mensagem, nome_usuario)
            client_socket.send(f"[Servidor]: {resposta}".encode())
            continue

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
        try:
            nome_usuario = client_socket.recv(1024).decode()
            if not nome_usuario:
                nome_usuario = "Usuário"
        except Exception as e:
            print(f"Erro ao receber nome do usuário: {e}")
            client_socket.close()
            continue

        clientes.append(client_socket)
        nomes_usuarios.append(nome_usuario)

        broadcast(f"{nome_usuario} entrou no chat", client_socket)

        thread_cliente = threading.Thread(target=recebe_mensagens, args=(client_socket, nome_usuario))
        thread_cliente.start()


if __name__ == "__main__":
    main()