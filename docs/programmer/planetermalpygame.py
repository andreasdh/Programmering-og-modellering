import pygame
from pylab import *
a = 0
b = 1
N = 1000
t = linspace(a,b,N)
dt = t[1]-t[0]

P = 0
# Filinnlesing på samme måte som i dellopgave f)

# Lag et vindu som er 840 x 840 stort med sort bakgrunn
# og tegn sola midt i vinduet

skrift = pygame.font.SysFont("monospace", 15) # For å vise tekst
tekst = "År: "

farger = [0]*P
for k in range(P):
    # generer tilfeldig farge for hver planet
    # hver r,g og b er tilfeldige heltall mellom 0 og 255
	farger[k] = (r,g,b)

run = True
i = 0
yr = 0
while run:
    # Tegn den sorte bakgrunnen og sola på nytt

	t = skrift.render(tekst+str(yr), 12, (255,255,255)) # Skriver tekst som
                                                        # forteller hvilker år
                                                        # simuleringen er på
	vindu.blit(t,(1,1)) # Plasser tekst

	for j in range(P): # gå gjennom hver planet
		pos_planet = pos[i,:,j]
		fart_planet = fart[i,:,j]

		# Regner ut akselerasjon til denne planeten (planet j)
        # som er påvirket av solen

		for k in range(P):
            # hvis k ikke er lik j:
                pos_andreplanet = pos[i,:,k]
                fart_andreplanet = fart[i,:,k]
                # Akselerasjon til planet som er påvirket av
                # andreplanet (planet k)

        # Euler-Cromer til fart[i+1,:,j] og pos[i+1,:,j]
		px = pos[i+1,0,j]
		py = pos[i+1,1,j]
		pygame.draw.circle(vindu,farger[j],(int(round(200*px+vindux/2)),int(round(200*py+vinduy/2))),10)

	if i+1 < N-1:
		i += 1
	else:
		i = 0
		pos[0,:,:] = pos[N-1,:,:]
		fart[0,:,:] = fart[N-1,:,:]
		yr += 1

    # Oppdater induet

	for e in pygame.event.get():
		if e.type == pygame.QUIT:
			run = False
			pygame.quit()
