# Lana Tilke

import xarray as xr
import glob
import csv
import os
import numpy as np

# path = Directory of NetCDF Files
path = "C:\\Users\\lanat\\Desktop\\NASA\\Climates_of_Warm_Earth_like_Planets_I\\AIJ"

# bath = Bathymetric NetCDF File
bath = xr.open_dataset("C:\\Users\\lanat\\Desktop\\NASA\\Climates_of_Warm_Earth_like_Planets_I\\INPUT_FILES\\Dynamic_Ocean\\OZ72X46N_gas.1_nocasp_btub005.nc")


# Opening the NetCDF Files and Processing Them
def main():
    num_files = len(glob.glob1(path, "*.nc"))
    file_counter = 1

    fieldnames = [
        "file_short",
        "file",
        "sdl",
        "insolation",
        "avg_hab_fraction_land_volume",
        "avg_hab_fraction_ocean_volume",
        "avg_hab_fraction_volume",
        "avg_hab_fraction_land_area",
        "avg_hab_fraction_ocean_area",
        "avg_hab_fraction_area"
    ]

    with open("data.csv", "w", encoding="UTF8", newline="") as data_csv:
        writer = csv.DictWriter(data_csv, fieldnames=fieldnames)
        writer.writeheader()

        if os.path.isdir(path):
            for file in os.listdir(path):
                if file.endswith(".nc"):
                    ds = xr.open_dataset(os.path.join(path, file))
                    metrics_dict = get_habitability(ds, file)
                    if file_counter < 10:
                        metrics_dict["file_short"] = "S0" + str(file_counter)
                    else:
                        metrics_dict["file_short"] = "S" + str(file_counter)
                    writer.writerow(metrics_dict)
                    print(str(file_counter) + "/" + str(num_files))
                    file_counter += 1
        else:
            file = path
            ds = xr.open_dataset(file)
            metrics_dict = get_habitability(ds, file)
            if file_counter < 10:
                metrics_dict["file_short"] = "S0" + str(file_counter)
            else:
                metrics_dict["file_short"] = "S" + str(file_counter)
            writer.writerow(metrics_dict)


