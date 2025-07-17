"""GSP functions for UK regions."""

import logging
import os

import pandas as pd

from pvsite_datamodel.write.data.utils import lat_lon_to_osgb

try:
    import geopandas as gpd
    from shapely.geometry import Point
except ImportError:
    print("You might want to install geopandas")  # noqa

logger = logging.getLogger(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))
gsp_local_file = f"{dir_path}/gsp"
gsp_names = pd.read_csv(f"{dir_path}/gsp_new_ids_and_names-edited.csv")


def get_gsp(latitude: float, longitude: float) -> dict:
    """Get a DNO from latitude and longitude.

    :param latitude:
    :param longitude:

    :return: dno is this format {"dno_id": dno_id, "name": dno_name, "long_name": dno_long_name}=
    """
    # load file
    gsp = gpd.read_file(gsp_local_file)

    # change lat lon to osgb
    x, y = lat_lon_to_osgb(lat=latitude, lon=longitude)
    point = Point(x, y)

    # select gsp
    mask = gsp.contains(point)
    gsp = gsp[mask]

    # format gsp
    if len(gsp) == 1:
        gsp = gsp.iloc[0]
        gsp_details = gsp_names[gsp_names["gsp_name"] == gsp.GSPs]
        gsp_id = gsp_details.index[0]
        gsp_details = gsp_details.iloc[0]
        name = gsp_details["region_name"]

        gsp_dict = {"gsp_id": str(gsp_id), "name": name}
    else:
        gsp_dict = {"gsp_id": "999", "name": "unknown"}

    return gsp_dict
