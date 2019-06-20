from __future__ import print_function
import os
import neat
from random import randint
from numpy import *
from ple import PLE
from ple.games import *
from pygame import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from Score_Test import *

Cenario = 1
Canos = 50000
#INIT_GAP = list(map(lambda x:192 if(x>192) else x,list(map(lambda x:25 if(x<25) else x,list(map(lambda x:abs(x),list(random.normal(108.5,82,(1,Canos))[0])))))))
#INIT_GAP = [25 if(i%2==0) else 25 for i in range(Canos)]
INIT_GAP = [randint(0,170) for i in range(Canos)]
GAME = FlappyBird(True,INIT_GAP,Canos)
ENV = PLE(GAME)
#GAP = [[25 if(i%2==0) else (25+j*80) for i in range(Canos)] for j in range(Cenario)]
GAP = [[randint(0,160)for i in range(Canos)]for j in range(Cenario)]
#GAP = [list(map(lambda x:192 if(x>192) else x,list(map(lambda x:25 if(x<25) else x,list(map(lambda x:abs(x),
                                  #list(random.normal(108.5,82,(1,int(Canos)))[0])))))))for i in range(Cenario)]# Cálculo baseado nos atributos da classe flappy

   
local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, 'config-feedforward_flappy')
L = []
p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-111')
    
for v in p.population:
    L.append(p.population[v])
    
    
maior = L[0]
maior = L[0]
for i in L:
    if(i.fitness != None):
        if(i.fitness>maior.fitness): maior = i

config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,neat.DefaultSpeciesSet, neat.DefaultStagnation,config_path)
maior = neat.nn.FeedForwardNetwork.create(maior, config)

Score = 0

app =  QApplication([])
window =  QMainWindow()
lcd = Ui_MainWindow()
lcd.setupUi(window)

while(True):
    State1 = ENV.game.getGameState()
                        
                    
    INP1 = State1["player_y"]
    INP2 = State1["next_pipe_bottom_y"]
    INP3= (-State1["next_pipe_top_y"]+State1["next_pipe_bottom_y"])/2 
    OUTPUT = maior.activate((INP1,INP2,INP3))
                        
    VAL = 119 if OUTPUT[0]>=0.4 else None
    RESP = ENV.act(VAL)
    ENV.display_screen = True
    ENV.force_fps = False
                     
    if(RESP>0):
        Score += 1
        lcd.Adicionar_Score(Score)

        
         
   

