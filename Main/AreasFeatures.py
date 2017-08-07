'''
Created on Jun 29, 2014

@author: Thomas
'''
import pyglet
import time

class Area(object):
    def __init__(self, name, description, **kwargs):
        self.name = name
        self.description = description
        self.size = 3
        self.visited = False
        self.state = 0
        self.connectedAreas = {}
        self.features = {}
        self.itemsContained = {}
        self.enemies = {}
        self.NPCs = {}

        #populate optional stats
        if kwargs is not None:
            for key, value in kwargs.iteritems():
                setattr(self, key, value)
        
    def lookAt(self):
        desc = self.name
        desc += "\n" + self.description[self.state] + "\n"
        if self.itemsContained:
            for item in self.itemsContained.itervalues():    #Display all the visible items
                if item.accessible:
                    if item.firstSeen and item.initSeenDesc:
                        desc += "\n" + item.initSeenDesc
                    elif item.firstTaken and item.notTakenDesc:
                        desc += "\n" + item.notTakenDesc
                    else:
                        desc += "\n" + item.seenDescription
                    
                    if item.quantity > 1:
                        desc += " (" + str(item.quantity) + ")"
                    item.firstSeen = False

        if self.NPCs or self.enemies:
            desc += "\n"
        if self.NPCs:
            for NPC in self.NPCs.itervalues():                  #Display all the NPCs
                desc += NPC.seenDescription
        if self.enemies:
            for enemy in self.enemies.itervalues():         #Display all the enemies
                if enemy.firstSeen:
                    enemy.firstSeen = False
                    desc += enemy.firstSeenDesc
                    if enemy.firstSeenSound:
                        source = pyglet.media.load(enemy.firstSeenSound, streaming=False)
                        source.play()
                elif enemy.stunnedTimer != 0:
                    desc += enemy.stunDesc
                    desc += " " + enemy.getDistance()
                else:
                    desc += enemy.seenDescription
                    desc += " " + enemy.getDistance()
                desc += "\n"
        return desc
        
    def connect(self, area, link):
        link.setDestination(area)
        self.connectedAreas[link.keywords] = link
            
    def disconnect(self, link):
        del self.connectedAreas[link.keywords]
        link.destination = None
    
    def addItem(self, itemToAdd):
        if itemToAdd.keywords in self.itemsContained:
            if itemToAdd.stackable:
                self.itemsContained[itemToAdd.keywords].quantity += itemToAdd.quantity
            else:
                self.itemsContained[itemToAdd.keywords].quantity += 1
        else:
            self.itemsContained[itemToAdd.keywords] = itemToAdd
            itemToAdd.currentLocation = self
        
    def removeItem(self, itemToRemove):
        if (self.itemsContained[itemToRemove.keywords].quantity > 1) and (not itemToRemove.stackable):
            self.itemsContained[itemToRemove.keywords].quantity -= 1
        else:
            del self.itemsContained[itemToRemove.keywords]
 
    def addFeature(self, featureToAdd):
        self.features[featureToAdd.keywords] = featureToAdd
        featureToAdd.currentLocation = self
        
    def removeFeature(self, featureToRemove):
        del self.features[featureToRemove.keywords]
        
    def spawnEnemy(self, enemyToSpawn, distanceToPlayer):
        self.enemies[enemyToSpawn.keywords] = enemyToSpawn
        enemyToSpawn.setLocation(self)
        #Make sure the enemy spawns within the confines of the area
        if distanceToPlayer < 1:
            distanceToPlayer = 1
        elif distanceToPlayer > self.size:
            distanceToPlayer = self.size
        enemyToSpawn.setDistance(distanceToPlayer)
        
    def killEnemy(self, enemyToKill):
        del self.enemies[enemyToKill.keywords]
        
    def addEnemy(self, enemyToAdd):
        self.enemies[enemyToAdd.keywords] = enemyToAdd
        enemyToAdd.setLocation(self)
        
    def removeEnemy(self, enemyToRemove):
        del self.enemies[enemyToRemove.keywords]
        
    def addNPC(self, NPCToAdd):
        self.NPCs[NPCToAdd.keywords] = NPCToAdd
        NPCToAdd.addToLocation(self)
        
    def removeNPC(self, NPCToRemove):
        del self.NPCs[NPCToRemove.keywords]
        NPCToRemove.removeFromLocation()
         
    def setIdNum(self, number):
        self.idNum = number

    def nextState(self):
        self.state += 1

