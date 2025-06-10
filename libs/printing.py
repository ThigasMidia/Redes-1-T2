from libs import game, message

#Pega o numero (0-51) e transforma na carta
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

#Imprime a mão do jogador e a quantidade de pontos de cada jogador
def imprimeMao(mao, pontos):
    tam = len(mao)
    for i in range(0, tam):
        carac = str(i+1)
        if mao[i] <= 12:
            print("♠", numToCarta(mao[i]), "(" + carac + ") ")
        elif mao[i] >= 13 and mao[i] <= 25:
            print("♦", numToCarta(mao[i]), "(" + carac + ") ")
        elif mao[i] >= 26 and mao[i] <= 38:
            print("♣", numToCarta(mao[i]), "(" + carac + ") ")
        else:
            print("♥", numToCarta(mao[i]), "(" + carac + ") ")

    print("PONTOS DO JOGADOR A: ", pontos[0])
    print("PONTOS DO JOGADOR B: ", pontos[1])
    print("PONTOS DO JOGADOR C: ", pontos[2])
    print("PONTOS DO JOGADOR D: ", pontos[3])

#Le a carta que o jogador deseja jogar, impimindo conforme as ações
def lePosicao(roundCards, maoAtual):
    if len(roundCards) == 3:
        posi = input("ESCOLHA UMA CARTA (DIGITE O NÚMERO DA POSIÇÃO):  ")
        while posi.isnumeric() == False:
            posi = input("DIGITE UM NÚMERO!!!!  ")
        posicao = int(posi)
        while posicao < 1 or posicao > len(maoAtual):
            posi = input("ESTA CARTA NÃO EXISTE!!  ")
            while posi.isnumeric() == False:
                posi = input("DIGITE UM NÚMERO!!!!  ")
            posicao = int(posi)
    else:
        naipe = game.decideNaipe(roundCards[3])
        if game.checaNaipe(maoAtual, naipe) == 1:
            posi = input("ESCOLHA UMA CARTA DO MESMO NAIPE DA PRIMEIRA (DIGITE O NÚMERO DA POSIÇÃO):  ")
            while posi.isnumeric() == False:
                posi = input("DIGITE UM NÚMERO!!!!  ")
            posicao = int(posi)
            while posicao < 1 or posicao > len(maoAtual) or game.decideNaipe(maoAtual[posicao-1]) != naipe:
                posi = input("ESTA CARTA NÃO EXISTE OU NÃO É DO MESMO NAIPE DA PRIMEIRA!!  ")
                while posi.isnumeric() == False:
                    posi = input("DIGITE UM NÚMERO!!!!  ")
                posicao = int(posi)
        else:
            posi = input("VOCE NÃO POSSUI UMA CARTA DO MESMO NAIPE. ESCOLHA QUALQUER UMA (DIGITE O NÚMERO DA POSIÇÃO)  ")
            while posi.isnumeric() == False:
                posi = input("DIGITE UM NÚMERO!!!!  ")
            posicao = int(posi)
            while posicao < 1 or posicao > len(maoAtual):
                posi = input("ESTA CARTA NÃO EXISTE!!  ")
                while posi.isnumeric() == False:
                    posi = input("DIGITE UM NÚMERO!!!!  ")
                posicao = int(posi)

    return posicao

#Imprime a jogada feita e o vencedor da rodada
def imprimeJogada(msg):
    if msg[message.MSG_SIZE] == 2:
        print("JOGADOR ", playerIdToChar(msg[message.MSG_DATA][0])," JOGOU A CARTA ", end="")
        naipe = game.decideNaipe(msg[message.MSG_DATA][1])
        num = numToCarta(msg[message.MSG_DATA][1])
        if naipe == 1:
            print("♠ ", end="")
        elif naipe == 2:
            print("♦ ", end="")
        elif naipe == 3:
            print("♣ ", end="")
        else:
            print("♥ ", end="")
        print(num)
    else: 
        print("JOGADOR ", playerIdToChar(msg[message.MSG_DATA][0])," VENCEU A RODADA!!!")

#Pega o caracter com base no numero do ID
def playerIdToChar(Id):
    if Id == 0:
        ret = "A"
    elif Id == 1:
        ret = "B"
    elif Id == 2:
        ret = "C"
    else:
        ret = "D"

    return ret

#Imprime vários ganhadores se for o caso
def IdToCharArray(IdA, tam):
    ret = str("")
    for i in range(0, tam-1):
        ret += playerIdToChar(IdA[i])
        ret += ","
    ret += playerIdToChar(IdA[tam-1])
    return ret

#Imprime quem venceu o jogo, incluindo se o jogo empatou
def printFim(msg):
    if msg[message.MSG_SIZE] == 1:
        print("JOGADOR", playerIdToChar(msg[message.MSG_DATA][0]), "VENCEU O JOGO COM A MENOR QUANTIDADE DE PONTOS!!!!")
    else:
        print("EMPATE!! JOGADORES",IdToCharArray(msg[message.MSG_DATA], msg[message.MSG_SIZE]), "VENCERAM O JOGO COM A MENOR E MESMA QUANTIDADE DE PONTOS!!!!")
