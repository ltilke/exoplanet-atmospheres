# Lana Tilke
# Just a Quick Graphing Tool I Threw Together

import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("data.csv")

data.plot.scatter(x="hab_fraction_land_volume", y="hab_fraction_ocean_volume")
plt.xlabel("hab_fraction_land_volume")
plt.ylabel("hab_fraction_ocean_volume")

data.plot.scatter(x="hab_fraction_land_area", y="hab_fraction_ocean_area")
plt.xlabel("hab_fraction_land_area")
plt.ylabel("hab_fraction_ocean_area")

data.plot.scatter(x="hab_fraction_area", y="hab_fraction_volume")
plt.xlabel("hab_fraction_area")
plt.ylabel("hab_fraction_volume")

plt.show()
