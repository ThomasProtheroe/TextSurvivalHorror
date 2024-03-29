'''
Created on Sep 5, 2014

@author: Thomas
'''
import sys
import Builder
import Player
import jsonpickle

global SAVEGAME_FILENAME
SAVEGAME_FILENAME = 'save.json'

class GameState(object):
    
    def __init__(self):
        self.builder = Builder.Builder()
        self.player = None
        self.areaList = list()
        self.turnCount = 0
        self.introText = ""
        self.backgroundMusic = None
        self.returnOnEnter = False

        self.builder.loadState(self)
        
    def addArea(self, area):
        self.areaList.append(area)
        
    def removeArea(self, area):
        self.areaList.remove(area)
        
    def addPlayer(self, player):
        self.player = player
    
    def spawnPlayer(self, player):
        self.player.currentLocation = self.areaList[0]

    def loadZone(self, startingArea):
        self.areaList = list()
        self.addArea(startingArea)
        self.spawnPlayer(self.player)

def newGameState():
    state = GameState()
    player = Player.Player()
    state.addPlayer(player)
    state.addArea(state.builder.buildPrologue100())
    state.spawnPlayer(player)
    state.returnOnEnter = False
    return state

def newSimulationState():
    state = GameState()
    player = Player.Player()
    state.addPlayer(player)
    state.addArea(state.builder.buildCombatSimulator())
    state.spawnPlayer(player)
    state.returnOnEnter = False
    return state

def save(state):
    with open(SAVEGAME_FILENAME, 'w') as savegame:
        savegame.write(jsonpickle.encode(state))
    return "Game saved."
    
def loadState():
    with open(SAVEGAME_FILENAME, 'r') as savegame:
        state = jsonpickle.decode(savegame.read())
        state.introText = "Game Loaded"
        return state
    
def quit():
    sys.exit()