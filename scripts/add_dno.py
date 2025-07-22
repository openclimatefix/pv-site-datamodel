"""This script adds the relevant GSP to the sites

Might need to install nowcasting_dataset

and we want to added the gsp as {gsp_id}|{gsp_nam} into the database

1. Load in dno data from NG
2. Load all sites
3. For each site add dno

"""
import json
import os
import ssl

import geopandas as gpd
from nowcasting_dataset.geospatial import lat_lon_to_osgb
from shapely.geometry import Point

from pvsite_datamodel.connection import DatabaseConnection
from pvsite_datamodel.sqlmodels import SiteSQL

# 1. load metadata
ssl._create_default_https_context = ssl._create_unverified_context
url = "https://data.nationalgrideso.com/backend/dataset/0e377f16-95e9-4c15-a1fc-49e06a39cfa0/resource/e96db306-aaa8-45be-aecd-65b34d38923a/download/dno_license_areas_20200506.geojson"
dno_shapes = gpd.read_file(url)

# 2. Load all sites
url = os.getenv("DB_URL")
connection = DatabaseConnection(url=url)
with connection.get_session() as session:

    # get sites with no gsp
    query = session.query(SiteSQL)
    query = query.filter(SiteSQL.dno == None)  # noqa
    sites = query.all()

    print(f"Total sites are {len(sites)}")

    for site in sites:

        latitude = site.latitude
        longitude = site.longitude

        print(f"{latitude=}")
        print(f"{longitude=}")

        # search for point in regions
        x, y = lat_lon_to_osgb(lat=latitude, lon=longitude)
        point = Point(x, y)
        mask = dno_shapes.contains(point)
        dno = dno_shapes[mask]

        # select dno
        assert len(dno) == 1 # noqa
        dno = dno.iloc[0]

        dno_id = dno["ID"]
        name = dno["Name"]
        long_name = dno["LongName"]

        db_dno = {"dno_id": str(dno_id), "name": name, "long_name": long_name}
        print(db_dno)
        db_dno = json.dumps(db_dno)

        # add to database
        site.dno = db_dno

    # commit at the end so all sites are updated
    session.commit()
