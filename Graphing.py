# Lana Tilke

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

plt.rc("font", family="serif")
plt.rc("xtick", labelsize="x-small")
plt.rc("ytick", labelsize="x-small")

df = pd.read_csv("data.csv")

sdl_ticks = np.array(df["sdl"])
sdl_ticks = np.unique(sdl_ticks)

# Sidereal Day Length
ax = df.plot(kind="scatter",
             x="sdl",
             y="avg_hab_fraction_ocean_volume",
             color="c", marker="o", label="Ocean")
df.plot(kind="scatter",
        x="sdl",
        y="avg_hab_fraction_land_volume",
        color="y", marker="o", label="Land", ax=ax)
df.plot(kind="scatter",
        x="sdl",
        y="avg_hab_fraction_volume",
        color="m", marker=".", label="Total", ax=ax)

ax.set_xscale("log")
plt.ylim(bottom=-0.05, top=1.05)
ax.set_xlabel("Sidereal Day Length")
ax.set_ylabel("Habitable Fraction")
plt.title(r"Habitable Fraction (Volume) vs. Sidereal Day Length (SDL$_\oplus$)")
plt.xticks(ticks=sdl_ticks, labels=sdl_ticks)
plt.minorticks_off()
plt.legend(loc="best")
plt.savefig("figs\\volume_sdl.png", dpi=600)
plt.show()

ax = df.plot(kind="scatter",
             x="sdl",
             y="avg_hab_fraction_ocean_area",
             color="c", marker="o", label="Ocean")
df.plot(kind="scatter",
        x="sdl",
        y="avg_hab_fraction_land_area",
        color="y", marker="o", label="Land", ax=ax)
df.plot(kind="scatter",
        x="sdl",
        y="avg_hab_fraction_area",
        color="m", marker=".", label="Total", ax=ax)

ax.set_xscale("log")
plt.ylim(bottom=-0.05, top=1.05)
ax.set_xlabel("Sidereal Day Length")
ax.set_ylabel("Habitable Fraction")
plt.title(r"Habitable Fraction (Area) vs. Sidereal Day Length (SDL$_\oplus$)")
plt.xticks(ticks=sdl_ticks, labels=sdl_ticks)
plt.minorticks_off()
plt.legend(loc="best")
plt.savefig("figs\\area_sdl.png", dpi=600)
plt.show()

# Insolation
ax = df.plot(kind="scatter",
             x="insolation",
             y="avg_hab_fraction_ocean_volume",
             color="c", marker="o", label="Ocean")
df.plot(kind="scatter",
        x="insolation",
        y="avg_hab_fraction_land_volume",
        color="y", marker="o", label="Land", ax=ax)
df.plot(kind="scatter",
        x="insolation",
        y="avg_hab_fraction_volume",
        color="m", marker=".", label="Total", ax=ax)

plt.ylim(bottom=-0.05, top=1.05)
ax.set_xlabel("Insolation")
ax.set_ylabel("Habitable Fraction")
plt.title(r"Habitable Fraction (Volume) vs. Insolation (W/m$^2$)")
plt.legend(loc="best")
plt.savefig("figs\\volume_insolation.png", dpi=600)
plt.show()

ax = df.plot(kind="scatter",
             x="insolation",
             y="avg_hab_fraction_ocean_area",
             color="c", marker="o", label="Ocean")
df.plot(kind="scatter",
        x="insolation",
        y="avg_hab_fraction_land_area",
        color="y", marker="o", label="Land", ax=ax)
df.plot(kind="scatter",
        x="insolation",
        y="avg_hab_fraction_area",
        color="m", marker=".", label="Total", ax=ax)

plt.ylim(bottom=-0.05, top=1.05)
ax.set_xlabel("Insolation")
ax.set_ylabel("Habitable Fraction")
plt.title(r"Habitable Fraction (Area) vs. Insolation (W/m$^2$)")
plt.legend(loc="best")
plt.savefig("figs\\area_insolation.png", dpi=600)
plt.show()
