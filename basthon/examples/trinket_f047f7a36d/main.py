from turtle import *

n = 8 # antall sider
sidelengde = 50
vinkel = 360/n

for i in range(n):
  forward(sidelengde)
  left(vinkel)