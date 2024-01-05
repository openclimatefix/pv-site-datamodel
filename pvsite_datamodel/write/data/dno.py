""" The script adds the relevant GSP to the sites.

Might need to install nowcasting_dataset

and we want to added the gsp as {gsp_id}|{gsp_nam} into the database

1. Load in dno data from NG
2. Load all sites
3. For each site add dno

"""
import logging
import os

import geopandas as gpd
from shapely.geometry import Point

from pvsite_datamodel.write.data.utils import lat_lon_to_osgb

logger = logging.getLogger(__name__)
dir_path = os.path.dirname(os.path.realpath(__file__))
dno_local_file = f"{dir_path}/dno"


def get_dno(latitude, longitude) -> dict:
    """
    Convert a latitude and longitude and returns the dno.

    :param latitude:
    :param longitude:

    :return: dno is this format {"dno_id": dno_id, "name": dno_name, "long_name": dno_long_name}=
    """

    # load file
    dno = gpd.read_file(dno_local_file)

    # change lat lon to osgb
    x, y = lat_lon_to_osgb(lat=latitude, lon=longitude)
    point = Point(x, y)

    # select dno
    mask = dno.contains(point)
    dno = dno[mask]

    # format dno
    if len(dno) == 1:
        dno = dno.iloc[0]

        dno_id = dno["ID"]
        name = dno["Name"]
        long_name = dno["LongName"]

        dno_dict = {"dno_id": str(dno_id), "name": name, "long_name": long_name}
        logger.debug(dno_dict)
    else:
        dno_dict = {"dno_id": "999", "name": "unknown", "long_name": "unknown"}

    return dno_dict


#
