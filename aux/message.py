MARCADOR_INI = 126
PORTA = 46964

#Macros de elementos da mensagem
MSG_DEST = 0
MSG_ORIG = 1
MSG_TYPE = 2
MSG_ACK = 3
MSG_SIZE = 4
MSG_DATA = 5

#Macros de tipo de mensagem
BATON = 0
CONNECT = 1
SENDHAND = 2
ROUND = 3
PRINT = 4
POINTS = 5
CHECK = 6
END = 7

#Calcula checksum
def calcChecksum(message):
    ret = (message[1] & 0xF0) + (message[1] & 0x0F) 
    tam = message[2] >> 4
    for i in range(3,tam+1):
        ret += (message[i] & 0xF0) + (message[i] & 0x0F)
    return ret % 16

#Desmonta um buffer de mensagem numa tupla
def desmontaMensagem(message):
    destino = message[1] >> 6
    origem = (message[1] & 48) >> 4
    tipo = (message[1] & 0x0E) >> 1
    ack = message[1] & 0x01
    tam = message[2]  >> 4
    dados = bytearray()
    dados[0:tam-1] = message[3:tam+3]
    msg = (destino, origem, tipo, ack, tam, dados)
    return msg

#Monta dados em um buffer de mensagem
def montaMensagem(destino, origem, tipo, tam, dados):
    message = bytearray()
    message.append(MARCADOR_INI)
    DOTA = ((((destino << 2) + origem) << 3) + tipo) << 1
    message.extend([DOTA, tam << 4])
    message[3:tam+2] = dados
    message[2] += calcChecksum(message)
    return message

#Faz o checksum
def checaMensagem(message):
    if(message[0] != 126):
        return 0
    sum = calcChecksum(message)
    if(sum == message[2] & 0x0F):
        return 1
    return -1

#Troca o Ack da mensagem para 1 e repassa
def broadcastAck(buffer, socket, nextPc):
    buf = bytearray(buffer)
    buf[1] += 1
    buf[2] = buf[2] & 0xF0
    buf[2] += calcChecksum(buf)
    socket.sendto(buf, nextPc)

#Repassa mensagem
def rebroadcast(buffer, socket, nextPc):
    socket.sendto(buffer, nextPc)

#Recebe mensagem
def recebeMensagem(socket):
    buf, addr = socket.recvfrom(1024)
    msg = desmontaMensagem(buf)
    return buf, msg

#Concatena pontos, recalcula checksum e envia
def enviaChecaFim(checaFim, pontos, socket, nextPc):
    checaFim.append(pontos)
    checaFim[2] = checaFim[2] & 0xF0
    checaFim[2] += 16
    checaFim[2] += calcChecksum(checaFim)
    socket.sendto(checaFim, nextPc)
