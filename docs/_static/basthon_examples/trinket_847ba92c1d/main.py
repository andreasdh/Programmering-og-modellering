def penger_i_banken(startkapital, sluttkapital, renter):
    kapital = startkapital
    år = 0
    while kapital <= sluttkapital:
        kapital = kapital + kapital*renter
        år = år + 1
    return kapital, år

penger, tid = penger_i_banken(1000, 3000, 0.01)
print("Det tar", tid, "år før du har", round(penger,2), "kroner i banken.")