class Feature(object):
    def __init__(self, description, keywords, **kwargs):
        self.description = description
        self.keywords = keywords
        self.state = 0
        self.currentLocation = None

        #populate optional stats
        if kwargs is not None:
            for key, value in kwargs.iteritems():
                setattr(self, key, value)
        
    def lookAt(self):
        return self.description[self.state]
    
    def get(self, holder, player):
        return "Assuming you could get it into your pack, what would be the point?"
    
    def setIdNum(self, number):
        self.idNum = number
        
    def setState(self, number):
        self.state = number
        
    def nextState(self):
        self.state += 1
    
class Hazard(Feature):
    def __init__(self, description, keywords, triggerDesc, **kwargs):
        self.triggerDesc = triggerDesc
        self.readied = True

        super(Hazard, self).__init__(description, keywords, **kwargs)

    def triggerHazard(self):
        pass

class Container(Feature):
    def __init__(self, description, keywords, isOpen, isAccessible, blockedDesc, openDesc, closeDesc, **kwargs):
        self.itemsContained = {}
        self.isOpen = isOpen
        self.isAccessible = isAccessible
        self.blockedDesc = blockedDesc
        self.openDesc = openDesc
        self.closeDesc = closeDesc
        super(Container, self).__init__(description, keywords, **kwargs)
        
    def addItem(self, itemToAdd):
        if itemToAdd.keywords in self.itemsContained:
            if itemToAdd.stackable:
                self.itemsContained[itemToAdd.keywords].quantity += itemToAdd.quantity
            else:
                self.itemsContained[itemToAdd.keywords].quantity += 1
        else:
            self.itemsContained[itemToAdd.keywords] = itemToAdd
            itemToAdd.currentLocation = self
        
    def removeItem(self, itemToRemove):
        if (self.itemsContained[itemToRemove.keywords].quantity > 1) and (not itemToRemove.stackable):
            self.itemsContained[itemToRemove.keywords].quantity -= 1
        else:
            del self.itemsContained[itemToRemove.keywords]

    def displayContents(self):
        desc = ""
        for item in self.itemsContained.itervalues():    #Display all the visible items
            if item.firstSeen and item.initSeenDesc:
                desc += "\n" + item.initSeenDesc
            elif item.firstTaken and item.notTakenDesc:
                desc += "\n" + item.notTakenDesc
            else:
                desc += "\n" + item.seenDescription

            if item.quantity > 1:
                desc += " (" + str(item.quantity) + ")"
            item.firstSeen = False
        return desc
        
    def lookAt(self):
        desc = self.description[self.state]
        if self.isOpen:
            desc += " It is open."
            if self.itemsContained:
                desc += self.displayContents()
        else:
            desc += " It is closed."

        return desc
    
    def tryUnlock(self, usedItem, player):
        return "It does not have a lock."
    
    def open(self, player):
        if not self.isAccessible:
            return self.blockedDesc

        for key, enemy in player.currentLocation.enemies.iteritems():
            if self in enemy.protectedThings:
                return enemy.protectedThings[self]
            elif self.currentLocation in enemy.protectedThings:
                return enemy.protectedThings[self.currentLocation]

        if self.isOpen:
            return "It is already open."
        else:
            self.isOpen = True
            desc = self.openDesc + "\n"
            if self.itemsContained:
                desc += self.displayContents()
            else:
                desc += "It appears to be empty."
        return desc,True

    def close(self, player):
        if not self.isOpen:
            return "It is already closed."
        for key, enemy in self.currentLocation.enemies.iteritems():
            if self in enemy.protectedThings:
                return enemy.protectedThings[self]
        else:
            self.isOpen = False
            return self.closeDesc,True
            
