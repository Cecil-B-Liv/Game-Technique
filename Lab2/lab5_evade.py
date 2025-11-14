# =====================================================================
# evade_behavior.py
# Lab 5: Evade Behavior
# Course: Games and AI Techniques
# =====================================================================
# Goal:
#   Demonstrate how an agent can flee intelligently by predicting
#   where the pursuer will be, instead of reacting too late.
# =====================================================================

import pygame
import math
pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Steering Behavior: EVADE")
clock = pygame.time.Clock()

def vec_length(v): return math.sqrt(v[0]**2 + v[1]**2)
def vec_normalize(v):
    l = vec_length(v)
    if l == 0: return (0,0)
    return (v[0]/l, v[1]/l)
def vec_sub(a,b): return (a[0]-b[0], a[1]-b[1])
def vec_add(a,b): return (a[0]+b[0], a[1]+b[1])
def vec_mul(v,s): return (v[0]*s, v[1]*s)
def vec_limit(v,maxv):
    l=vec_length(v)
    if l>maxv:
        v=vec_normalize(v)
        return (v[0]*maxv,v[1]*maxv)
    return v

class Pursuer:
    def __init__(self,x,y):
        self.position=(x,y)
        self.velocity=(2.5,1.8)
        self.radius=10
    def update(self):
        self.position=vec_add(self.position,self.velocity)
        x,y=self.position
        if x<self.radius or x>WIDTH-self.radius:
            self.velocity=(-self.velocity[0],self.velocity[1])
        if y<self.radius or y>HEIGHT-self.radius:
            self.velocity=(self.velocity[0],-self.velocity[1])
    def draw(self,surface):
        pygame.draw.circle(surface,(255,60,60),(int(self.position[0]),int(self.position[1])),self.radius)

class Agent:
    def __init__(self,x,y):
        self.position=(x,y)
        self.velocity=(0,0)
        self.acceleration=(0,0)
        self.max_speed=4.0
        self.max_force=0.1
    def evade(self,pursuer):
        to_pursuer=vec_sub(pursuer.position,self.position)
        distance=vec_length(to_pursuer)
        speed=vec_length(self.velocity) if vec_length(self.velocity)>0 else self.max_speed
        prediction_time=distance/speed
        future_position=vec_add(pursuer.position,vec_mul(pursuer.velocity,prediction_time*0.5))
        desired=vec_sub(self.position,future_position)
        desired=vec_normalize(desired)
        desired=vec_mul(desired,self.max_speed)
        steer=vec_sub(desired,self.velocity)
        steer=vec_limit(steer,self.max_force)
        self.acceleration=steer
    def update(self):
        self.velocity=vec_add(self.velocity,self.acceleration)
        self.velocity=vec_limit(self.velocity,self.max_speed)
        self.position=vec_add(self.position,self.velocity)
        self.acceleration=(0,0)
    def draw(self,surface):
        x,y=self.position
        if vec_length(self.velocity)==0:
            angle=0
        else:
            angle=math.degrees(math.atan2(-self.velocity[1],self.velocity[0]))
        size=15
        pts=[
            (x+math.cos(math.radians(angle))*size,
             y-math.sin(math.radians(angle))*size),
            (x+math.cos(math.radians(angle+120))*size*0.5,
             y-math.sin(math.radians(angle+120))*size*0.5),
            (x+math.cos(math.radians(angle-120))*size*0.5,
             y-math.sin(math.radians(angle-120))*size*0.5)
        ]
        pygame.draw.polygon(surface,(0,255,0),pts)

def main():
    running=True
    pursuer=Pursuer(WIDTH//2,HEIGHT//3)
    agent=Agent(WIDTH*0.7,HEIGHT*0.6)
    while running:
        dt=clock.tick(60)/1000
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
        pursuer.update()
        agent.evade(pursuer)
        agent.update()
        screen.fill((30,30,30))
        pursuer.draw(screen)
        agent.draw(screen)
        pygame.draw.line(screen,(100,100,255),(int(agent.position[0]),int(agent.position[1])),(int(pursuer.position[0]),int(pursuer.position[1])),1)
        font=pygame.font.SysFont("consolas",20)
        txt=font.render("Agent evades pursuer",True,(255,255,255))
        screen.blit(txt,(20,20))
        pygame.display.flip()
    pygame.quit()

if __name__=="__main__":
    main()