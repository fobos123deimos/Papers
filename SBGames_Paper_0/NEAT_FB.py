from __future__ import print_function
import matplotlib.pyplot as plt
import os
import neat
import visualize
from numpy import *
from ple import PLE
from ple.games import *


VET_MED1 =[]
VET_BEST1 = []
VET_MED2 =[]
VET_BEST2 = []

Cenario = 3
Canos = 3

Score = 0.0
Pont = 0.0
Fator_y = 0.0

Peso_Pont = 1.0
Peso_Score = 1.0
Peso_FY = 0.08

Peso_Cen1 = 1.0
Peso_Cen2 = 2.0
Peso_Cen3 = 6.0


#INIT_GAP = list(map(lambda x:192 if(x>192) else x,list(map(lambda x:25 if(x<25) else x,list(map(lambda x:abs(x),list(random.normal(108.5,82,(1,Canos))[0])))))))
INIT_GAP = [25 if(i%2==0) else 25 for i in range(Canos)]
GAME = FlappyBird(True,INIT_GAP,Canos)
ENV = PLE(GAME)
#GAP = [list(map(lambda x:192 if(x>192) else x,list(map(lambda x:25 if(x<25) else x,list(map(lambda x:abs(x),
                                  #list(random.normal(108.5,82,(1,int(Canos)))[0])))))))for i in range(Cenario)]# Cálculo baseado nos atributos da classe flappy
GAP = [[25 if(i%2==0) else 25 + 80*j for i in range(Canos)] for j in range(Cenario)]

print(GAME.height)

def eval_genomes(genomes, config):
    
    VT_NET = []
    SCORE1 = []
    SCORE2 = []
    
    for genome_id,genome in genomes:#Decoifica os Genomas em Redes
        VT_NET.append(neat.nn.FeedForwardNetwork.create(genome, config))
        
    for net,pair in zip(VT_NET,genomes): 
        score = []
        pont = []
        ENV.init()
        
        for i in range(Cenario):
            Score = 0.0
            Pont = 0.0
            Fator_y = 0.0
      
            while(True):
                #Armazene o Estado pré-Rede;Repasse para a Rede; Obtenha sua Resposta
             
                State1 = ENV.game.getGameState()
                INP1 = State1["player_y"]
                INP2 = State1["next_pipe_bottom_y"]
                INP3= (-State1["next_pipe_top_y"]+State1["next_pipe_bottom_y"])/2
                #INP4 = State1["next_pipe_dist_to_player"]
               
                OUTPUT = net.activate((INP1,INP2,INP3))
            	
                
                VAL = 119 if OUTPUT[0]>=0.4 else None
                
                #VAL = 119 if (OUTPUT.index(max(OUTPUT))==0) else None
                RESP = ENV.act(VAL)
                ENV.display_screen = True
                ENV.force_fps = True
                #Trate a Resposta do Ambiente 
                if(RESP>0):
                    Score += 1
                    if(Score==Canos):
                        if(i<Cenario):
                            ENV.reset_game(GAP[i],Canos)
                            break
                        
                        break

                Pont += 1.0
                if(ENV.game_over()):#Se for game_over() o estado pós-Rede é filtrado
                
                    State2 = ENV.game.getGameState()
                    if(i<Cenario):
                    
                        Fator_y = abs(State2["player_y"] - (State2["next_pipe_top_y"]+(State2["next_pipe_top_y"]-State2["next_pipe_bottom_y"])/2))
                        ENV.reset_game(GAP[i],Canos)
                        break
                    
                    break
                    
            
            pont.append(Peso_Pont*(Pont/195) + Peso_Score*(Score/3) - Peso_FY*(Fator_y/GAME.height))
            #pont.append((Pont/195) + (Score/3) - (Fator_y/GAME.height))
            #pont.append((Pont/10) + (10*Score) - (Fator_y/100))4
            score.append(Score)
            #print("Score:{} // Score/3:{}".format(Score,Score/3))
            #print("Pont:{} // Pont/195:{}".format(Pont,Pont/195))
            #print("Fator_Y:{} // Fator_Y/GAME.height:{} // GAME.height:{}".format(Fator_y,Fator_y/GAME.height,GAME.height)) 
           
    
        
        #SCORE1.append(round(sum(pont)/len(pont),4))
        SCORE1.append(round((pont[0]*Peso_Cen1+pont[1]*Peso_Cen2+pont[2]*Peso_Cen3)/(Peso_Cen1+Peso_Cen2+Peso_Cen3),4))
        SCORE2.append(round(sum(score)/len(score),4))
        
        
        pair[1].fitness = round((pont[0]*Peso_Cen1+pont[1]*Peso_Cen2+pont[2]*Peso_Cen3)/(Peso_Cen1+Peso_Cen2+Peso_Cen3),4)
        #pair[1].fitness = round(sum(pont)/len(pont),4)
        
    
    VET_MED1.append(round(sum(SCORE1)/len(SCORE1),4))# Adiciono a média dos scores da população a um vetor de médias para plotagem
    VET_BEST1.append(max(SCORE1))#Busco o que obteve o maior score e guardo pra plotagem

    VET_MED2.append(round(sum(SCORE2)/len(SCORE2),4))
    VET_BEST2.append(max(SCORE2))
    
    print(max(SCORE1))
    print(round(sum(SCORE1)/len(SCORE1),4))

    print(max(SCORE2))
    print(round(sum(SCORE2)/len(SCORE2),4))

        
    
def run(config_file):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    p = neat.Population(config)
    #p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-996')
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1))

    
    winner = p.run(eval_genomes,100) #Retorna o melhor depois de 150 gerações

    print('\nBest genome:\n{!s}'.format(winner))

   
    node_names = {-3:'Y_P',-2:'Y_B',-1:'Y_C',0:'Prob'}
    visualize.draw_net(config, winner, True, node_names=node_names)
    #visualize.plot_stats(stats, ylog=False, view=True)
    visualize.plot_species(stats, view=True)

    #Plotagem do Grafico do Médio e do Melhor Fitness
    plt.plot(list(range(1,len(VET_MED1)+1)),VET_MED1,linewidth=2,color = 'blue',label='Average Fitness')
    plt.plot(list(range(1,len(VET_BEST1)+1)),VET_BEST1,linewidth=2,color = 'red',label='Best Fitness')
    plt.title("Fitness",fontsize=24)
    plt.xlabel("Generations",fontsize=14)
    plt.ylabel("A_P&B_P/Generation",fontsize=14)
    plt.tick_params(axis='both',which = 'major',labelsize=5)
    plt.axis([1,(len(VET_MED1)+1),0,1.9],fontsize=25)
    plt.grid()
    legend = plt.legend(loc='upper right')
    plt.savefig('Fitness.png')
    plt.show()

    #Plotagem do Grafico do Médio e do Melhor Score
    plt.plot(list(range(1,len(VET_MED2)+1)),VET_MED2,linewidth=2,color = 'blue',label='Average Score')
    plt.plot(list(range(1,len(VET_BEST2)+1)),VET_BEST2,linewidth=2,color = 'red',label='Best Score')
    plt.title("Score",fontsize=24)
    plt.xlabel("Generations",fontsize=14)
    plt.ylabel("A_S&B_S/Generation",fontsize=14)
    plt.tick_params(axis='both',which = 'major',labelsize=5)
    plt.axis([1,(len(VET_MED2)+1),0,3.1],fontsize=25)
    plt.grid()
    legend = plt.legend(loc='upper right')
    plt.savefig('Score.png')
    plt.show()

 


if __name__ == '__main__':
 
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward_flappy')
    run(config_path)


