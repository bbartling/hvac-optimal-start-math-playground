

import matplotlib.pyplot as plt



# t = 0.7 * x**2 + 6

def compute_times(deltaTemp):
    minutes = 0.7 * deltaTemp**2 + 6
    return round(minutes,2)


DeltaTemps = [3, 5, 7]
dataForPlot = []

for DeltaT in DeltaTemps:
    #print(DeltaT)
    data = compute_times(DeltaT)
    dataForPlot.append(data)
    print("Minutes ",data)


print(dataForPlot)

plt.plot(dataForPlot)
plt.show()