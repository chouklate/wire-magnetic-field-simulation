# Variables --------------------------------------
R = 7  #Calculates value for every R pixels (horizontally and vertically). Increasing this value will result in slower computation
DR = 4 # Draw X or Os every R * DR pixels
HEIGHT = 600 # Screen height
WIDTH = 1000 # Screen width

# ------------------------------------------------


import numpy as np
from numpy import array as V
import pygame
import time


class Wire:
    """ line with representation a + tn"""
    def __init__(self, current, a = V([0,0]), n = V([1,0])):
        self.current = current
        self.a = a
        self.n = n #n must be a normalized vector


    def initiate(self, p1, p2):
        #for 2 points create a line
        self.a = p1
        dp = p2 - p1
        dp_norm = np.linalg.norm(dp)
        self.n = dp / np.linalg.norm(dp) if dp_norm != 0 else V([1,0]) # if clicked on same location twice


    def getDistance(self, p):
        """calculate distance from point p"""
        pVector = (self.a - p) -((np.dot((self.a-p), self.n))*self.n)
        dVector = np.cross(self.n, pVector) # - if coming in + if coming out
        if dVector > 0:
            return np.linalg.norm(pVector)
        else:
            return -np.linalg.norm(pVector)


    def getB(self, p):
        d = self.getDistance(p)
        if 0 <= d <= 0.001: # Cap at d=+-0.001
            d = 0.001
        if -0.001 <= d < 0:
            d = -0.001
        return self.current / d



pygame.init()


def NewWire(mp1, mp2):
    global Wires
    wire = Wire(1000)
    wire.initiate(V(mp1) , V(mp2))
    Wires.append(wire)
    getBmap()
    drawBmap()



def getBmap():
    global Bmap
    for i in range(0, len(Bmap)):
        for j in range(0, len(Bmap[0])):
            Bmap[i][j] += Wires[-1].getB(V([i*R, j*R]))
        print("row {} of {} complete (step {})".format(i, len(Bmap)-1, R))
        print("Calculated!")
    # It probably would be much faster to approximate the B value by grouping points in a certain range to a wire,
    # applying the B value, and iterating over every wire but oh well


def drawBmap():
    global Bmap
    display.fill((0,0,0))
    for i in range(0, len(Bmap), DR):
        for j in range(0, len(Bmap[0]), DR):
            B = Bmap[i][j]
            color = getColor(B)
            if B < 0:
                pygame.draw.line(display, color, (R*i -3, R*j -3), (R*i +3 , R*j +3), 2)
                pygame.draw.line(display, color, (R *i-3, R * j + 3), (R * i + 3, R * j - 3), 2)

            if B > 0:
                pygame.draw.circle(display, color, (R*i, R*j),2)

            if B == 0:
                display.set_at((R*i, R*j), color)
    drawWires()
    print("Drawn!")


def drawWires():
    for wire in Wires:
        pygame.draw.line(display, (220,220,220), ((wire.a-10000*wire.n)[0], (wire.a-10000*wire.n)[1]), ((wire.a+10000*wire.n)[0], (wire.a+10000*wire.n)[1]), 5)
        dirL = - V([(wire.n[0] + wire.n[1]) * 0.5, (wire.n[1] - wire.n[0]) * 0.5])
        dirR = - V([( wire.n[0] - wire.n[1]) * 0.5, (wire.n[0] + wire.n[1]) * 0.5])
        for t in range(-10000,10000,100):
            p2 = wire.a + t * wire.n
            p3 = p2 + 25 * dirL
            p4 = p2 + 25 * dirR
            pygame.draw.line(display, (220, 220, 220), (p3[0], p3[1]), (p2[0], p2[1]), 3)
            pygame.draw.line(display, (220, 220, 220), (p4[0], p4[1]), (p2[0], p2[1]), 3)


def getMaxB():
    max_B = 0
    for wire in Wires:
        if wire.current > max_B:
            max_B = wire.current
    return max_B


def getColor(B):
    B = abs(B)
    k = 0.01
    max_B = getMaxB()
    if B >= k* max_B:
        B = k* max_B

    if max_B == 0:
        max_B = 1

    cValue = int(((B) * 255 / max_B) /k)
    color = (cValue, 255-cValue, 0, 255) #cValue)

    return color

# Pygame variables

FPS = 60
display = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("자기장 시뮬레이션")
font = pygame.font.SysFont(None, 40)
text_surface = pygame.Surface((250, 50))
clock = pygame.time.Clock()
firstButtonDown = False
run = True
Bmap = np.zeros((WIDTH//R + 1, HEIGHT//R+1), dtype="float32")

Wires = []

# pygame logic -----------------------------------

drawBmap()

while run:
    mousePos = pygame.mouse.get_pos()
    #t1 = time.time()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                if not firstButtonDown:
                    mp1 = mousePos
                    firstButtonDown = True
                else:
                    NewWire(mp1, mousePos)
                    firstButtonDown = False

    img = font.render(str(round(Bmap[mousePos[0]//R][mousePos[1]//R], 5)) +" (μT)", True, (255, 255, 255))
    text_surface.fill((0, 0, 0))
    text_surface.blit(img, (20, 20))

    display.blit(text_surface, (0,0))
    pygame.display.update()
    clock.tick(FPS)
    #t2 = time.time()
    #if(t2-t1 >0.0001):
    #    pass

pygame.quit()