# Calculating the Various Fractional Habitability Metrics of a NetCDF File
def get_habitability(ds, file):
    # The Basics
    ocean_depth = bath.zocean.data
    areas = ds.axyp.data  # m^2
    ice_thicknesses = ds.ZSI.data  # m
    lake_fraction = ds.lakefr.data  # %

    try:
        water_availability = ds.avail_water_all.data
    except AttributeError:
        water_availability = (ds.gwtr.data - ds.gice.data - 376.21)/1699.1

    temps = ds.tsurf.data  # C
    lake_mass = ds.mwl.data  # 10^10 kg
    solar_radiation = ds.incsw_toa_hemis.data  # W/m^2

    ice_thicknesses = np.where(np.isnan(ice_thicknesses), 0.0, ice_thicknesses)
    lake_fraction = np.true_divide(lake_fraction, 100)
    lake_mass *= 10**10  # kg
    insolation = solar_radiation[2] * 4

    continental_height = 30
    min_water_availability = 0.0
    hab_min_temp = 0.0
    hab_max_temp = 100.0
    rho_water = 997.0  # kg/m^3
    land_layer_heights = [0.1, 0.173, 0.298, 0.514, 0.886, 1.529]

    # Making Masks
    land_mask = np.where(ocean_depth <= continental_height, True, False)
    land_area = np.where(land_mask, areas, 0.0)
    land_area_total = np.sum(land_area)

    ocean_mask = ~land_mask
    ocean_area = np.where(ocean_mask, areas, 0.0)
    ocean_area_total = np.sum(ocean_area)

    has_ice_mask = np.where(np.isnan(ice_thicknesses), False, True)
    ocean_has_ice_mask = has_ice_mask & ocean_mask
    lake_mask = np.where(lake_fraction > 0.0, True, False)

    water_availability_mask = np.where(np.abs(water_availability) > min_water_availability, True, False)
    water_availability_mask |= lake_mask

    # Land Surface Area Habitability
    hab_land_area_mask = np.copy(water_availability_mask)
    hab_land_area_mask &= np.where(temps > hab_min_temp, True, False)
    hab_land_area_mask &= np.where(temps < hab_max_temp, True, False)
    hab_land_area = np.where(hab_land_area_mask, areas, 0.0)
    hab_land_area_total = np.sum(hab_land_area)

    # Ocean Surface Area Habitability
    hab_ocean_area_mask = np.copy(ocean_mask)
    hab_ocean_area_mask &= np.where(temps > hab_min_temp, True, False)
    hab_ocean_area_mask &= np.where(temps < hab_max_temp, True, False)
    hab_ocean_area = np.where(hab_ocean_area_mask, areas, 0.0)
    hab_ocean_area_total = np.sum(hab_ocean_area)

    # Land Volumetric Habitability (Including Lakes)
    land_layer_temps = [ds.bs_tlay1, ds.bs_tlay2, ds.bs_tlay3, ds.bs_tlay4, ds.bs_tlay5, ds.bs_tlay6]
    land_layer_temps = [a.data for a in land_layer_temps]
    land_layer_temps = np.stack(land_layer_temps, axis=0)

    hab_land_layer_volume_mask = np.repeat(water_availability_mask[np.newaxis, ...], land_layer_temps.shape[0], axis=0)
    hab_land_layer_volume_mask &= np.where(land_layer_temps > hab_min_temp, True, False)
    hab_land_layer_volume_mask &= np.where(land_layer_temps < hab_max_temp, True, False)

    lake_volume = np.true_divide(lake_mass, rho_water)
    lake_volume_total = np.sum(lake_volume)

    land_layer_volume = [a * land_area for a in land_layer_heights]
    land_layer_volume = np.stack(land_layer_volume, axis=0)
    land_volume = np.sum(land_layer_volume, axis=0)
    land_volume_total = np.sum(land_volume)
    land_volume_total += lake_volume_total

    hab_land_layer_volume = np.where(hab_land_layer_volume_mask, land_layer_volume, 0.0)
    hab_land_volume = np.sum(hab_land_layer_volume, axis=0)
    hab_land_volume_total = np.sum(hab_land_volume)
    hab_land_volume_total += lake_volume_total

    # Ocean Volumetric Habitability
    ocean_volume = ocean_area * ocean_depth
    ocean_volume_total = np.sum(ocean_volume)

    ice_volume = np.where(ocean_has_ice_mask, areas * ice_thicknesses, 0.0)
    ice_volume_subsurface = 9 * ice_volume

    ocean_volume_liquid = ocean_volume - ice_volume_subsurface
    hab_ocean_volume = np.where(hab_ocean_area_mask, ocean_volume_liquid, 0.0)
    hab_ocean_volume_total = np.sum(hab_ocean_volume)

    # Putting Everything Together
    avg_hab_fraction_land_volume = hab_land_volume_total / land_volume_total
    avg_hab_fraction_ocean_volume = hab_ocean_volume_total / ocean_volume_total
    avg_hab_fraction_volume = (hab_land_volume_total + hab_ocean_volume_total) / (land_volume_total + ocean_volume_total)
    avg_hab_fraction_land_area = hab_land_area_total / land_area_total
    avg_hab_fraction_ocean_area = hab_ocean_area_total / ocean_area_total
    avg_hab_fraction_area = (hab_land_area_total + hab_ocean_area_total) / (land_area_total + ocean_area_total)

    sdl = file[33:36].lstrip("0")

    return {
        "file": file,
        "sdl": sdl,
        "insolation": insolation,
        "avg_hab_fraction_land_volume": avg_hab_fraction_land_volume,
        "avg_hab_fraction_ocean_volume": avg_hab_fraction_ocean_volume,
        "avg_hab_fraction_volume": avg_hab_fraction_volume,
        "avg_hab_fraction_land_area": avg_hab_fraction_land_area,
        "avg_hab_fraction_ocean_area": avg_hab_fraction_ocean_area,
        "avg_hab_fraction_area": avg_hab_fraction_area,
    }


main()
