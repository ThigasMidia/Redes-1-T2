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

#msg = message.montaMensagem(3, 2, 1, 6, [4, 8, 16, 32, 64, 128])
#mensg = message.desmontaMensagem(msg)
#print(list(msg))
#print(mensg[0]) # destino
#print(mensg[1]) # origem
#print(mensg[2]) # tipo
#print(mensg[3]) # ack
#print(mensg[4]) # tam
#print(list(mensg[5])) # dados
#message.ackMessage(msg)
#print(list(msg)) 

#Pega o ID em argv
if len(sys.argv) != 2:
    print("ENTRADA ERRADA")
    sys.exit(1)

Id = sys.argv[1]
myId = 0

if Id == 'A':
    myId = 0
elif Id == 'B':
    myId = 1
elif Id == 'C':
    myId = 2
else:
    myId = 3

#Checa se o ID existe
if Id not in ANEL:
    print("OPCAO DE ID INVALIDA")
    sys.exit(1)


porta = ANEL[Id]["porta"]
nextId = ANEL[Id]["proxima"]

#Endereco do destino da mensagem do pc iniciado. guarda ip do proximo e porta do proximo
#No projeto, a porta sera a mesma para todos os computadores e o id deve ser pego de outra maneira
nextPc = (ANEL[nextId]["ip"], ANEL[nextId]["porta"])

#bind no socket
sockt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockt.bind((ANEL[Id]["ip"], porta))

mesage = message.montaMensagem(3, 1, 0, 0, [])

#D deve ser o ultimo a ser inicializado. Quando ele é inicializado, manda uma mensagem para A
#Que repassa pelo anel até chegar a D novamente, que vai receber a mensagem e decidir se 
#A mensagem foi manipualda corretamente pelo anel ou nao
if Id == "D":
    sockt.sendto(mesage , nextPc)
    dados, addr = sockt.recvfrom(1024)
    mesge = message.desmontaMensagem(dados)
    k = game.trataPassagem(mesge, myId, sockt, nextPc)
    print("MENSAGEM RECEBIDA: ", list(dados))
    if k == 1:
        print("DEU CERTO!!!")
    else:
        print("NAO ROLOU")
    print(list(dados))

#A mensagem tem como destino o B. caso seja B, adiciona outro byte à mensagem
#"dados" é uma constante, entao nao se pode fazer append. Devemos armazenar seu conteudo em outro
#bytearray e entao manipular como precisamos 
else:
    dados, addr = sockt.recvfrom(1024)
    print("MENSAGEM RECEBIDA: ", list(dados))
    louco = bytearray(dados)
    mesge = message.desmontaMensagem(dados)
    teste = game.trataPassagem(mesge, myId, sockt, nextPc)
