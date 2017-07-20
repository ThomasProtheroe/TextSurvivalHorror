'''
Created on Aug 22, 2014

@author: Thomas
'''
import random
import pyglet

class Item(object):
    
    def __init__(self, name, description, seenDescription, quantity, keywords, initSeenDesc="", notTakenDesc="", initPickupDesc=""):
        self.name = name
        self.description = description
        self.seenDescription = seenDescription
        self.initPickupDesc = None
        self.quantity = quantity
        self.keywords = keywords
        self.accessible = True
        self.inAccessibleDesc = None
        self.firstSeen = True
        self.firstTaken = True
        self.pickupDesc = "You pick up the " + self.name + "."
            
        if initPickupDesc:
            self.initPickupDesc = initPickupDesc
        else:
            self.initPickupDesc = None
            
        if initSeenDesc:
            self.initSeenDesc = initSeenDesc
        else:
            self.initSeenDesc = None
        if notTakenDesc:
            self.notTakenDesc = notTakenDesc
        else:
            self.notTakenDesc = None
        self.inaccessibleDesc = None
        
    def get(self, holder, player):
        if not self.accessible:
            return self.inaccessibleDesc,True
        
        player.addItem(self)
        holder.removeItem(self)
        
        if self.firstTaken:
            if self.initPickupDesc:
                resultString = self.initPickupDesc
            else:
                resultString = self.pickupDesc
        else:
            resultString = self.pickupDesc
    
        self.firstSeen = False
        self.firstTaken = False

        if (player.mainHand == None) and (isinstance(self, Weapon)):
            self.equip(player)
        return resultString, True
    
    def drop(self, player):
        player.removeItem(self)
        player.currentLocation.addItem(self)
        return "You drop the " + self.name,True
    
    def destroy(self, holder):
        holder.removeItem(self)
        
    def makeAccessible(self):
        self.accessible = True
        
    def makeInAccessible(self, desc):
        self.accessible = False
        self.inaccessibleDesc = desc
        
    def setPickupDesc(self, desc):
        self.pickupDesc = desc
        
    def setInitPickupDesc(self,desc):
        self.initPickupDesc = desc
    
    def setIdNum(self, number):
        self.idNum = number
    
    def lookAt(self):
        return self.description

class Armor(Item):
    
    def __init__(self, name, description, seenDescription, quantity, keywords, armorRating, initSeenDesc="", notTakenDesc="", initPickupDesc=""):
        self.armorRating = armorRating
        super(Armor, self).__init__(name, description, seenDescription, quantity, keywords, initSeenDesc, notTakenDesc, initPickupDesc)
        
    def equip(self, player):
        if player.armor == self:
            return "You are already wearing that."
        
        player.armor = self
        return "You equip the " + self.name + ".",True
    
class Weapon(Item):
    
    def __init__(self, name, description, seenDescription, quantity, keywords, minDamage, maxDamage, size, critChance, initSeenDesc="", notTakenDesc="", initPickupDesc="", attackDesc=""):
        self.minDamage = minDamage
        self.maxDamage = maxDamage
        self.critChance = critChance
        self.size = size
        if not attackDesc:
            self.attackDesc = "You attack."
        else:
            self.attackDesc = attackDesc
        super(Weapon, self).__init__(name, description, seenDescription, quantity, keywords, initSeenDesc, notTakenDesc, initPickupDesc)
        
    def equip(self, player):
        if player.mainHand == self:
            return "That is already equipped."
        if self.size == 1:
            if player.mainHand == player.offHand:
                player.offHand = None
            player.mainHand = self
            return "You equip the " + self.name,True
        elif self.size == 2:
            player.mainHand = self
            player.offHand = self
            return "You equip the " + self.name,True

    def attack(self):
        pass
        
