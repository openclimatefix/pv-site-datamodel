""" Script to add all sites to a user

This is for internal users
"""


import json
import os

import pandas as pd
from nowcasting_dataset.data_sources.gsp.eso import get_gsp_shape_from_eso
from nowcasting_dataset.geospatial import lat_lon_to_osgb
from shapely.geometry import Point

from pvsite_datamodel.connection import DatabaseConnection
from pvsite_datamodel.read.user import get_user_by_email, get_site_group_by_name
from pvsite_datamodel.read.site import get_all_sites
from pvsite_datamodel.sqlmodels import SiteSQL, UserSQL, SiteGroupSiteSQL


user_emails = 'brad@openclimatefix.org'

url = os.getenv("DB_URL")
connection = DatabaseConnection(url=url)
with connection.get_session() as session:

    users = session.query(UserSQL).filter(UserSQL.email.contains('openclimatefix.org')).all()

    print('Found users: ' + str(len(users)))

    site_group = get_site_group_by_name(session=session, site_group_name='ocf')

    # for user in users:
    #     print(user.email)
    #
    #     # 1. attached to correct site group
    #     if user.site_group.site_group_name != 'ocf':
    #         site_group = get_site_group_by_name(session=session, site_group_name='ocf')
    #         user.site_group = site_group
    #
    #         session.commit()

    # 2. make sure all sites are in ocf site group
    all_sites = get_all_sites(session=session)
    print(f'Found {len(all_sites)} sites')

    site_uuids = [site.site_uuid for site in site_group.sites]

    for site in all_sites:
        if site.site_uuid not in site_uuids:
            print(f'Adding site {site.site_uuid} in ocf site group')
            site_group.sites.append(site)
        else:
            print(f'Site {site.site_uuid} already in ocf site group')

        # if site.client_site_name == '38 Norreys Avenue':
        #     for f in site.forecasts:
        #         for fv in f.forecast_values:
        #             session.delete(fv)
        #         session.delete(f)
        #     session.delete(site)

    session.commit()





