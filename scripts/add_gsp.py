""" This script adds the relevant GSP to the sites

Might need to install nowcasting_dataset

and we want to added the gsp as {gsp_id}|{gsp_nam} into the database

1. Load in metadata
2. Load in gsp names
3. Load all sites
4. For each site add gsp

"""
import json
import os

import pandas as pd
from nowcasting_dataset.data_sources.gsp.eso import get_gsp_shape_from_eso
from nowcasting_dataset.geospatial import lat_lon_to_osgb
from shapely.geometry import Point

from pvsite_datamodel.connection import DatabaseConnection
from pvsite_datamodel.sqlmodels import SiteSQL

# 1. load metadata
eso_meta = get_gsp_shape_from_eso()

# 2.
dir = ""
print(os.getcwd())
dir = "./scripts"
gsp_names = pd.read_csv(f"{dir}/gsp_new_ids_and_names-edited.csv")


# 3. Load all sites
url = os.getenv("DB_URL")
connection = DatabaseConnection(url=url)
with connection.get_session() as session:

    # get sites with no gsp
    query = session.query(SiteSQL)
    query = query.filter(SiteSQL.gsp == None)
    sites = query.all()

    print(f"Total sites are {len(sites)}")

    for site in sites:

        latitude = site.latitude
        longitude = site.longitude

        print(f"{latitude=}")
        print(f"{longitude=}")

        # search for point in region
        x, y = lat_lon_to_osgb(lat=latitude, lon=longitude)
        point = Point(x, y)
        mask = eso_meta.contains(point)
        gsp = eso_meta[mask]

        # select region and get gsp_id and name
        assert len(gsp) == 1
        gsp = gsp.iloc[0]
        gsp_details = gsp_names[gsp_names["gsp_name"] == gsp.GSPs]
        assert len(gsp_details) == 1
        gsp_id = gsp_details.index[0]
        gsp_details = gsp_details.iloc[0]
        name = gsp_details["region_name"]

        db_gsp = {"gsp_id": str(gsp_id), "name": name}
        print(db_gsp)
        db_gsp = json.dumps(db_gsp)

        print(db_gsp)

        site.gsp = db_gsp

    session.commit()
