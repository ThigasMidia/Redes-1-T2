from aux import message

def trataPassagem(msg, myId, socket, nextPc):
    if msg[0] == msg[1]:
        return 1

    ret = 0
    if msg[0] == myId:
        print("OIIIIII")
        ret = 1
    
    newMessage = message.montaMensagem(msg[0], msg[1], msg[2], msg[4], msg[5])
    newMessage[1] += ret
    socket.sendto(newMessage, nextPc)
    return ret
