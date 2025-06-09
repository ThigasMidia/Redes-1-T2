from aux import message
import random

#Trata passagem de bastao
def trataPassagem(msg, myId):
    if msg[message.MSG_DEST] == msg[message.MSG_ORIG] and msg[message.MSG_ACK] != 1:
        return 0

    ret = 1
    if msg[message.MSG_DEST] == myId:
        ret = 2
    
    return ret

#Inicia rodadas
def iniciaConexao(socket, nextPc):
    inicio = message.montaMensagem(3, 3, message.CONNECT, 0, [])
    socket.sendto(inicio, nextPc)
    dados, addr = socket.recvfrom(1024)

#Embaralha e distribui cartas
def comecaJogo(socket, myId, nextPc):
    deque = geraMaos()
    it = 0
    while it < 4:
        atual = bytearray(deque[it])
        if it != myId:
            cartas = message.montaMensagem(it, myId, message.SENDHAND, 13, atual)
            socket.sendto(cartas, nextPc)
            bufferReceive, addr = socket.recvfrom(1024)
            messageReceive = message.desmontaMensagem(bufferReceive)
            if(messageReceive[message.MSG_ACK] == 0):
                it -= 1

        else:
            ret = bytearray(atual)

        it += 1

    return ret

#Recebe as cartas enviadas
def recebeCartas(msg, dados):
    envio = bytearray(dados)
    maoAtual = bytearray(msg[message.MSG_DATA])
    envio[1] += 1
    envio[2] = envio[2] & 0xF0
    envio[2] += message.calcChecksum(envio)
    return maoAtual, envio
    
#Embaralha cartas
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
    #maoA.append(50)
    #maoB.append(44)
    #maoC.append(45)
    #maoD.append(51)
    maoA[0:13] = deque[0:13]
    maoB[0:13] = deque[13:26]
    maoC[0:13] = deque[26:39]
    maoD[0:13] = deque[39:52]
    ret = (maoA, maoB, maoC, maoD)
    return ret

#Decide naipe da carta
def decideNaipe(Card):
    if Card <= 12:
        naipe = 1
    elif Card >= 13 and Card <= 25:
        naipe = 2
    elif Card >= 26 and Card <= 38:
        naipe = 3
    else:
        naipe = 4
    return naipe

#Checa se possui na mao uma carta do naipe da rodada
def checaNaipe(maoAtual, naipe):
    ret = 0
    it = 0
    while ret == 0 and it < len(maoAtual):
        if decideNaipe(maoAtual[it]) == naipe:
            ret = 1
        it += 1
    return ret

#Faz a soma de pontos da rodada
def somaPontos(roundCards):
    soma = 0
    for i in range(3, 7):
        if decideNaipe(roundCards[i]) == 4:
            soma += 1
        elif roundCards[i] == 10:
            soma += 10

    return soma

#Decide quem ganhou a rodada
def decideVencedor(roundCards):
    naipe = decideNaipe(roundCards[3])
    bigger = 1
    for i in range (4,7):
        if decideNaipe(roundCards[i]) == naipe and roundCards[i] > roundCards[bigger+2]:
            bigger = i-2
    return bigger

#Se o jogo acabou, decide quem ganhou
def decideVencedorJogo(myId, tam, pontos):
    i = 0
    menor = 33
    vencedores = bytearray()
    for i in range(0, tam):
        if pontos[i] < menor:
            menor = pontos[i]

    for i in range(0, tam):
        if pontos[i] == menor:
            vencedores.append(i)
    
    ret = bytearray()
    tam = 0
    for i in range(0, len(vencedores)):
        ret.append((myId + vencedores[i]) % 4)
        tam += 1
    return ret, tam

#Checa se alguém ja alcançou 33 pontos
def checa33Pontos(tam, dados):
    flag = 0
    i = 0
    while i < tam and flag == 0:
        if dados[i] >= 33:
            flag = 1
        i += 1
    return flag 

#Remove carta da mão
def removeCarta(mao, numero):
    mao.pop(numero)

#Joga carta na rodada
def jogaCarta(roundCards, carta):
    roundCards.append(carta)
    roundCards[2] = roundCards[2] & 0xF0
    roundCards[2] += 16
    roundCards[2] += message.calcChecksum(roundCards)
    return roundCards 