class Link(object):
    def __init__(self, description, keywords, isAccessible, **kwargs):
        self.description = description
        self.keywords = keywords
        self.isAccessible = isAccessible

        self.travelDesc = "You move on."
        self.destination = None
        self.siblingLink = None

        #populate optional stats
        if kwargs is not None:
            for key, value in kwargs.iteritems():
                setattr(self, key, value)
        
    def lookAt(self):
        return self.description
        
    def travel(self, player):
        for key, enemy in player.currentLocation.enemies.iteritems():
            if self in enemy.protectedThings:
                return enemy.protectedThings[self]

        if self.isAccessible == False:
            return self.blockedDesc
        
        if player.isRestricted:
            return player.restrictedDesc
        
        #Track chasing enemies and save their chase descriptions for later
        chaseDesc = ""
        for key, enemy in player.currentLocation.enemies.iteritems():
            if enemy.willChase:
                chaseDesc += "\n" + enemy.chaseDesc

        desc = self.travelDesc + "\n\n"
        player.currentLocation = self.destination
        if self.travelSound:
            source = pyglet.media.load(self.travelSound, streaming=False)
            source.play()
            time.sleep(1.8)
        if player.currentLocation.visited == False:
            player.currentLocation.visited = True
        desc += player.currentLocation.lookAt()
        desc += chaseDesc

        return desc,True
        
    def enemyTravel(self, enemy):
        if self.isAccessible == False:
            return False
        enemy.currentLocation.removeEnemy(enemy)
        self.destination.addEnemy(enemy)
        return True


    def makeSibling(self, sibling):
        self.siblingLink = sibling
        sibling.siblingLink = self
        
    def setDestination(self, area):
        self.destination = area
        
    def setIdNum(self, number):
        self.idNum = number
    
class Door(Link):
    def __init__(self, description, keywords, isAccessible, **kwargs):
 
        if not ("travelSound" in kwargs):
            kwargs.update({
                "travelSound":"Sounds/Misc/GenericDoor1.mp3"
            })
        if not ("travelDesc" in kwargs):
            kwargs.update({
                "travelDesc":"You open the door and step through."
            })

        super(Door, self).__init__(description, keywords, isAccessible, **kwargs)
        
    def lookAt(self):
        desc = self.description
        desc += " It seems to be "
        if self.isAccessible:
            desc += "unlocked."
        else:
            desc += "locked."
        return desc
        
    def tryUnlock(self, usedItem, player):
        return "That door does not have a lock."
    
    def open(self, player):
        return self.travel(player)
    
    def close(self, player):
        return "The door is already closed."

    def get(self, holder, player):
        return "After several minutes of struggling, you come to the realization that this door is unlikely to fit in your pack. You win this time, door."

    def playerAdvances(self):
        return "You bravely advance towards the threatening door with your weapon at the ready, daring it to make a move. The door does not seem to respond. "

    def playerRetreats(self):
        return "You slowly and cautiously back away from the door. Who knows what it's capable of?"

    def exorciseAttempt(self, player):
        return "You call upon all the powers of your god to free the door from the clutches of the demon that is undoubtedly possessing it, but nothing happens. The fiend must be truly powerful."

class Path(Link):
    def __init__(self, description, keywords, isAccessible, **kwargs):
 
        if not ("travelSound" in kwargs):
            kwargs.update({
                "travelSound":"Sounds/Misc/FootstepsHall.mp3"
            })

        super(Path, self).__init__(description, keywords, isAccessible, **kwargs)
        