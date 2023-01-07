#! /usr/bin/python
#-*- coding: utf-8 -*-

from robot import Robot #Import a base Robot
import math, random

class RandomBot(Robot): #Create a Robot
    
    def init(self):    #To initialyse your robot
        
        
        #Set the bot color in RGB
        self.setColor(255, 0, 0)
        self.setGunColor(255, 0, 0)
        self.setRadarColor(255, 0, 0)
        self.setBulletsColor(255, 0, 0)
        
        self.radarVisible(True) # if True the radar field is visible
        
        #get the map size
        size = self.getMapSize()
        
        self.lockRadar("gun")
        self.setRadarField("thin")
        self.inTheCorner = False
        

    
    def run(self): #main loop to command the bot
        # angle=self.getHeading() % 360
        # print ("going angle:",angle)
        # self.move(5)
        action = random.randint(0, 8)
        if action == 0: # move ahead
            self.move(5)
        elif action == 1: # move back
            self.move(-5)
        elif action == 2: # turn right     
            self.turn(5)
        elif action == 3: # turn left
            self.turn(-5)
        elif action == 4: # turn gun right
            self.gunTurn(5)
        elif action == 5: # turn gun left
            self.gunTurn(-5)
        elif action == 6: # turn radar right
            self.radarTurn(5)
        elif action == 7: # turn radar left
            self.radarTurn(-5)
        elif action == 8: # fire
            self.fire(1)
        self.stop()

    def onHitWall(self):
        pass

    def sensors(self): 
        pass
        
    def onRobotHit(self, robotId, robotName): # when My bot hit another
        pass
        
    def onHitByRobot(self, robotId, robotName):
        pass

    def onHitByBullet(self, bulletBotId, bulletBotName, bulletPower): #NECESARY FOR THE GAME
        pass
        
    def onBulletHit(self, botId, bulletId):#NECESARY FOR THE GAME
        pass
        
    def onBulletMiss(self, bulletId):
        pass
        
    def onRobotDeath(self):
        pass
        
    def onTargetSpotted(self, botId, botName, botPos):#NECESARY FOR THE GAME
        pass
