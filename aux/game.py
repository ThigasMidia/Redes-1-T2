from aux import message
import random

def trataPassagem(msg, myId, socket, nextPc):
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
    while it <= 51:
        if it < 13:
            maoA.append(deque[it])
        elif it >= 13 and it < 26:
            maoB.append(deque[it])
        elif it >= 26 and it < 39:
            maoC.append(deque[it])
        else:
            maoD.append(deque[it])
        it += 1

    ret = (maoA, maoB, maoC, maoD)
    return ret