class RangedWeapon(Weapon):
    
    def __init__(self, name, description, seenDescription, quantity, keywords, minDamage, maxDamage, size, accuracy, capacity, ammoRemaining, fireSound, critChance=10, initSeenDesc="", notTakenDesc="", initPickupDesc="", attackDesc=""):
        self.accuracy = accuracy
        self.capacity = capacity
        self.ammoRemaining = ammoRemaining
        self.fireSound = fireSound
        self.rangeMod = [0,5,10]
        self.emptySound = "Sounds/Combat/EmptyGun.mp3"
        if not attackDesc:
            self.attackDesc = "You open fire!"
        else:
            self.attackDesc = attackDesc
        super(RangedWeapon, self).__init__(name, description, seenDescription, quantity, keywords, minDamage, maxDamage, size, critChance, initSeenDesc, notTakenDesc, initPickupDesc, attackDesc)
                            #Me name es Wayne Purkle coz when I nommin' grapes day be PURKLE!!!
    def attack(self, enemy, player, attackType):
        try:
            if attackType == "heavy":
                return "You are not holding a melee weapon."
            
            if self.ammoRemaining <= 0:
                source = pyglet.media.load(self.emptySound, streaming=False)
                source.play()
                return "You are out of ammo!"
            
            source = pyglet.media.load(self.fireSound, streaming=False)
            source.play()
            
            self.ammoRemaining -= 1
            hitChance = self.accuracy
            hitChance -= enemy.dodgeChance
            
            if enemy.distanceToPlayer == 1:
                hitChance -= self.rangeMod[0]
            elif enemy.distanceToPlayer == 2:
                hitChance -= self.rangeMod[1]
            elif enemy.distanceToPlayer == 3:
                hitChance -= self.rangeMod[2]
                
            if player.intoxication > 75:
                hitChance -= 25
            elif player.intoxication > 60:
                hitChance -= 15
            elif player.intoxication > 40:
                hitChance -= 10
            elif player.intoxication > 25:
                hitChance -= 5
            elif player.intoxication > 10:
                hitChance += 8
            elif player.intoxication > 1:
                hitChance += 5
            elif player.intoxication > 60:
                hitChance -= 5
                
            if enemy.stunnedTimer > 0:
                hitChance += 10
                
            if hitChance < 5:
                hitChance = 5
                
            attackRoll = random.randint(0, 100)
            if attackRoll <= hitChance:
                resultString = "\n" + enemy.takeHit(self, "ranged")
            else:
                resultString = self.attackDesc
                resultString += "\nYou miss!"
            return resultString, True
        except AttributeError:
            return "That isn't worth wasting ammo on..."

    def shoot(self, enemy, player):
        return self.attack(enemy, player)
    
    def reload(self, player):
        for item in player.inventory.itervalues():
            try:
                weaponType = item.weaponType
            except AttributeError:
                continue
            
            if self.name == weaponType:
                self.ammoRemaining = self.capacity
                item.destroy(player)
                return "You reload the " + self.name + ".",True
            
        return "You don't have any ammo."
        
    def lookAt(self):
        resultString = self.description + "\n"
        resultString += "It has " + str(self.ammoRemaining) + " shots remaining."
        return resultString
        
class MeleeWeapon(Weapon):

    def __init__(self, name, description, seenDescription, quantity, keywords, minDamage, maxDamage, size, accuracy, critChance=10, stunLength=2, initSeenDesc="", notTakenDesc="", initPickupDesc="", attackDesc=""):
        self.accuracy = accuracy
        self.stunLength = stunLength
        self.missSound = "Sounds/Combat/MeleeMiss.mp3"
        if not attackDesc:
            self.attackDesc = "You swing your weapon!"
        else:
            self.attackDesc = attackDesc
        super(MeleeWeapon, self).__init__(name, description, seenDescription, quantity, keywords, minDamage, maxDamage, size, critChance, initSeenDesc, notTakenDesc, initPickupDesc)   

    def attack(self, enemy, player, attackType):
        try:
            if enemy.distanceToPlayer > 1:
                return "You are not within striking distance."

            hitChance = self.accuracy
            hitChance -= enemy.dodgeChance
            
            if player.intoxication > 75:
                hitChance -= 25
            elif player.intoxication > 60:
                hitChance -= 15
            elif player.intoxication > 40:
                hitChance -= 10
            elif player.intoxication > 25:
                hitChance -= 5
            elif player.intoxication > 10:
                hitChance += 8
            elif player.intoxication > 1:
                hitChance += 5
                
            if attackType == "heavy":
                hitChance -= 10
            
            if enemy.stunnedTimer > 0:
                hitChance += 50
            
            if hitChance < 5:
                hitChance = 5
            attackRoll = random.randint(0, 100)
            if attackRoll <= hitChance:
                resultString = "\n" + enemy.takeHit(self, attackType)
            else:
                resultString = self.attackDesc
                resultString += "\nYou miss!"
                source = pyglet.media.load(self.missSound, streaming=False)
                source.play()
            return resultString, True
        except AttributeError:
            return "That isn't an enemy..."

class Ammo(Item):
    
    def __init__(self, name, description, seenDescription, quantity, keywords, weaponType, initSeenDesc="", notTakenDesc="", initPickupDesc=""):
        self.weaponType = weaponType
        super(Ammo, self).__init__(name, description, seenDescription, quantity, keywords, initSeenDesc, notTakenDesc, initPickupDesc)
    
class Usable(Item):
    
    def __init__(self, name, description, seenDescription, quantity, keywords, useDescription, initSeenDesc="", notTakenDesc="", initPickupDesc=""):
        self.useDescription = useDescription
        super(Usable, self).__init__(name, description, seenDescription, quantity, keywords, initSeenDesc, notTakenDesc, initPickupDesc)
        
class Drinkable(Usable):
    
    def __init__(self, name, description, seenDescription, quantity, keywords, useDescription, initSeenDesc="", notTakenDesc="", initPickupDesc=""):
        super(Drinkable, self).__init__(name, description, seenDescription, quantity, keywords, useDescription, initSeenDesc, notTakenDesc, initPickupDesc)
        
class Readable(Item):
    
    def __init__(self, name, description, seenDescription, quantity, keywords, initSeenDesc="", notTakenDesc="", initPickupDesc=""):
        super(Readable, self).__init__(name, description, seenDescription, quantity, keywords, initSeenDesc, notTakenDesc, initPickupDesc)
            
    def read(self):
        pass

class Corpse(Item):
    def __init__(self, name, description, seenDescription, quantity, keywords, initSeenDesc="", notTakenDesc="", initPickupDesc=""):
        super(Corpse, self).__init__(name, description, seenDescription, quantity, keywords, initSeenDesc, notTakenDesc, initPickupDesc)
    
    def get(self, holder, player):
        return "I've no desire to carry around a corpse."