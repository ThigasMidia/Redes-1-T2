PORTA = 46961
MARCADOR_INI = 126

def calcChecksum(message):
    ret = (message[1] & 0xF0) + (message[1] & 0x0F) 
    tam = message[2] >> 4
    for i in range(3,tam+3):
        ret += (message[i] & 0xF0) + (message[i] & 0x0F)
    return ret % 16

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

def montaMensagem(destino, origem, tipo, tam, dados):
    message = bytearray()
    message.append(MARCADOR_INI)
    DOTA = ((((destino << 2) + origem) << 3) + tipo) << 1
    message.extend([DOTA, tam << 4])
    message[3:tam+2] = dados
    message[2] += calcChecksum(message)
    return message

def checaMensagem(message):
    if(message[0] != 126):
        return 0
    sum = calcChecksum(message)
    if(sum == message[2] & 0x0F):
        return 1
    return -1 
