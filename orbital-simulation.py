import pygame
import random
import math
import os
import sys
from collections import deque
pygame.init()
pygame.mixer.init()

font=pygame.font.SysFont('Arial', 30)
def draw_text(text,font,color,x,y):
    img=font.render(text, True, color)
    screen.blit(img, (x, y))
screen = pygame.display.set_mode((1500, 850))
is_fullscreen=False
pygame.display.set_caption("Shooting Star")
clock=pygame.time.Clock()




def draw_glow(radius,color):
    size=radius*2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    for r in range(radius,0, -1):
        falloff = (1-r/radius)**2
        alpha = int(255 * falloff)
        pygame.draw.circle(surf, (*color, alpha),(radius, radius), r)
    return surf
def get_glow(glow_cache,color,radius):
    radius=max(1,int(radius))
    if radius not in glow_cache:
        glow_cache[radius]=draw_glow(radius,color)
    return glow_cache[radius]

def gravity_at(p):
    a=pygame.Vector2(0,0)
    for planet in planets:
        d=planet.pos-p
        distance=d.length()
        if distance!=0:
            strength=G*planet.mass*1000/(distance**2)
            a+=d/distance*strength
    return a
class Planet:
    def __init__(self,mass):        
        self.pos=pygame.Vector2(random.randint(200,400), random.randint(200,400))
        self.velocity=pygame.Vector2(0,0)
        self.mass=mass
        self.color=(random.randint(10,50),random.randint(10,50),random.randint(10,50))
        self.radius=(mass/1000)**3
        if self.radius<10:
            self.radius=10
        self.tail_steps=20
        self.glow_cache={}
        self.dragged=False
    def draw(self,screen,start,end,dt):
        for i in range(self.tail_steps):
            t=i/self.tail_steps
            pos=start+(end-start)*t
            radius=self.radius*(1-t)*1.6+2
            glow=get_glow(self.glow_cache,self.color,radius*1.5)
            rect = glow.get_rect(center=pos)
            screen.blit(glow, rect, special_flags=pygame.BLEND_RGBA_ADD)
        if not paused:
            self.velocity+=gravity_at(self.pos)/self.mass
            self.pos+=self.velocity*dt
class InputBox:
    def __init__(self,x,y):
        self.x=x
        self.y=y
        self.rect=pygame.Rect(self.x, self.y, 200, 50)
        self.text=''
        self.active=False
        self.button_rect=pygame.Rect(self.x,self.y+50,100,50)
        self.passive_color=(0,255,255)
        self.active_color=(0,120,120)
        self.color=self.passive_color
        self.hovered=False
    def draw(self,screen):
        if len(self.text)>5:
            self.rect.w=100+15*(len(self.text)-5)
        else:
            self.rect.w=100
        if self.active:
            pygame.draw.rect(screen,(0,100,255),self.rect,3)
        else:
            pygame.draw.rect(screen,(0,255,255),self.rect,3)
        draw_text('tonnes',font,(0,255,255),self.x+5+self.rect.w,self.y+5)
        draw_text(self.text,font,(0,100,255),self.x+5,self.y+5)
        pygame.draw.rect(screen,self.color,self.button_rect)
        if self.hovered:
            self.color=self.active_color
            draw_text("Create",font,(255,255,255),self.x+5,self.y+55)
        else:
            self.color=self.passive_color
            draw_text("Create",font,(0,0,0),self.x+5,self.y+55)
class Notification:
    def __init__(self,text):
        self.text=text
        self.x=300
        self.y=200
    def draw(self):
        draw_text(self.text,font,(255,0,0),self.x,self.y)
        self.y-=5

planet_spawner=InputBox(10,50)
holding=None
#List
stars=[]
planets=[]
for i in range(random.randint(50,100)):
        stars.append((random.randint(0,1500),random.randint(0,850),random.randint(1,2),(random.randint(125,255),random.randint(125,255),random.randint(125,255))))
notifications=[]
#Constants
G=1000
paused=True
running=True
while running:
    #Input
    dt=clock.tick(60)/1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_f:
                is_fullscreen= not is_fullscreen
                if is_fullscreen:
                    screen = pygame.display.set_mode((1500, 850), pygame.FULLSCREEN|pygame.SCALED)
                else:
                    screen = pygame.display.set_mode((1500, 850))
            if event.key==pygame.K_SPACE:
                paused=not paused
            if planet_spawner.active:
                if event.key==pygame.K_RETURN:
                    planet_spawner.registered=True
                if event.key==pygame.K_BACKSPACE:
                    planet_spawner.text=planet_spawner.text[:-1]
                else:
                    if event.key in [pygame.K_0,pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_4,pygame.K_5,pygame.K_6,pygame.K_7,pygame.K_8,pygame.K_9]:
                        if len(planet_spawner.text)<4:
                            planet_spawner.text+=event.unicode

        mouse_pos=pygame.Vector2(pygame.mouse.get_pos())
        if planet_spawner.button_rect.collidepoint(mouse_pos):
            planet_spawner.hovered=True
        else:
            planet_spawner.hovered=False
        if event.type==pygame.MOUSEBUTTONDOWN:
            if planet_spawner.rect.collidepoint(mouse_pos):
                planet_spawner.active=True
            else:
                planet_spawner.active=False
            if planet_spawner.button_rect.collidepoint(mouse_pos):
                if int(planet_spawner.text)<=5000 and int(planet_spawner.text)>0:
                    planets.append(Planet(int(planet_spawner.text)))
                else:
                    notifications.append(Notification("Too big. Maximum planet mass is 5000 tonnes."))
                    planet_spawner.text=''
        for planet in planets:
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if planet.pos.distance_to(mouse_pos)<planet.radius:
                    planet.dragged=True
                    holding=planet
            elif event.type==pygame.MOUSEBUTTONUP and event.button==1:
                planet.dragged=False
                holding=None
            elif event.type==pygame.MOUSEMOTION and holding:
                holding.pos=mouse_pos



    #Rendering
    screen.fill((8,8,24))
    for x,y,r,color in stars:
        pygame.draw.circle(screen,color,(x,y),r)
    for planet in planets:
        planet.draw(screen,planet.pos,planet.pos,dt)
    draw_text(f"Create a planet:",font,(0,255,255),10,10)
    draw_text(f"Paused: {paused}",font,(0,255,255),700,20)
    planet_spawner.draw(screen)
    for notification in notifications:
        notification.draw()
        if notification.y<-10:
            notifications.remove(notification)
    pygame.display.flip() 
pygame.quit()