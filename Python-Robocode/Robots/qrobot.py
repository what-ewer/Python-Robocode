#! /usr/bin/python
#-*- coding: utf-8 -*-

from robot import Robot #Import a base Robot
import numpy as np
import math, random, threading, time, sys, dill

class QRobot(Robot): #Create a Robot
    
    def init(self):# NECESARY FOR THE GAME   To initialyse your robot
        self.main_window = self._Robot__parent.Parent
        self.attempts_total = 100000
        self.buckets = 9
        self.alpha = 0.2 # learning rate
        self.epsilon = 0.1
        self.gamma = 0.98 # discount factor
        self.attempts_p = 0.5
        self.last_action = 0
        self.last_fire = 0

        self.main_window.scores.append(0)

        self.rewards = []
        self.target_angle = -1
        self.bullets_hit = []
        self.bullets_missed = []

        self.lower_bounds = [
            0.0, # gun direction
            0.0, # radar direction
            0.0, # opponent direction (0 if none)
             # opponent in sight
             # last_action
             # last fire - whether it hit or not - NOT USED CURRENTLY
        ]

        self.upper_bounds = [
            360.0,
            360.0,
            360.0,
        ]

        # obserwacja - stan
        # radar_direction, gun_direction, opponent in sight

        # scouting - move radar clockwise to find opponent
        # calibration - move gun to exact enemy position
        # shooting - fire
        # dodging?
        self.actions_count = 3
        # self.load_knowledge()

        #Set the bot color in RGB
        self.setColor(250, 10, 20)
        self.setGunColor(0, 0, 0)
        self.setRadarColor(200, 100, 0)
        self.setBulletsColor(100, 150, 250)
        
        #get the map size
        size = self.getMapSize() #get the map size
        self.radarVisible(True) # show the radarField        

    def discretise(self, observation):
        res = [max(min(math.floor((o - self.lower_bounds[i]) / ((self.upper_bounds[i] - self.lower_bounds[i]) / self.buckets)), self.buckets-1), 0) for i, o in enumerate(list(observation[:3]))]
        res.extend(observation[3:])
        return tuple(res)

    def pick_action(self, observation):
        if np.random.random(1) > self.get_epsilon():
            vals = [self.main_window.knowledge[i][observation] for i in range(self.actions_count)]
            return vals.index(max(vals))
        else:
            return random.randint(0, self.actions_count - 1)

    def update_knowledge(self, action, observation, new_observation, bullet=None):
        reward = self.get_reward(action, bullet)
        old_val = self.main_window.knowledge[action][observation]
        opt_fut_val = max([self.main_window.knowledge[i][new_observation] for i in range(self.actions_count)])
        self.main_window.knowledge[action][observation] = (1 - self.get_alpha()) * old_val + (self.get_alpha() * (reward + self.gamma * opt_fut_val))

    def get_alpha(self):
        alpha_temp = 0.9 - (self.main_window.attempt_no / (self.attempts_total * self.attempts_p))
        return max(alpha_temp, self.alpha)

    def get_epsilon(self):
        epsilon_temp = 0.9 - (self.main_window.attempt_no / (self.attempts_total * self.attempts_p))
        return max(epsilon_temp, self.epsilon)

    def get_observation(self):
        pos = self.getPosition()
        observation = [
            self.getGunHeading(),
            self.getRadarHeading(),
            self.target_angle,
            1 if self.target_angle != -1 else 0,
            self.last_action,
            # self.last_fire
        ]
        return observation

    def get_reward(self, action, bullet = None):
        # we want to 
        # highly reward accurate shooting
        # reward aiming for opponents
        # penalize missing 
        if action == 0: #scout
            if self.target_angle != -1:
                reward = -0.5
            else:
                reward = 0.25
        elif action == 1: #calibrate
            if self.target_angle != -1:
                reward = 0.25
            else:
                reward = -0.1
        elif action == 2: #shoot
            curr_reward = -0.7
            # todo add reward for hitting
            while bullet not in self.bullets_hit and bullet not in self.bullets_missed:
                time.sleep(0.1)
                pass
            if bullet in self.bullets_hit:
                curr_reward += 4.3
                self.bullets_hit.remove(bullet)
                self.last_fire = 1
            else:
                self.bullets_missed.remove(bullet)
                self.last_fire = 0
            reward = curr_reward
        else: # dodge
            reward = 0.1

        self.main_window.scores[-1] += reward
        return reward

    def scout(self):
        self.radarTurn(5)

    def calibrate(self, target_angle):
        if target_angle == -1:
            return
        angle = self.getGunHeading()
        self.gunTurn(target_angle - angle)

    def shoot(self):
        self.shoot(1)

    def dodge(self):
        move = random.randint(1, 7)

        rand_val = random.random()
        if rand_val < 0.45:
            self.move(move * 5)
        elif rand_val > 0.55:
            self.move(-move * 5)

        rand_val = random.random()
        if rand_val < 0.4:
            self.turn(move * 5)
        elif rand_val > 0.6:
            self.turn(-move * 5)


    def save_knowledge(self):
        with open('knowledge.dill', 'wb') as f:
            dill.dump(self.main_window.knowledge, f)
        
        with open('scores.dill', 'wb') as f:
            dill.dump(self.main_window.scores, f)
        
        with open('positions.dill', 'wb') as f:
            dill.dump(self.main_window.positions, f)
           
    def run(self): #NECESARY FOR THE GAME  main loop to command the bot
        observation = self.discretise(self.get_observation())
        action = self.pick_action(observation)
        bullet = None

        if action == 0: # scout
            self.scout()
        elif action == 1: # calibrate
            self.calibrate(self.target_angle)
        elif action == 2: # shoot  
            bullet = self.fire(1)
        elif action == 3: # dodge
            self.dodge()

        self.stop()

        new_observation = self.discretise(self.get_observation())
        threading.Thread(target=self.update_knowledge, args=(action, observation, new_observation, bullet)).start()
        # self.update_knowledge(action, observation, new_observation, bullet)
        observation = new_observation
        self.target_angle = -1
        self.main_window.attempt_no += 1
        self.last_action = action

        if self.main_window.attempt_no % 100 == 0:
            print(self.main_window.attempt_no)

        if self.main_window.attempt_no == self.attempts_total:
            self.save_knowledge()
            # threading.Thread(target=self.save_knowledge).start()
            sys.exit()


    def sensors(self):  #NECESARY FOR THE GAME
        """Tick each frame to have datas about the game"""
        
        pos = self.getPosition() #return the center of the bot
        x = pos.x() #get the x coordinate
        y = pos.y() #get the y coordinate
        
        angle = self.getGunHeading() #Returns the direction that the robot's gun is facing
        angle = self.getHeading() #Returns the direction that the robot is facing
        angle = self.getRadarHeading() #Returns the direction that the robot's radar is facing
        list = self.getEnemiesLeft() #return a list of the enemies alive in the battle
        for robot in list:
            id = robot["id"]
            name = robot["name"]
            # each element of the list is a dictionnary with the bot's id and the bot's name
        
    def onHitByRobot(self, robotId, robotName):
        self.rPrint("damn a bot collided me!")

    def onHitWall(self):
        self.reset() #To reset the run fonction to the begining (auomatically called on hitWall, and robotHit event) 
        # self.pause(100)
        # self.move(-100)
        # self.rPrint('ouch! a wall !')
        # self.setRadarField("large") #Change the radar field form
    
    def onRobotHit(self, robotId, robotName): # when My bot hit another
        self.rPrint('collision with:' + str(robotName)) #Print information in the robotMenu (click on the righ panel to see it)
       
    def onHitByBullet(self, bulletBotId, bulletBotName, bulletPower): #NECESARY FOR THE GAME
        """ When i'm hit by a bullet"""
        self.reset() #To reset the run fonction to the begining (auomatically called on hitWall, and robotHit event) 
        self.rPrint ("hit by " + str(bulletBotName) + "with power:" +str( bulletPower))
        
    def onBulletHit(self, botId, bulletId):#NECESARY FOR THE GAME
        """when my bullet hit a bot"""
        self.bullets_hit.append(bulletId)
        self.rPrint ("fire done on " +str( botId))

        
    def onBulletMiss(self, bulletId):#NECESARY FOR THE GAME
        """when my bullet hit a wall"""
        self.rPrint ("the bullet "+ str(bulletId) + " fail")
        self.bullets_missed.append(bulletId)
        # self.pause(10) #wait 10 frames
        
    def onRobotDeath(self):#NECESARY FOR THE GAME
        """When my bot die"""
        self.rPrint (f"damn I'm Dead - attempt {self.main_window.attempt_no}")
    
    def onTargetSpotted(self, botId, botName, botPos):#NECESARY FOR THE GAME
        "when the bot see another one"
        pos = self.getPosition() 
        x, y = pos.x(), pos.y()
        x_target, y_target = botPos.x(), botPos.y()
        self.target_angle = math.atan2(y- y_target, x-x_target) * 180 / math.pi + 90
        # self.fire(5)
        self.rPrint("I see the bot:" + str(botId) + "on position: x:" + str(botPos.x()) + " , y:" + str(botPos.y()))
    