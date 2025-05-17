import socket
import sys

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


porta = ANEL[Id]["porta"]
nextId = ANEL[Id]["proxima"]

#Endereco do destino da mensagem do pc iniciado. guarda ip do proximo e porta do proximo
#No projeto, a porta sera a mesma para todos os computadores e o id deve ser pego de outra maneira
nextPc = (ANEL[nextId]["ip"], ANEL[nextId]["porta"])

#bind no socket
sockt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockt.bind((ANEL[Id]["ip"], porta))

#cria uma mensagem de 3 bytes
mensagem = bytearray()
mensagem.extend([130, 133, 111])

#D deve ser o ultimo a ser inicializado. Quando ele é inicializado, manda uma mensagem para A
#Que repassa pelo anel até chegar a D novamente, que vai receber a mensagem e decidir se 
#A mensagem foi manipualda corretamente pelo anel ou nao
if Id == "D":
    sockt.sendto(mensagem , nextPc)
    dados, addr = sockt.recvfrom(1024)
    print("MENSAGEM RECEBIDA: ", list(dados))
    if len(dados) == 4:
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
    if Id == "B":
        louco.append(98)
        print("PRA MIM: ", list(louco))
    else:
        print("NAO E PRA MIM ", len(dados))

    sockt.sendto(louco, nextPc)
