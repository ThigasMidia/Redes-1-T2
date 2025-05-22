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
pontos = 0
while jogo == 1:
    #Flag de rodada inicializada. Enquanto 1, ainda há cartas nas maos dos jogadores e nao é necessario sorteá-las novamente
    rodada = 1
    #primeira vez que entra no loop, o "dono" da rodada cria a mensagem de rodada
    if dono == 1:
        roundCards = message.montaMensagem(myId, myId, 3, 0, [])
        dono = 0
    
    game.imprimeMao(maoAtual)
    #enquanto há cartas nas maos dos jogadores
    while rodada == 1:
        #se é seu turno de jogar
        if turno == 1:
            if len(roundCards) == 3:
                x = int(input("ESCOLHA UMA CARTA (DIGITE O NUMERO DA POSICAO):  "))
                while x < 1 or x > len(maoAtual):
                    x = int(input("O NUMERO DIGITADO NAO EXISTE, ESCOLHA OUTRO  "))
            else:
                naipe = game.decideNaipe(roundCards[3])
                if game.checaNaipe(maoAtual, naipe) == 1:
                    x = int(input("ESCOLHA UMA CARTA DO MESMO NAIPE DA PRIMEIRA (DIGITE O NUMERO DA POSICAO):  "))
                    while x < 1 or x > len(maoAtual) or game.decideNaipe(maoAtual[x-1]) != naipe:
                        x = int(input("ESTA CARTA NÃO EXISTE OU NÃO É DO MESMO NAIPE DA PRIMEIRA!!  "))
                else:
                    x = int(input("VOCE NAO POSSUI UMA CARTA DO MESMO NAIPE. ESCOLHA QUALQUER UMA (DIGITE O NUMERO DA POSICAO):  "))
                    while x < 1 or x > len(maoAtual):
                        x = int(input("O NUMERO DIGITADO NAO EXISTE, ESCOLHA OUTRO  "))

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
            loop = 1
            while loop == 1:
                if(message.checaMensagem(buf) == 1):
                    #Recebeu novamente a propria mensagem de print. Descarta e envia a mensagem com as cartas jogadas na rodada
                    if msg[2] == 4:
                        game.imprimeJogada(msg)
                        if msg[4] == 2:
                            sockt.sendto(roundCards, nextPc)
                        else:
                            printa = message.montaMensagem(winnerId, myId, 5, 1, [soma])
                            sockt.sendto(printa, nextPc)

                        buf, addr = sockt.recvfrom(1024)
                        msg = message.desmontaMensagem(buf)
                    
                    elif msg[2] == 5:
                        game.imprimeMao(maoAtual)
                        if msg[3] != 1:
                            pontos += msg[5][0]
                            roundCards = message.montaMensagem(myId, myId, 3, 0, [])
                    
                        else:
                            printa = message.montaMensagem(winnerId, myId, 0, 0, [])
                            sockt.sendto(printa, nextPc)
                            turno = 0
                        if len(maoAtual) == 0:
                            rodada = 0
                        loop = 0

                    #Se recebeu novamente a mensagem com as cartas jogadas na rodada
                    elif msg[2] == 3:
                        #Se tamanho 4, foi o último a jogar na rodada. É então o que checa o jogo
                        if msg[4] == 4:
                            winnerId = (myId + game.decideVencedor(roundCards)) % 4
                            soma = game.somaPontos(roundCards)
                            printa = message.montaMensagem(myId, myId, 4, 1, [winnerId])
                            sockt.sendto(printa, nextPc)
                            buf, addr = sockt.recvfrom(1024)
                            msg = message.desmontaMensagem(buf)
                            
                        #Passa o bastao
                        else:
                            bastao = message.montaMensagem(myId, myId, 0, 0, [])
                            sockt.sendto(bastao, nextPc)
                            turno = 0
                            loop = 0
                
        #se nao é seu turno de jogar
        else:
            roda, addr = sockt.recvfrom(1024)
            msg = message.desmontaMensagem(roda)
            #Recebe a mensagem
            if(message.checaMensagem(roda) == 1):
                #Se a mensagem é para print de jogada, o faz
                if msg[2] == 4:
                    game.imprimeJogada(msg)  
                    message.rebroadcast(roda, sockt, nextPc)
                elif msg[2] == 5:
                    game.imprimeMao(maoAtual)
                    roundCards = message.montaMensagem(myId, myId, 3, 0, [])
                    if msg[0] == myId:
                        pontos += msg[5][0]
                        message.broadcastAck(roda, sockt, nextPc)
                    else:
                        message.rebroadcast(roda, sockt, nextPc)
                #Se é mensagem de cartas da rodada, armazena os resultados e reenvia
                elif msg[2] == 3:
                    roundCards = bytearray(roda)  
                    message.rebroadcast(roda, sockt, nextPc)
                #Se é passagem de bastao, recebe o bastao
                elif msg[2] == 0:
                    if msg[1] != myId or msg[3] != 1:
                        pas = game.trataPassagem(msg, myId)
                        if pas == 0:
                            turno = 1
                        elif pas == 2:
                            turno = 1
                            message.broadcastAck(roda, sockt, nextPc)
                            if len(maoAtual) == 0:
                                rodada = 0
                        else:
                            message.rebroadcast(roda, sockt, nextPc)
                            if len(maoAtual) == 0:
                                rodada = 0


    if turno == 1:
        checaFim = message.montaMensagem(myId, myId, 6, 0, [])
        sockt.sendto(checaFim, nextPc)
        buf, addr = sockt.recvfrom(1024)
        print("DEPOIS DO BUF")
        msg = message.desmontaMensagem(buf)
        loop = 1
        while loop == 1 and jogo == 1:
            print("entrou LOOP")
            if(message.checaMensagem(buf) == 1):
                if msg[2] == 6:
                    if msg[4] != 0:
                        FIM = message.montaMensagem(myId, myId, 7, 0, [])
                        sockt.sendto(FIM, nextPc)

                    else:
                        maoAtual = game.comecaJogo(sockt, myId, nextPc)
                        game.iniciaConexao(sock, nextPc)
                        rodada = 1
                        loop = 0
                elif msg[2] == 7:
                    jogo = 0

    else:
        print("ELSE")
        roda, addr = sockt.recvfrom(1024)
        print("RECEBEU A PRIMEIRA DPS")
        msg = message.desmontaMensagem(roda)
        interludio = 1
        while interludio == 1 and jogo == 1:
            if(message.checaMensagem(roda) == 1):
                print("TA CHEGANDO DENTRO DESSE LOOP AQUI!")
                if msg[2] == 6:
                    print("TIPO 6!!!")
                    checaFim = bytearray(roda)
                    if pontos >= 100:
                        checaFim.append(pontos)
                        checaFim[2] = checaFim[2] & 0xF0
                        checaFim[2] += 16
                        checaFim[2] += message.calcChecksum(checaFim)
                    sockt.sendto(checaFim, nextPc)

                elif msg[2] == 7:
                    print("TIPO 7!!!")
                    jogo = 0
                    message.rebroadcast(roda, sockt, nextPc)

                elif msg[2] == 2:
                    print("TIPO 2!!!")
                    envio = bytearray(roda)
                    if msg[0] == myId:
                        maoAtual, envio = message.recebeCartas(msg, roda)
                    sockt.sendto(envio, nextPc)

                elif msg[2] == 1:
                    print("TIPO 1!!!")
                    interludio = 0
                    rodada = 1
                    message.rebroadcast(roda, sockt, nextPc)
