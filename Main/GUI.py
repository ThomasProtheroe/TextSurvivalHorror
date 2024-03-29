import pyglet
import copy
import Enemies
import Parser
import StateControl
import time

class Rectangle(object):
    '''Draws a rectangle into a batch.'''
    def __init__(self, x1, y1, x2, y2, color, batch, group=None):
        self.batch = batch
        self.color = color
        self.group = group
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.vertex_list = batch.add(4, pyglet.gl.GL_QUADS, group,
            ('v2i', [x1, y1, x2, y1, x2, y2, x1, y2]),
            ('c4B', color * 4)
        )

    def deleteRect(self):
        self.vertex_list.delete()

    def redrawRect(self):
        self.vertex_list = self.batch.add(4, pyglet.gl.GL_QUADS, self.group,
            ('v2i', [self.x1, self.y1, self.x2, self.y1, self.x2, self.y2, self.x1, self.y2]),
            ('c4B', self.color * 4)
        )

    def changeRect(self, color):
        self.color = color
        self.vertex_list = self.batch.add(4, pyglet.gl.GL_QUADS, self.group,
            ('v2i', [self.x1, self.y1, self.x2, self.y1, self.x2, self.y2, self.x1, self.y2]),
            ('c4B', color * 4)
        )

class DisplayWindow(object):
    def __init__(self, text, x, y, width, batch, group=None):
        self.document = pyglet.text.document.UnformattedDocument(text)
        self.document.set_style(0, len(self.document.text),
            dict(color=(0, 0, 0, 255), bold=True)
        )
        font = self.document.get_font()
        height = (font.ascent - font.descent) * 31
        
        self.layout = pyglet.text.layout.IncrementalTextLayout(
            self.document, width, height, multiline=True, batch=batch, group=group)
        
        self.layout.x = x
        self.layout.y = y
        
        pad = 2
        self.rectangle = Rectangle(x - pad, y - pad,
                                   x + width + pad, y + height + pad, [64, 64, 64, 255], batch, group)

class TextWidget(object):
    def __init__(self, text, x, y, width, batch, group=None):
        self.document = pyglet.text.document.UnformattedDocument(text)
        self.document.set_style(0, len(self.document.text), 
            dict(color=(0, 0, 0, 255), bold=True)
        )
        font = self.document.get_font()
        height = (font.ascent - font.descent)
        
        self.layout = pyglet.text.layout.IncrementalTextLayout(
            self.document, width, height, multiline=False, batch=batch, group=group)
        self.caret = pyglet.text.caret.Caret(self.layout)

        self.layout.x = x
        self.layout.y = y

        # Rectangular outline
        pad = 2
        self.rectangle = Rectangle(x - pad, y - pad, 
                                   x + width + pad, y + height + pad, [200, 200, 220, 255], batch, group)

    def clearContents(self):
        self.document.delete_text(0, len(self.document.text))

    def hit_test(self, x, y):
        return (0 < x - self.layout.x < self.layout.width and
                0 < y - self.layout.y < self.layout.height)

class DamageFlash(object):
     def __init__(self, x, y, width, height, batch, group):
        self.rectangle = Rectangle(x, y, x + width, y + height, [255, 32, 32, 255], batch, group)

class FadeToBlack(object):
     def __init__(self, x, y, width, height, batch, group, labelGroup):
        self.rectangle = Rectangle(x, y, x + width, y + height, [0, 0, 0, 0], batch, group)
        self.alpha = 0
        self.label1 = pyglet.text.Label("Game Over", x=width/2, y=height/2 + height / 12, font_name='Times New Roman',font_size=32,
                                        batch=batch, group=labelGroup, color=(155,0,0,0), bold=True, anchor_x='center', anchor_y='center')
        self.label2 = pyglet.text.Label("Press Enter to Continue", x=width/2, y=height/2, font_name='Times New Roman',font_size=32,
                                        batch=batch, group=labelGroup, color=(155,0,0,0), bold=True, anchor_x='center', anchor_y='center')

