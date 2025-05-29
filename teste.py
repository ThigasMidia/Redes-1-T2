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

nome1 = socket.gethostname()
tamNome = len(nome1)

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

#print(nome1)
#aux = int(nome1[tamNome-1])
#print(aux)
#if myId == 3:
#    aux -= 3
#else:
#    aux += 1

#nome = nome1[:tamNome-1] + str(aux)
#print(aux)
#ipMeu = socket.gethostbyname(nome1)
#ipProx = socket.gethostbyname(nome)

porta = ANEL[Id]["porta"]
nextId = ANEL[Id]["proxima"]

#Endereco do destino da mensagem do pc iniciado. guarda ip do proximo e porta do proximo
#No projeto, a porta sera a mesma para todos os computadores e o id deve ser pego de outra maneira

#nextPc = (ipProx, 46961)
nextPc = (ANEL[nextId]["ip"], ANEL[nextId]["porta"])

#bind no socket
sockt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockt.bind((ANEL[Id]["ip"], porta))

maoAtual = bytearray()
jogo = 1

#D deve ser o ultimo a ser inicializado. Quando ele é inicializado, manda uma mensagem para A
#Que repassa pelo anel até chegar a D novamente, que vai receber a mensagem e começar o jogo
if myId == 3:
    game.iniciaConexao(sockt, nextPc)
    maoAtual = game.comecaJogo(sockt, myId, nextPc)
    game.iniciaConexao(sockt, nextPc)

