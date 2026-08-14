import matplotlib.pyplot as plt 

organismer = ["Zooplankton", "Istidskreps", "Krøkle", "Lagesild", "Lake", "Brunørret"]
D5_mjøsa = [2.3, 11.8, 65.2, 161.9, 157.4, 2042]
D5_randsfjorden = [1.82, 0, 18.8, 0, 0, 46.78]

plt.plot(organismer, D5_mjøsa, color = "Steelblue",
    label = "Mjøsa", linestyle = ":", marker = "s")
plt.plot(organismer, D5_randsfjorden, color = "darkseagreen",
    label = "Randsfjorden", linestyle = "-", marker = "^")
plt.xlabel("Organisme")
plt.ylabel("ng siloksan per g fettvev (ng/g)")
plt.ylim(0, 200)
plt.legend()
plt.show()