class MenuButton(object):
    def __init__(self, buttonFunction, text, x, y, batch, spriteGroup, labelGroup):
        self.buttonFunction = buttonFunction

        self.label = pyglet.text.Label(text, x=x, y=y, font_name='Times New Roman',font_size=22,
                                        batch=batch, group=labelGroup, color=(125,125,125,255), bold=True)
        self.label.anchor_x = 'center'
        self.pressed = False
        self.hover = False
        
        #load and position the sprites
        self.defaultImage = pyglet.image.load("Sprites/buttonNormal.png");
        self.defaultImage.anchor_x = self.defaultImage.width // 2
        self.defaultImage.anchor_y = self.defaultImage.height // 2
        self.hoverImage = pyglet.image.load("Sprites/buttonHighLight.png");
        self.hoverImage.anchor_x = self.hoverImage.width // 2
        self.hoverImage.anchor_y = self.hoverImage.height // 2
        self.pressedImage = pyglet.image.load("Sprites/buttonPressed.png");
        self.pressedImage.anchor_x = self.pressedImage.width // 2
        self.pressedImage.anchor_y = self.pressedImage.height // 2

        self.defaultSprite = pyglet.sprite.Sprite(self.defaultImage, x, y + 10, batch=batch, group=spriteGroup)
        self.defaultSprite.scale = 0.6

    def hit_test(self, x, y):
        return (15 < x - (self.defaultSprite.x - (self.defaultSprite.width / 2)) < self.defaultSprite.width - 20 and
                10 < y - (self.defaultSprite.y - (self.defaultSprite.height / 2)) < self.defaultSprite.height -5)

    def delete(self):
        self.label.delete()

class GameButton(object):
    def __init__(self, buttonCommand, text, x, y, batch, spriteGroup, labelGroup):
        self.buttonCommand = buttonCommand

        self.label = pyglet.text.Label(text, x=x, y=y, font_name='Times New Roman',font_size=16,
                                        batch=batch, group=labelGroup, color=(125,125,125,255), bold=True)
        self.label.anchor_x = 'center'
        self.pressed = False
        self.hover = False
        
        #load and position the sprites
        self.defaultImage = pyglet.image.load("Sprites/buttonNormal.png");
        self.defaultImage.anchor_x = self.defaultImage.width // 2
        self.defaultImage.anchor_y = self.defaultImage.height // 2
        self.hoverImage = pyglet.image.load("Sprites/buttonHighLight.png");
        self.hoverImage.anchor_x = self.hoverImage.width // 2
        self.hoverImage.anchor_y = self.hoverImage.height // 2
        self.pressedImage = pyglet.image.load("Sprites/buttonPressed.png");
        self.pressedImage.anchor_x = self.pressedImage.width // 2
        self.pressedImage.anchor_y = self.pressedImage.height // 2

        self.defaultSprite = pyglet.sprite.Sprite(self.defaultImage, x, y + 10, batch=batch, group=spriteGroup)
        self.defaultSprite.scale = 0.4

    def hit_test(self, x, y):
        return (5 < x - (self.defaultSprite.x - (self.defaultSprite.width / 2)) < self.defaultSprite.width - 10 and
                5 < y - (self.defaultSprite.y - (self.defaultSprite.height / 2)) < self.defaultSprite.height - 3)

    def delete(self):
        self.label.delete()
        
