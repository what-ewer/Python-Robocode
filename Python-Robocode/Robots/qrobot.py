#! /usr/bin/python
#-*- coding: utf-8 -*-

from robot import Robot #Import a base Robot
import numpy as np
import math
import importlib
# gui_window = importlib.import_module("GUI.window")
# qStore = gui_window.qStore
# sim_data_queue = gui_window.sim_data_queue
# from GUI.window import sim_data_queue, qStore
from scipy.special import softmax

class QRobot(Robot): #Create a Robot
    
    def init(self):# NECESARY FOR THE GAME   To initialyse your robot
        # obserwacja - stan
        # position_x, position_y, direction, radar_direction, gun_direction, health, enemy_seen, enemy_x, enemy_y
        self.upper_bounds = [
            self.getMapSize().width(),
            self.getMapSize().height(),
            360.0,
            360.0,
            360.0,
            100.0,
            1.0,
            self.getMapSize().width(),
            self.getMapSize().height()
        ]

        # possible actions - move, turn, gunTurn, radarTurn, fire  - always use shortest action that requires only 1 turn
        # move, turn, gunTurn, radarTurn require two actions - left/right and ahead/back

        # self.actions_count = 9
        # self.knowledge = {
        #     i: defaultdict(lambda: np.random.random(1))
        #     for i in range(self.actions_count)
        # }

        #Set the bot color in RGB
        self.setColor(160, 2, 199)
        self.setGunColor(255, 255, 38)
        self.setRadarColor(255, 178, 196)
        self.setBulletsColor(255, 255, 255)
        
        #get the map size
        size = self.getMapSize() #get the map size
        self.radarVisible(True) # show the radarField

    def normalize_state(self, observation):
        res = [min(max((o - 0) / (self.upper_bounds[i] - 0), 0), 1) for i, o in enumerate(list(observation))]
        return np.array(res)

    # def discretise(self, observation):
    #     res = [max(min(math.floor((o - self.lower_bounds[i]) / ((self.upper_bounds[i] - self.lower_bounds[i]) / self.buckets)), self.buckets-1), 0) for i, o in enumerate(list(observation[:-1]))]
    #     res.append(observation[-1]) # we do not discretise event
    #     return tuple(res)

    # def pick_action(self, observation):
    #     if np.random.random(1) > self.get_epsilon():
    #         vals = [self.knowledge[i][observation] for i in range(self.actions_count)]
    #         return vals.index(max(vals))
    #     else:
    #         return random.randint(0, self.actions_count - 1)

    # def update_knowledge(self, action, observation, new_observation, reward):
    #     old_val = self.knowledge[action][observation]
    #     opt_fut_val = max([self.knowledge[i][new_observation] for i in range(self.actions_count)])
    #     self.knowledge[action][observation] = (1 - self.get_alpha()) * old_val + (self.get_alpha() * (reward + self.gamma * opt_fut_val))

    # def get_alpha(self):
    #     alpha_temp = 0.9 - (self.attempt_no / (self.attempts_total * self.attempts_p))
    #     return max(alpha_temp, self.alpha)

    # def get_epsilon(self):
    #     epsilon_temp = 0.9 - (self.attempt_no / (self.attempts_total * self.attempts_p))
    #     return max(epsilon_temp, self.epsilon)

    # state = [self.x,self.y, self.alpha, self.hp ... |  r.v, r.x, r.y]

    def get_observation(self):
        pos = self.getPosition()
        closest_enemy_in_radar = None
        for item in set(self._Robot__radar.collidingItems(1)) - self._Robot__items:
            if isinstance(item, Robot):
                if not closest_enemy_in_radar:
                    closest_enemy_in_radar = item
                else: # swap the closest enemy to be the one closer to gun axis
                    x_0, y_0 = self.getPosition().x(), self.getPosition().y()
                    x_1, y_1 = closest_enemy_in_radar.getPosition().x(), closest_enemy_in_radar.getPosition().y()
                    x_2, y_2 = item.getPosition().x(), item.getPosition().y()
                    gun_angle = self.getGunHeading()
                    angle_1 = math.atan2(y_1 - y_0, x_1 - x_0) * 180 / math.pi
                    angle_2 = math.atan2(y_2 - y_0, x_2 - x_0) * 180 / math.pi
                    if abs(angle_1 - gun_angle) > abs(angle_2 - gun_angle):
                        closest_enemy_in_radar = item

        observation = [
            pos.x(),
            pos.y(),
            self.getHeading(),
            self.getGunHeading(),
            self.getRadarHeading(),
            self._Robot__health,
            1 if closest_enemy_in_radar else 0,
            0 if not closest_enemy_in_radar else closest_enemy_in_radar.getPosition().x(),
            0 if not closest_enemy_in_radar else closest_enemy_in_radar.getPosition().y(),
        ]
        return observation


    def get_reward(self):
        HP_WEIGHT = 2.0
        ENEMIES_WEIGHT = 1.0
        
        alive_bots = len(self._Robot__parent.aliveBots)
        dead_bots = len(self._Robot__parent.deadBots)
        total_bots = alive_bots + dead_bots

        reward = (self._Robot__health/100)*HP_WEIGHT + (dead_bots/(total_bots-1))*ENEMIES_WEIGHT if self._Robot__health > 0 else 0

        return reward
    
    def run(self): #NECESARY FOR THE GAME  main loop to command the bot
        window_parent = self._Robot__parent.Parent
        state_t = self.normalize_state(self.get_observation())
        action_p = window_parent.qStore.get_q(state_t)

        print(action_p)

        move = np.random.choice(3, p=softmax(action_p[0:3]))  # 0-don't move, 1-left, 2-right
        rotate_robot = np.random.choice(3, p=softmax(action_p[3:6])) # 0-don't rotate, 1-left, 2-right
        rotate_gun = np.random.choice(3, p=softmax(action_p[6:9]))  # 0-don't rotate, 1-left, 2-right
        rotate_radar = np.random.choice(3, p=softmax(action_p[9:12]))  # 0-don't rotate, 1-left, 2-right
        shoot =  np.random.choice(2, p=softmax(action_p[12:14]))  # 0-don't shoot, 1-shoot
        # print(action_p)

        if move == 0: # don't move
            pass
        if move == 1: # move left
            self.move(-5)
        if move == 2: # move right
            self.move(5)
        
        if rotate_robot == 0: # don't rotate robot
            pass
        if rotate_robot == 1: # rotate left
            self.turn(-5)
        if rotate_robot == 2: # rotate right
            self.turn(5)

        if rotate_gun == 0: # don't rotate gun
            pass
        if rotate_gun == 1: # rotate left
            self.gunTurn(-5)
        if rotate_gun == 2: # rotate right
            self.gunTurn(5)

        if rotate_radar == 0: # don't rotate radar
            pass
        if rotate_radar == 1: # rotate left
            self.radarTurn(-5)
        if rotate_radar == 2: # rotate right
            self.radarTurn(5)

        if shoot == 0: # don't shoot
            pass
        if shoot == 1: # shoot 
            self.fire(1)
            
        self.stop()
        # TODO get discrete actions from proba vector

        # if action == 0: # move ahead
        #     self.move(5)
        # elif action == 1: # move back
        #     self.move(-5)
        # elif action == 2: # turn right     
        #     self.turn(5)
        # elif action == 3: # turn left
        #     self.turn(-5)
        # elif action == 4: # turn gun right
        #     self.gunTurn(5)
        # elif action == 5: # turn gun left
        #     self.gunTurn(-5)
        # elif action == 6: # turn radar right
        #     self.radarTurn(5)
        # elif action == 7: # turn radar left
        #     self.radarTurn(-5)
        # elif action == 8: # fire
        #     self.fire(1)
        # self.stop()

        # new_observation = self.discretise(self.get_observation())
        # self.update_knowledge(action, observation, new_observation, 1)
        # observation = new_observation

        action_t = [move, rotate_robot+3, rotate_gun+6, rotate_radar+9, shoot+12]
        reward_t = self.get_reward()
        state_t_plus_1= self.normalize_state(self.get_observation())

        #put data necessary to train on queue
        window_parent.sim_data_queue.append((state_t, action_t, reward_t, state_t_plus_1, False))

        

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
        self.rPrint ("fire done on " +str( botId))

        
    def onBulletMiss(self, bulletId):#NECESARY FOR THE GAME
        """when my bullet hit a wall"""
        self.rPrint ("the bullet "+ str(bulletId) + " fail")
        # self.pause(10) #wait 10 frames
        
    def onRobotDeath(self):#NECESARY FOR THE GAME
        """When my bot die"""
        self.rPrint (f"damn I'm Dead")
    
    def onTargetSpotted(self, botId, botName, botPos):#NECESARY FOR THE GAME
        "when the bot see another one"
        # self.fire(5)
        self.rPrint("I see the bot:" + str(botId) + "on position: x:" + str(botPos.x()) + " , y:" + str(botPos.y()))
    