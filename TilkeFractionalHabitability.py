# Lana Tilke

import xarray as xr
import glob
import csv
import os
import numpy as np

# Path = Directory of NetCDF Files
# Bath = Bathymetric NetCDF File
path = "C:\\Users\\lanat\\Desktop\\NASA\\Climates_of_Warm_Earth_like_Planets_I\\AIJ"
bath = xr.open_dataset("C:\\Users\\lanat\\Desktop\\NASA\\Climates_of_Warm_Earth_like_Planets_I\\"
                       "INPUT_FILES\\Dynamic_Ocean\\OZ72X46N_gas.1_nocasp_btub005.nc")


# Opening the NetCDF Files and Processing Them
def main():
    num_files = len(glob.glob1(path, "*.nc"))
    file_counter = 0

    fieldnames = [
        "file",
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

        for file in os.listdir(path):
            if file.endswith(".nc"):
                ds = xr.open_dataset(os.path.join(path, file))
                metrics_dict = get_habitability(ds, file)
                writer.writerow(metrics_dict)
                file_counter += 1
                print(str(file_counter) + "/" + str(num_files))


# Calculating the Various Fractional Habitability Metrics of a NetCDF File
def get_habitability(ds, file):
    # The Basics
    ocean_depth = bath.zocean.data
    areas = ds.axyp.data
    water_availability = ds.avail_water_all.data  # (gwtr - gice - theta_hygro(kg/m2))/theta_sat = (gwtr - gice - 376.21)/1699.1
    temps = ds.tsurf.data
    ice_thicknesses = ds.ZSI.data
    lake_fraction = ds.lakefr.data
    lake_mass = ds.mwl.data

    rho_water = 997
    continental_height = 30
    min_water_availability = 0.0
    hab_min_temp = 0.0
    hab_max_temp = 100.0
    land_layer_heights = [0.1, 0.173, 0.298, 0.514, 0.886, 1.529]

    # Land vs. Ocean
    land_mask = np.where(ocean_depth <= continental_height, True, False)
    land_area = np.where(land_mask, areas, 0.0)
    land_area_total = np.sum(land_area)

    ocean_mask = ~land_mask
    ocean_area = np.where(ocean_mask, areas, 0.0)
    ocean_area_total = np.sum(ocean_area)

    has_ice_mask = np.where(np.isnan(ice_thicknesses), False, True)
    lake_mask = np.where(lake_fraction > 0.0, True, False)

    water_availability_mask = np.where(np.abs(water_availability) > min_water_availability, True, False)
    water_availability_mask |= lake_mask

    # Lake Habitability
    with np.errstate(divide="ignore", invalid="ignore"):
        lake_volume = np.where(lake_mask,
                               np.true_divide(np.true_divide(lake_mass, np.true_divide(lake_fraction, 100)), rho_water),
                               0.0)

    lake_has_ice_mask = has_ice_mask & lake_mask

    lake_ice_volume = np.where(lake_has_ice_mask, areas * ice_thicknesses, 0.0)
    lake_ice_volume_subsurface = 9 * lake_ice_volume
    lake_volume_total = np.sum(lake_volume) + np.sum(lake_ice_volume)

    hab_lake_volume = lake_volume - lake_ice_volume_subsurface
    hab_lake_volume_total = np.sum(np.where(hab_lake_volume > 0.0, hab_lake_volume, 0.0))
    # This was returning a big negative number, possibly due to some lakes being entirely ice/the ice thickness being

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

    # Land Volumetric Habitability
    land_layer_temps = [ds.bs_tlay1, ds.bs_tlay2, ds.bs_tlay3, ds.bs_tlay4, ds.bs_tlay5, ds.bs_tlay6]
    land_layer_temps = [a.data for a in land_layer_temps]
    land_layer_temps = np.stack(land_layer_temps, axis=0)

    hab_land_layer_volume_mask = np.repeat(water_availability_mask[np.newaxis, ...], land_layer_temps.shape[0], axis=0)
    hab_land_layer_volume_mask &= np.where(land_layer_temps > hab_min_temp, True, False)
    hab_land_layer_volume_mask &= np.where(land_layer_temps < hab_max_temp, True, False)

    land_layer_volume = [a * land_area for a in land_layer_heights]
    land_layer_volume = np.stack(land_layer_volume, axis=0)
    land_volume = np.sum(land_layer_volume, axis=0)
    land_volume_total = np.sum(land_volume)
    land_volume_total += lake_volume_total

    hab_land_layer_volume = np.where(hab_land_layer_volume_mask, land_layer_volume, 0.0)
    hab_land_volume = np.sum(hab_land_layer_volume, axis=0)
    hab_land_volume_total = np.sum(hab_land_volume)
    hab_land_volume_total += hab_lake_volume_total

    # Ocean Volumetric Habitability
    ocean_has_ice_mask = has_ice_mask & ocean_mask

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

    return {
        "file": file,
        "avg_hab_fraction_land_volume": avg_hab_fraction_land_volume,
        "avg_hab_fraction_ocean_volume": avg_hab_fraction_ocean_volume,
        "avg_hab_fraction_volume": avg_hab_fraction_volume,
        "avg_hab_fraction_land_area": avg_hab_fraction_land_area,
        "avg_hab_fraction_ocean_area": avg_hab_fraction_ocean_area,
        "avg_hab_fraction_area": avg_hab_fraction_area,
    }


main()