class StatsPanel(object):
    def __init__(self, batch, spriteGroup, labelGroup):
        self.condition = 'Unhurt'
        self.spirit = 'Saint Like'
        self.intoxication = 'Sober'
        width = 190
        height = 230
        x = 1024 - width - 35
        y = 680 - height
        pad = 2
        self.border = Rectangle(x - pad, y - pad,
                                   x + width + pad, y + height + pad, [204, 0, 0, 255], batch, spriteGroup)
        self.filler = Rectangle(x - pad + 5, y - pad + 5,
                                   x + width + pad -5, y + height + pad - 5, [0, 0, 0, 255], batch, spriteGroup)
        
        conditionOk_seq = pyglet.image.ImageGrid(pyglet.image.load("Sprites/ekgOK.png"), 1, 19)
        conditionOk_anim = pyglet.image.Animation.from_image_sequence(conditionOk_seq, 0.08, True)
        self.conditionOk_sprite = pyglet.sprite.Sprite(conditionOk_anim, x=x+40, y=y+120, batch=batch, group=labelGroup)
        self.conditionOk_sprite.scale = 2.2

        conditionCaution_seq = pyglet.image.ImageGrid(pyglet.image.load("Sprites/ekgCAUTION.png"), 1, 19)
        conditionCaution_anim = pyglet.image.Animation.from_image_sequence(conditionCaution_seq, 0.065, True)
        self.conditionCaution_sprite = pyglet.sprite.Sprite(conditionCaution_anim, x=x+40, y=y+120)
        self.conditionCaution_sprite.scale = 2.2

        conditionCaution2_seq = pyglet.image.ImageGrid(pyglet.image.load("Sprites/ekgCAUTION2.png"), 1, 19)
        conditionCaution2_anim = pyglet.image.Animation.from_image_sequence(conditionCaution2_seq, 0.05, True)
        self.conditionCaution2_sprite = pyglet.sprite.Sprite(conditionCaution2_anim, x=x+40, y=y+120)
        self.conditionCaution2_sprite.scale = 2.2

        conditionDanger_seq = pyglet.image.ImageGrid(pyglet.image.load("Sprites/ekgDANGER.png"), 1, 19)
        conditionDanger_anim = pyglet.image.Animation.from_image_sequence(conditionDanger_seq, 0.035, True)
        self.conditionDanger_sprite = pyglet.sprite.Sprite(conditionDanger_anim, x=x+40, y=y+120)
        self.conditionDanger_sprite.scale = 2.2

        self.conditionSprite = self.conditionOk_sprite
        
        self.labels = [
            pyglet.text.Label('Condition', x=x+15, y=y+200, font_name='Times New Roman',font_size=16,
                                       batch=batch, group=labelGroup, color=(155,0,0,255), bold=True, multiline=True, width = width - 10),
            pyglet.text.Label('Spirit:\n' + self.spirit, x=x+15, y=y+95, font_name='Times New Roman',font_size=16,
                                        batch=batch, group=labelGroup, color=(155,0,0,255), bold=True, multiline=True, width = width - 10),
            pyglet.text.Label('Intoxication:\n' + self.intoxication, x=x+15, y=y+38, font_name='Times New Roman',font_size=16,
                                        batch=batch, group=labelGroup, color=(155,0,0,255), bold=True, multiline=True, width = width - 10)
        ]
        
    def updateStats(self, player, batch, group):
        condition = player.getCondition()
        spirit = player.getSpirit()
        intoxication = player.getIntoxication()

        self.conditionSprite.batch = None
        if player.health > 90:
            self.conditionSprite = self.conditionOk_sprite
        elif player.health > 60:
            self.conditionSprite = self.conditionCaution_sprite
        elif player.health > 30:
            self.conditionSprite = self.conditionCaution2_sprite
        else:
            self.conditionSprite = self.conditionDanger_sprite

        self.conditionSprite.batch = batch
        self.conditionSprite.group = group
        self.labels[1].text = 'Spirit:\n' + spirit
        self.labels[2].text = 'Intoxication:\n' + intoxication

class EquipPanel(object):
    def __init__(self, batch, spriteGroup, labelGroup):
        self.mainHand = "Empty"
        self.offHand = "Empty"
        self.armor = "None"        
        width = 190
        height = 200
        x = 1024 - width - 35
        y = 225
        pad = 2
        self.border = Rectangle(x - pad, y - pad, 
                                   x + width + pad, y + height + pad, [204, 0, 0, 255], batch, spriteGroup)
        self.filler = Rectangle(x - pad + 5, y - pad + 5,
                                   x + width + pad -5, y + height + pad - 5, [0, 0, 0, 255], batch, spriteGroup)
        
        self.labels = [
            pyglet.text.Label('Main Hand:\n' + self.mainHand, x=x+15, y=y+165, font_name='Times New Roman',font_size=16,
                                        batch=batch, group=labelGroup, color=(155,0,0,255), bold=True, multiline=True, width = width - 10),
            pyglet.text.Label('Off Hand:\n' + self.offHand, x=x+15, y=y+105, font_name='Times New Roman',font_size=16,
                                        batch=batch, group=labelGroup, color=(155,0,0,255), bold=True, multiline=True, width = width - 10),
            pyglet.text.Label('Armor:\n' + self.armor, x=x+15, y=y+40, font_name='Times New Roman',font_size=16,
                                        batch=batch, group=labelGroup, color=(155,0,0,255), bold=True, multiline=True, width = width - 10)
        ]

    def updateEquip(self, player):
        mainHand = player.getMainHand()
        offHand = player.getOffHand()
        armor = player.getArmor()
        
        if mainHand:
            mainHand = mainHand.name
        else:
            mainHand = "Empty"
        if offHand:
            offHand = offHand.name
        else:
            offHand = "Empty"
        if armor:
            armor = armor.name
        else:
            armor = "None"
        
        self.labels[0].text = 'Main Hand:\n' + mainHand
        self.labels[1].text = 'Off Hand:\n' + offHand
        self.labels[2].text = 'Armor:\n' + armor

