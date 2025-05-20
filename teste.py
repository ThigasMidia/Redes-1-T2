import socket
import sys
from aux import message , game

#Definicao de nomes para facilitar
ANEL = {
    "A": {"porta": 46961, "proxima": "B", "ip": "127.0.0.1"},
    "B": {"porta": 46962, "proxima": "C", "ip": "127.0.0.1"},
    "C": {"porta": 46963, "proxima": "D", "ip": "127.0.0.1"},
    "D": {"porta": 46964, "proxima": "A", "ip": "127.0.0.1"},
}

#Pega o ID em argv
if len(sys.argv) != 2:
    print("ENTRADA ERRADA")
    sys.exit(1)

Id = sys.argv[1]

#Checa se o ID existe
if Id not in ANEL:
    print("OPCAO DE ID INVALIDA")
    sys.exit(1)

myId = 0

if Id == 'B':
    myId = 1
elif Id == 'C':
    myId = 2
elif Id == 'D':
    myId = 3

porta = ANEL[Id]["porta"]
nextId = ANEL[Id]["proxima"]

#Endereco do destino da mensagem do pc iniciado. guarda ip do proximo e porta do proximo
#No projeto, a porta sera a mesma para todos os computadores e o id deve ser pego de outra maneira
nextPc = (ANEL[nextId]["ip"], ANEL[nextId]["porta"])

#bind no socket
sockt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockt.bind((ANEL[Id]["ip"], porta))

maoAtual = bytearray()
jogo = 1

#D deve ser o ultimo a ser inicializado. Quando ele é inicializado, manda uma mensagem para A
#Que repassa pelo anel até chegar a D novamente, que vai receber a mensagem
if myId == 3:
    game.iniciaConexao(sockt, nextPc)
    maoAtual = game.comecaJogo(sockt, myId, nextPc)
    print(list(maoAtual))
    buffer = message.montaMensagem(3, 3, 7, 0, [])
    sockt.sendto(buffer, nextPc)
    dados, addr = sockt.recvfrom(1024)
    msg = message.desmontaMensagem(dados)
    if msg[2] == 7:
        print("DEU CERTO!!!!!")
    else:
        print("NAO ROLOU")

#A mensagem tem como destino o B. caso seja B, adiciona outro byte à mensagem
#"dados" é uma constante, entao nao se pode fazer append. Devemos armazenar seu conteudo em outro
#bytearray e entao manipular como precisamos 
else:
    dados, addr = sockt.recvfrom(1024)
    sockt.sendto(dados, nextPc)
    while jogo == 1:
        dados, addr = sockt.recvfrom(1024)
        msg = message.desmontaMensagem(dados)
        if(message.checaMensagem(dados) == 1):
            if msg[2] == 7:
                jogo = 0
                sockt.sendto(dados, nextPc)
            else:
                envio = bytearray(dados)
                if msg[0] == myId:
                    maoAtual = bytearray(msg[5])
                    envio[1] += 1
                    envio[2] = envio[2] & 0xF0
                    envio[2] += message.calcChecksum(envio)
            
                sockt.sendto(envio, nextPc)
        else:
            sockt.sendto(dados, nextPc)
    
    print(list(maoAtual))