#Espera a mensagem de inicio de conexao, espera para receber as cartas do primeiro sorteio e depois espera novamente
#o começo da conexao (começo do jogo)
else:
    dados, msg = message.recebeMensagem(sockt)
    message.rebroadcast(dados, sockt, nextPc)
    #Enquanto a segunda mensagem de conexao nao é recebida
    while jogo == 1:
        dados, msg = message.recebeMensagem(sockt)
        #Caso a mensagem esteja correta
        if(message.checaMensagem(dados) == 1):
            #Se é mensagem de conexao, sai do loop
            if msg[message.MSG_TYPE] == message.CONNECT:
                jogo = 0
                message.rebroadcast(dados, sockt, nextPc)
            #Recebe as cartas
            else:
                envio = bytearray(dados)
                if msg[message.MSG_DEST] == myId:
                    maoAtual, envio = game.recebeCartas(msg, dados)
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
        roundCards = message.montaMensagem(myId, myId, message.ROUND, 0, [])
        dono = 0
    
    game.imprimeMao(maoAtual, pontos)
    #enquanto há cartas nas maos dos jogadores
    while rodada == 1:
        #se é seu turno de jogar
        if turno == 1:
            #Se você é o primeiro a jogar na rodada, voce decidira o naipe da rodada
            x = game.lePosicao(roundCards, maoAtual)
            #Coloca no vetor roundCards a carta jogada
            roundCards = game.jogaCarta(roundCards, maoAtual[x-1]) 
            #Cria mensagem de print, que diz o ID do jogador e o numero da carta (PRECISA DE AJUSTES)
            printa = message.montaMensagem(myId, myId, message.PRINT, 2, [myId, maoAtual[x-1]])
            #remove da mao do jogador a carta jogada
            game.removeCarta(maoAtual, x-1)

            sockt.sendto(printa, nextPc)
            buf, msg = message.recebeMensagem(sockt)
            #Loop de tratamento de todas as outras mensagens até passagem do bastao
            loop = 1
            while loop == 1:
                if(message.checaMensagem(buf) == 1):
                    #Recebeu novamente a propria mensagem de print. Descarta e envia a mensagem com as cartas jogadas na rodada
                    if msg[message.MSG_TYPE] == message.PRINT:
                        game.imprimeJogada(msg)
                        if msg[message.MSG_SIZE] == 2:
                            sockt.sendto(roundCards, nextPc)
                        #Recebeu novamente a mensagem de quem ganhou a partida, entao envia os pontos para o vencedor
                        else:
                            printa = message.montaMensagem(winnerId, myId, message.POINTS, 1, [soma])
                            sockt.sendto(printa, nextPc)
                        
                        buf, msg = message.recebeMensagem(sockt)
                    
                    #Se recebeu novamente a mensagem dos pontos
                    elif msg[message.MSG_TYPE] == message.POINTS:
                        #Se sou eu o destino
                        if msg[message.MSG_ACK] != 1:
                            pontos += msg[message.MSG_DATA][0]
                            #Reseta a rodada
                            roundCards = message.montaMensagem(myId, myId, message.ROUND, 0, [])
                            printa = message.montaMensagem(myId, myId, message.CONNECT, 0, [])
                        
                        #Se nao sou eu o destino
                        else:
                            #Passagem de bastao para o vencedor
                            printa = message.montaMensagem(winnerId, myId, message.BATON, 0, [])
                            turno = 0
                        
                        #passa bastao ou inicia uma nova rodada
                        sockt.sendto(printa, nextPc)
                        buf, msg = message.recebeMensagem(sockt)
                        #Se acabaram as cartas da mao
                        if len(maoAtual) == 0:
                            rodada = 0
                        loop = 0
                        game.imprimeMao(maoAtual, pontos)

                    #Se recebeu novamente a mensagem com as cartas jogadas na rodada
                    elif msg[message.MSG_TYPE] == message.ROUND:
                        #Se tamanho 4, foi o último a jogar na rodada. É então o que checa o jogo
                        if msg[message.MSG_SIZE] == 4:
                            #Decide Id do vencedor
                            winnerId = (myId + game.decideVencedor(roundCards)) % 4
                            soma = game.somaPontos(roundCards)
                            #Printa quem foi o vencedor da rodada
                            printa = message.montaMensagem(myId, myId, message.PRINT, 1, [winnerId])
                            sockt.sendto(printa, nextPc)
                            buf, msg = message.recebeMensagem(sockt)
                            
                        #Passa o bastao
                        else:
                            bastao = message.montaMensagem(myId, myId, message.BATON, 0, [])
                            sockt.sendto(bastao, nextPc)
                            turno = 0
                            loop = 0
                
        #se nao é seu turno de jogar
        else:
            roda, msg = message.recebeMensagem(sockt)
            #Recebe a mensagem
            if(message.checaMensagem(roda) == 1):
                #Se a mensagem é para print de jogada, o faz e repassa
                if msg[message.MSG_TYPE] == message.PRINT:
                    game.imprimeJogada(msg)  
                    message.rebroadcast(roda, sockt, nextPc)

                #Se a mensagem é para soma de pontos
                elif msg[message.MSG_TYPE] == message.POINTS:
                    #Reseta as cartas da rodada
                    roundCards = message.montaMensagem(myId, myId, message.ROUND, 0, [])
                    #Se eu fui o vencedor
                    if msg[message.MSG_DEST] == myId:
                        pontos += msg[message.MSG_DATA][0]
                        game.imprimeMao(maoAtual, pontos)
                        message.broadcastAck(roda, sockt, nextPc)
                    else:
                        game.imprimeMao(maoAtual, pontos)
                        message.rebroadcast(roda, sockt, nextPc)

                #Se é mensagem de inicio de rodada
                elif msg[message.MSG_TYPE] == message.CONNECT:
                    if len(maoAtual) == 0:
                        rodada = 0
                    message.rebroadcast(roda, sockt, nextPc)

                #Se é mensagem de cartas da rodada, armazena os resultados e reenvia
                elif msg[message.MSG_TYPE] == message.ROUND:
                    roundCards = bytearray(roda)  
                    message.rebroadcast(roda, sockt, nextPc)

                #Se é passagem de bastao
                elif msg[message.MSG_TYPE] == message.BATON:
                    if msg[message.MSG_ORIG] != myId or msg[message.MSG_ACK] != 1:
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

    #Loop de fim de jogo. Checa se o jogo acabou. Se não, redistriui as cartas e volta para o loop anterior
    if turno == 1:
        #Envia mensagem de checagem de Fim de Jogo
        checaFim = message.montaMensagem(myId, myId, message.CHECK, 0, [])
        message.enviaChecaFim(checaFim, pontos, sockt, nextPc)
        buf, msg = message.recebeMensagem(sockt)
        loop = 1
        #Enquanto nao checar todos os jogadores
        while loop == 1 and jogo == 1:
            if(message.checaMensagem(buf) == 1):
                #Se receber novamente a mensagem de checagem
                if msg[message.MSG_TYPE] == message.CHECK:
                    #Se alguem alcançou 33 pontos ou mais
                    if game.checa33Pontos(msg[message.MSG_SIZE], msg[message.MSG_DATA]) == 1:
                        #Armazena quem e quantos ganharam
                        vencedor, quantos = game.decideVencedorJogo(myId, msg[message.MSG_SIZE], msg[message.MSG_DATA])
                        #Envia mensagem de fim de jogo
                        FIM = message.montaMensagem(myId, myId, message.END, quantos, vencedor)
                        sockt.sendto(FIM, nextPc)
                        buf, msg = message.recebeMensagem(sockt)

                    #Se ninguem alcançou 33 pontos ou mais
                    else:
                        #Sorteia novamente as cartas
                        maoAtual = game.comecaJogo(sockt, myId, nextPc)
                        game.iniciaConexao(sockt, nextPc)
                        loop = 0
                
                #Se recebeu a mensagem de fim de jogo
                elif msg[message.MSG_TYPE] == message.END:
                    #Acaba o jogo e printa resultados
                    jogo = 0
                    game.printFim(msg)

    else:
        interludio = 1
        while interludio == 1 and jogo == 1:
            roda, msg = message.recebeMensagem(sockt)
            if(message.checaMensagem(roda) == 1):
                #Se é mensagem de checagem
                if msg[message.MSG_TYPE] == message.CHECK:
                    #Concatena quantidade de pontos em checaFim e envia novamente
                    checaFim = bytearray(roda)
                    message.enviaChecaFim(checaFim, pontos, sockt, nextPc)
                
                #Se é fim de jogo, repassa a mensagem e printa os resultados
                elif msg[message.MSG_TYPE] == message.END:
                    jogo = 0
                    message.rebroadcast(roda, sockt, nextPc)
                    game.printFim(msg)

                #Se esta recebendo a mao novamente
                elif msg[message.MSG_TYPE] == message.SENDHAND:
                    envio = bytearray(roda)
                    if msg[message.MSG_DEST] == myId:
                        maoAtual, envio = game.recebeCartas(msg, roda)
                    sockt.sendto(envio, nextPc)
                
                #Se esta começando a rodada
                elif msg[message.MSG_TYPE] == message.CONNECT:
                    interludio = 0
                    message.rebroadcast(roda, sockt, nextPc)

