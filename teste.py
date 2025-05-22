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
turno = 0
dono = 0

if Id == 'B':
    myId = 1
elif Id == 'C':
    myId = 2
elif Id == 'D':
    myId = 3
    turno = 1
    dono = 1

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
    game.iniciaConexao(sockt, nextPc)

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
            if msg[2] == 1:
                jogo = 0
                message.rebroadcast(dados, sockt, nextPc)
            else:
                envio = bytearray(dados)
                if msg[0] == myId:
                    maoAtual, envio = message.recebeCartas(msg, dados)
                sockt.sendto(envio, nextPc)
        else:
            message.rebroadcast(dados, sockt, nextPc)


#Loop principal de jogo
jogo = 1
while jogo == 1:
    #Flag de rodada inicializada. Enquanto 1, ainda há cartas nas maos dos jogadores e nao é necessario sorteá-las novamente
    rodada = 1
    #primeira vez que entra no loop, o "dono" da rodada cria a mensagem de rodada
    if dono == 1:
        roundCards = message.montaMensagem(myId, myId, 3, 0, [])
        dono = 0
    
    #enquanto há cartas nas maos dos jogadores
    while rodada == 1:
        #se é seu turno de jogar
        if turno == 1:
            game.imprimeMao(maoAtual)
            x = int(input("ESCOLHA UMA CARTA (DIGITE O NUMERO DA POSICAO):  "))
            #Coloca no vetor roundCards a carta jogada
            roundCards = game.jogaCarta(roundCards, maoAtual[x-1]) 
            #Cria mensagem de print, que diz o ID do jogador e o numero da carta (PRECISA DE AJUSTES)
            printa = message.montaMensagem(myId, myId, 4, 2, [myId, maoAtual[x-1]])
            #remove da mao do jogador a carta jogada
            game.removeCarta(maoAtual, x-1)
            sockt.sendto(printa, nextPc)
            buf, addr = sockt.recvfrom(1024)
            msg = message.desmontaMensagem(buf)
            #Loop de tratamento de todas as outras mensagens até passagem do bastao
            while turno == 1:
                if(message.checaMensagem(buf) == 1):
                    #Recebeu novamente a propria mensagem de print. Descarta e envia a mensagem com as cartas jogadas na rodada
                    if msg[2] == 4:
                        sockt.sendto(roundCards, nextPc)
                        buf, addr = sockt.recvfrom(1024)
                        msg = message.desmontaMensagem(buf)
                    #Se recebeu novamente a mensagem com as cartas jogadas na rodada
                    elif msg[2] == 3:
                        #Se tamanho 4, foi o último a jogar na rodada. É então o que checa o jogo
                        if msg[4] == 4:
                            print("qualquer coisa")
                            #LOOP DE CHECAGEM DE QUEM GANHOU O TURNO
                        #Passa o bastao
                        else:
                            bastao = message.montaMensagem(myId, myId, 0, 0, [])
                            sockt.sendto(bastao, nextPc)
                            turno = 0
                
        #se nao é seu turno de jogar
        else:
            roda, addr = sockt.recvfrom(1024)
            msg = message.desmontaMensagem(roda)
            #Recebe a mensagem
            if(message.checaMensagem(roda) == 1):
                #Se a mensagem é para print de jogada, o faz
                if msg[2] == 4:
                    game.imprimeJogada(msg[5])  
                    message.rebroadcast(roda, sockt, nextPc)
                #Se é mensagem de cartas da rodada, armazena os resultados e reenvia
                elif msg[2] == 3:
                    roundCards = bytearray(roda)  
                    message.rebroadcast(roda, sockt, nextPc)
                #Se é passagem de bastao, recebe o bastao
                elif msg[2] == 0:
                    pas = game.trataPassagem(msg, myId)
                    if pas == 0:
                        turno = 1

    print("FIM DE JOGO??")
    jogo = 0
