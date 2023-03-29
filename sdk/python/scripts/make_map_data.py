"""
Script to get centers of gsp and dno areas
"""
import json
import ssl
import geopandas as gpd
from nowcasting_dataset.data_sources.gsp.eso import get_gsp_metadata_from_eso
from nowcasting_dataset.geospatial import osgb_to_lat_lon

# make gsp centorid file
d = get_gsp_metadata_from_eso()

gsp_df = d[['centroid_lat', 'centroid_lon']]
gsp_df.rename(columns={'centroid_lat': 'lat', 'centroid_lon': 'lon'}, inplace=True)
gsp_dicts = gsp_df.to_dict(orient='records')
gsp_dicts = [[str(i),d] for i,d in enumerate(gsp_dicts)]

with open('gsp_metadata.json', 'w') as f:
    json.dump(gsp_dicts, f, indent=4)


# make dno centorid file
ssl._create_default_https_context = ssl._create_unverified_context
url = "https://data.nationalgrideso.com/backend/dataset/0e377f16-95e9-4c15-a1fc-49e06a39cfa0/resource/e96db306-aaa8-45be-aecd-65b34d38923a/download/dno_license_areas_20200506.geojson"
dno_shapes = gpd.read_file(url)

dno_shapes["centroid_x"] = dno_shapes["geometry"].centroid.x
dno_shapes["centroid_y"] = dno_shapes["geometry"].centroid.y
dno_shapes["lat"], dno_shapes["lon"] = osgb_to_lat_lon(
    x=dno_shapes["centroid_x"], y=dno_shapes["centroid_y"]
)

dno_df = dno_shapes[['lat', 'lon']]
dno_dicts = dno_df.to_dict(orient='records')
dno_dicts = [[str(i),d] for i,d in enumerate(dno_dicts)]

with open('dno_metadata.json', 'w') as f:
    json.dump(dno_dicts, f, indent=4)
