""" Script us used to download DNO and GSP data from NG. """
import logging
import os
import ssl

import geopandas as gpd
import pandas as pd

from pvsite_datamodel.write.data import utils

logger = logging.getLogger(__name__)
dir_path = os.path.dirname(utils.__file__)
dno_local_file = f"{dir_path}/dno"


dir_path = os.path.dirname(utils.__file__)
gsp_local_file = f"{dir_path}/gsp"
gsp_names = pd.read_csv(f"{dir_path}/gsp_new_ids_and_names-edited.csv")


def download_dno():
    """Download DNO data from NG."""

    logger.debug("Getting dno file")
    ssl._create_default_https_context = ssl._create_unverified_context
    url = "https://data.nationalgrideso.com/backend/dataset/0e377f16-95e9-4c15-a1fc-49e06a39cfa0/resource/e96db306-aaa8-45be-aecd-65b34d38923a/download/dno_license_areas_20200506.geojson"  # noqa
    dno_shapes = gpd.read_file(url)

    logger.debug("Saving dno file")
    dno_shapes.to_file(dno_local_file)


def download_gsp():
    """Down GSP data from NG."""

    logger.debug("Getting gsp file")

    url = (
        "https://data.nationalgrideso.com/backend/dataset/2810092e-d4b2-472f-b955-d8bea01f9ec0/"
        "resource/08534dae-5408-4e31-8639-b579c8f1c50b/download/gsp_regions_20220314.geojson"
    )
    ssl._create_default_https_context = ssl._create_unverified_context
    gsp_shapes = gpd.read_file(url)

    logger.debug("Saving gsp file")
    gsp_shapes.to_file(gsp_local_file)

# download_dno()
# download_gsp()
