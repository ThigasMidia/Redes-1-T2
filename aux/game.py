from aux import message
import random

def trataPassagem(msg, myId):
    if msg[0] == msg[1]:
        return 0

    ret = 1
    if msg[0] == myId:
        ret = 2
    
    return ret

def iniciaConexao(socket, nextPc):
    inicio = message.montaMensagem(3, 3, 1, 0, [])
    socket.sendto(inicio, nextPc)
    dados, addr = socket.recvfrom(1024)

def comecaJogo(socket, myId, nextPc):
    deque = geraMaos()
    it = 0
    while it < 4:
        atual = bytearray(deque[it])
        if it != myId:
            cartas = message.montaMensagem(it,myId,2,13,atual)
            socket.sendto(cartas, nextPc)
            bufferReceive, addr = socket.recvfrom(1024)
            messageReceive = message.desmontaMensagem(bufferReceive)
            if(messageReceive[3] == 0):
                it -= 1

        else:
            ret = bytearray(atual)

        it += 1

    return ret

def numToCarta(num):
    if num == 0 or num == 13 or num == 26 or num == 39:
        return "2"
    elif num == 1 or num == 14 or num == 27 or num == 40:
        return "3"
    elif num == 2 or num == 15 or num == 28 or num == 41:
        return "4"
    elif num == 3 or num == 16 or num == 29 or num == 42:
        return "5"
    elif num == 4 or num == 17 or num == 30 or num == 43:
        return "6"
    elif num == 5 or num == 18 or num == 31 or num == 44:
        return "7"
    elif num == 6 or num == 19 or num == 32 or num == 45:
        return "8"
    elif num == 7 or num == 20 or num == 33 or num == 46:
        return "9"
    elif num == 8 or num == 21 or num == 34 or num == 47:
        return "10"
    elif num == 9 or num == 22 or num == 35 or num == 48:
        return "J"
    elif num == 10 or num == 23 or num == 36 or num == 49:
        return "Q"
    elif num == 11 or num == 24 or num == 37 or num == 50:
        return "K"
    elif num == 12 or num == 25 or num == 38 or num == 51:
        return "A"

def imprimeMao(mao):
    tam = len(mao)
    for i in range(0, tam):
        if mao[i] <= 12:
            print("♠", numToCarta(mao[i]), "  ", end="")
        elif mao[i] >= 13 and mao[i] <= 25:
            print("♦", numToCarta(mao[i]), "  ", end="")
        elif mao[i] >= 26 and mao[i] <= 38:
            print("♣", numToCarta(mao[i]), "  ", end="")
        else:
            print("♥", numToCarta(mao[i]), "  ", end="")
    print()
    
def geraMaos():
    it = 0

    deque = bytearray()
    while it <= 51:
        deque.append(it)
        it += 1
    random.shuffle(deque)

    maoA = bytearray()
    maoB = bytearray()
    maoC = bytearray()
    maoD = bytearray()
    it = 0
    maoA[0:13] = deque[0:13]
    maoB[0:13] = deque[13:26]
    maoC[0:13] = deque[26:39]
    maoD[0:13] = deque[39:52]
    ret = (maoA, maoB, maoC, maoD)
    return ret

def decideNaipe(roundCards):
    if roundCards <= 12:
        naipe = 1
    elif roundCards >= 13 and roundCards <= 25:
        naipe = 2
    elif roundCards >= 26 and roundCards <= 38:
        naipe = 3
    else:
        naipe = 4
    return naipe

def checaNaipe(maoAtual, naipe):
    ret = 0
    it = 0
    while ret == 0 and it < len(maoAtual):
        if decideNaipe(maoAtual[it]) == naipe:
            ret = 1
        it += 1
    return ret

def somaPontos(roundCards):
    soma = 0
    for i in range(3, 7):
        if decideNaipe(roundCards[i]) == 4:
            soma += 1
        elif roundCards[i] == 10:
            soma += 10

    return soma

def decideVencedor(roundCards):
    naipe = decideNaipe(roundCards[3])
    bigger = 1
    for i in range (4,7):
        if decideNaipe(roundCards[i]) == naipe and roundCards[i] > roundCards[bigger+2]:
            bigger = i-2
    return bigger

def imprimeJogada(msg):
    if msg[4] == 2:
        print("JOGADOR ", msg[5][0]," JOGOU A CARTA ", end="")
        naipe = decideNaipe(msg[5][1])
        num = numToCarta(msg[5][1])
        if naipe == 1:
            print("♠ ", end="")
        elif naipe == 2:
            print("♦ ", end="")
        elif naipe == 3:
            print("♣ ", end="")
        else:
            print("♥ ", end="")
        print(num)
    elif msg[4] == 1:
        print("JOGADOR ", msg[5][0]," VENCEU A RODADA!!!")
    else:
        print("JOGADOR", msg[5][0]," VENCEU O JOGO!!!")

def removeCarta(mao, numero):
    mao.pop(numero)

def jogaCarta(roundCards, carta):
    roundCards.append(carta)
    roundCards[2] = roundCards[2] & 0xF0
    roundCards[2] += 16
    roundCards[2] += message.calcChecksum(roundCards)
    return roundCards 