class Window(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(1024, 768, caption='Text Game')

        self.inMenu = False
        self.writingText = False
        self.textToWrite = ""
        self.backgroundMusic = None
        self.soundPlayer = pyglet.media.Player()
        self.musicPlayer = pyglet.media.Player()
        
        self.startMainMenu()

    def startMainMenu(self):
        pyglet.gl.glBlendFunc( pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        self.inMenu = True
        self.batch = pyglet.graphics.Batch()
        self.group1 = pyglet.graphics.OrderedGroup(0)
        self.group2 = pyglet.graphics.OrderedGroup(1)
        self.group3 = pyglet.graphics.OrderedGroup(2)
        self.group4 = pyglet.graphics.OrderedGroup(3)
        self.group5 = pyglet.graphics.OrderedGroup(4)
        self.parser = Parser.Parser()
        self.state = None
        self.widgets = None
        self.focus = None
        self.buttonClick = pyglet.media.load('Sounds/UI/menuClick.mp3', streaming=False)
        self.buttonHover = pyglet.media.load('Sounds/UI/menuHover.wav', streaming=False)
        self.setBackgroundMusic('Music/Oblivion.mp3')

        self.title = pyglet.text.Label('Before I Wake', x=(self.width / 2), y=(self.height - 100), anchor_x='center', anchor_y='center',
                                        font_name='Times New Roman',font_size=32, batch=self.batch, color=(155,0,0,255), bold=True)
        
        self.menuButtons = [
            MenuButton(StateControl.newGameState, 'New Game', (self.width / 2), (self.height - 225), self.batch, self.group2, self.group3),
            MenuButton(StateControl.loadState, 'Load Game', (self.width / 2), (self.height - 350), self.batch, self.group2, self.group3),
            MenuButton(StateControl.newSimulationState, 'Training', (self.width / 2), (self.height - 475), self.batch, self.group2, self.group3),
            MenuButton(StateControl.quit, 'Quit', (self.width / 2), (self.height - 600), self.batch, self.group2, self.group3)
        ]

    def setBackgroundMusic(self, musicFile):
        if self.musicPlayer.playing:
            self.musicPlayer.pause()
        del self.musicPlayer
        self.musicPlayer = pyglet.media.Player()
        soundtrackSource = pyglet.media.load(musicFile)
        self.musicPlayer.queue(soundtrackSource)
        self.musicPlayer.eos_action = pyglet.media.Player.EOS_LOOP
        self.musicPlayer.play()

    def stopBackgroundMusic(self):
        self.musicPlayer.pause()

    def refreshBackgroundMusic(self):
        if self.state.backgroundMusic:
            self.setBackgroundMusic(self.state.backgroundMusic)
        else:
            self.stopBackgroundMusic()

    def startGameState(self, state):
        pyglet.clock.schedule_interval(self.updateText, 0.01)
        self.inMenu = False
        self.batch = pyglet.graphics.Batch()
        self.group1 = pyglet.graphics.OrderedGroup(0)
        self.group2 = pyglet.graphics.OrderedGroup(1)
        self.group3 = pyglet.graphics.OrderedGroup(2)
        self.group4 = pyglet.graphics.OrderedGroup(3)
        self.state = state
        self.parser.loadState(state)
        
        self.title = pyglet.text.Label('Before I Wake', x=(self.width / 2), y=(self.height - 40), anchor_x='center', anchor_y='center',
                                        font_name='Times New Roman',font_size=32, batch=self.batch, group=self.group2, color=(155,0,0,255), bold=True)

        self.disp = DisplayWindow(self.state.introText, 40, 91, self.width - 300, self.batch, self.group2)
        
        self.refreshBackgroundMusic()

        self.widgets = [
            TextWidget('', 40, 55, self.width - 300, self.batch, self.group2)
        ]

        self.gameButtons = [
            GameButton("Attack", 'Attack', 890, 175, self.batch, self.group2, self.group3),
            GameButton("Heavy Attack", 'Heavy Attack', 890, 115, self.batch, self.group2, self.group3),
            GameButton("Exorcise", 'Exorcise', 890, 55, self.batch, self.group2, self.group3)
        ]
        self.text_cursor = self.get_system_mouse_cursor('text')

        self.set_focus(self.widgets[0])
        
        self.statsDisplay = StatsPanel(self.batch, self.group2, self.group3)
        self.statsDisplay.updateStats(self.state.player, self.batch, self.group3)
        
        self.equipDisplay = EquipPanel(self.batch, self.group2, self.group3)
        self.equipDisplay.updateEquip(self.state.player)

        self.damageFlash = DamageFlash(0, 0, self.width, self.height, self.batch, self.group4)
        self.damageFlash.rectangle.deleteRect()

        self.fadeRect = FadeToBlack(0, 0, self.width, self.height, self.batch, self.group4, self.group5)
        self.fadeRect.rectangle.deleteRect()

    def loadZone(self):
        self.refreshBackgroundMusic()

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        if self.inMenu:
            for button in self.menuButtons:
                if button.hit_test(x, y):
                    button.defaultSprite.image = button.hoverImage
                    if not button.hover:
                        self.buttonHover.play()
                        button.hover = True
                else:
                    button.defaultSprite.image = button.defaultImage
                    button.pressed = False
                    button.hover = False
        else:
            for button in self.gameButtons:
                if button.hit_test(x, y):
                    button.defaultSprite.image = button.hoverImage
                    if not button.hover:
                        button.hover = True
                else:
                    button.defaultSprite.image = button.defaultImage
                    button.pressed = False
                    button.hover = False
            
        if self.widgets:
            for widget in self.widgets:
                if widget.hit_test(x, y):
                    self.set_mouse_cursor(self.text_cursor)
                    break
            else:
                self.set_mouse_cursor(None)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.inMenu:
            for button in self.menuButtons:
                if button.hit_test(x, y):
                    button.defaultSprite.image = button.pressedImage
                    button.pressed = True
        else:
            for button in self.gameButtons:
                if button.hit_test(x, y):
                    button.defaultSprite.image = button.pressedImage
                    button.pressed = True

        if self.widgets:
            for widget in self.widgets:
                if widget.hit_test(x, y):
                    self.set_focus(widget)
                    break
            else:
                self.set_focus(None)

        if self.focus:
            self.focus.caret.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        if self.inMenu:
            if self.menuButtons:    
                for button in self.menuButtons:
                    if button.hit_test(x, y) and button.pressed:
                        self.buttonClick.play()
                        state = button.buttonFunction()
                        self.startGameState(state)
        else:
            if self.gameButtons:    
                for button in self.gameButtons:
                    if button.hit_test(x, y) and button.pressed:
                        pyglet.media.load('Sounds/UI/menuHover.wav').play()
                        button.defaultSprite.image = button.hoverImage
                        self.widgets[0].document.text = button.buttonCommand
                        self.enterPressed()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.focus:
            self.focus.caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_text(self, text):
        if self.focus:
            self.focus.caret.on_text(text)

    def on_text_motion(self, motion):
        if self.focus:
            
            self.focus.caret.on_text_motion(motion)

    def on_text_motion_select(self, motion):
        if self.focus:
            self.focus.caret.on_text_motion_select(motion)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ENTER:
            self.enterPressed()
        elif self.widgets and (not self.focus == self.widgets[0]):
            self.set_focus(self.widgets[0])


    def set_focus(self, focus):
        if self.focus:
            self.focus.caret.visible = False
            self.focus.caret.mark = self.focus.caret.position = 0

        self.focus = focus
        if self.focus:
            self.focus.caret.visible = True
            self.focus.caret.mark = 0
            self.focus.caret.position = len(self.focus.document.text)
            
    def on_close(self):
        StateControl.quit()

    def enterPressed(self):
        if self.state.returnOnEnter or self.state.player.returnToMenu:
            self.returnToMenu()
            return
            
        userInput = self.widgets[0].document.text
        self.parsePlayerInput(userInput)
        self.widgets[0].clearContents()
        
        self.statsDisplay.updateStats(self.state.player, self.batch, self.group3)
        self.equipDisplay.updateEquip(self.state.player)

    def returnToMenu(self):
        pyglet.clock.unschedule(self.fadeToBlack)
        self.fadeRect.rectangle.deleteRect()
        self.startMainMenu()
            
    def parsePlayerInput(self, userInput):
        self.state.player.beginTurn()

        actingEnemies = self.state.player.getActingEnemies()
        pursuingEnemies = self.state.player.getPursuingEnemies()
        
        enemyDestination = self.state.player.currentLocation
        
        print "Player taking action"
        turnResult = self.parser.parse(userInput)
        try:
            resultString,turnPassed,sources = turnResult
        except ValueError:
            try:
                resultString, turnPassed = turnResult
                sources = list()
            except ValueError:
                resultString = turnResult
                turnPassed = False
                sources = list()
            
        gameOver = self.checkGameOver()
        if gameOver:
            resultString += gameOver
            self.displayDeathScreen(resultString)
            return
        
        if turnPassed:
            print "Turn has passed. Enemies acting"
            #Perform enemy actions
            enemyResult, enemySources = Enemies.enemyAction(self.state.player, actingEnemies)
            if (self.parser.command == "go") and (actingEnemies):
                resultString = "You run for the exit...\n" + enemyResult + "\n" + resultString
            else:
                resultString += "\n\n" + enemyResult
                sources += enemySources
            
            if self.state.player.tookHit:
                self.guiTakeHit()

            gameOver = self.checkGameOver()
            if gameOver:
                resultString += gameOver
                self.displayDeathScreen(resultString)
                return

            if turnPassed == 'transition':
                self.loadZone()
                
            if pursuingEnemies:
                resultString += Enemies.enemyMovement(pursuingEnemies, enemyDestination, self.state.player)

            gameOver = self.checkGameOver()
            if gameOver:
                resultString += gameOver
                self.updateTextBox(resultString)
                return

        for source in sources:
            self.soundPlayer.queue(source)
        self.soundPlayer.play()

        self.updateTextBox(resultString)

    def updateTextBox(self, text):
        self.disp.document.delete_text(0, len(self.disp.document.text))
        self.writingText = True
        self.textToWrite = text

    def guiTakeHit(self):
        pyglet.clock.schedule_once(self.guiStartFlash, 0)
        pyglet.clock.schedule_once(self.guiClearFlash, .1)

    def guiStartFlash(self, dt):
        self.damageFlash.rectangle.redrawRect()

    def guiClearFlash(self, dt):
        self.damageFlash.rectangle.deleteRect()

    def checkGameOver(self):
        if self.state.player.health < 1:
            return "\nYou have died...\nPress enter to return to the main menu."
        return False

    def displayDeathScreen(self, gameOverText):
        self.state.returnOnEnter = True
        self.updateTextBox(gameOverText)
        self.fadeRect.rectangle.redrawRect()
        pyglet.clock.schedule_interval(self.fadeToBlack, 0.2)

    def fadeToBlack(self, dt):
        if self.fadeRect.alpha > 60:
            self.fadeRect.alpha = 100
            pyglet.clock.unschedule(self.fadeToBlack)
        self.fadeRect.alpha = self.fadeRect.alpha + 1
        bgColor = [0, 0, 0, self.fadeRect.alpha]
        self.fadeRect.rectangle.changeRect(bgColor)
        labelColor = [155, 0, 0, self.fadeRect.alpha * 2]
        self.fadeRect.label1.color = labelColor
        self.fadeRect.label2.color = labelColor

    def updateText(self, dt):
        if self.writingText:
            if len(self.textToWrite) > 0:
                self.disp.document.text += self.textToWrite[:3]
                self.textToWrite = self.textToWrite[3:]
            else:
               self.writingText = False