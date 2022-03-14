from pylab import *
a = 0
b = 15
N = 10000
t = linspace(a,b,N)
dt = t[1]-t[0]

P = 0

# åpner filen og leser
planeter_data.dat som infile:

	# Sett lik P til å være den første linje i filen
	pos = zeros([N,2,P])
	fart = zeros([N,2,P])
	masse = zeros(N)
	for i,line in enumerate(infile):
		data = line.split()
        # Hent ut de nødvendige datatene og omgjør til flyttall

		pos[0,:,i] = array([x,y]) # x og y er startposisjon
                                  # langs hhv. x- og y-aksen til planet i

		fart[0,:,i] = array([vx,vy]) # vx og vy er startfart
                                     # langs hhv. x- og y-aksen til planet i

		# Sett det i-te elementet i masse til å være lik planet i sin masse

for i in range(N-1):
    for j in range(P):
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

for p in range(P):
    x = pos[:,0,p]
    y = pos[:,1,p]
    #Tegner posisjonen til planet p

# Tegner sola som gul prikk
# Viser fram plott
