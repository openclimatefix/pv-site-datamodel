""" Tools for making fake users and sites in the database."""
from datetime import datetime, timezone
import sqlalchemy as sa
from sqlalchemy.sql import func
from pvsite_datamodel.sqlmodels import SiteGroupSQL, SiteSQL, UserSQL, ForecastValueSQL, ForecastSQL
from sqlalchemy.orm.session import Session
from typing import Optional

def make_site(db_session, ml_id=1):
    """Make a site.

    This is mainly used for testing purposes.
    """

    site = SiteSQL(
        client_site_id=1,
        latitude=51,
        longitude=3,
        capacity_kw=4,
        inverter_capacity_kw=4,
        module_capacity_kw=4.3,
        created_utc=datetime.now(timezone.utc),
        ml_id=ml_id,
    )
    db_session.add(site)
    db_session.commit()

    return site


def make_site_group(db_session, site_group_name="test_site_group"):
    """Make a site group.

    This is mainly used for testing purposes.
    """
    # create site group
    site_group = SiteGroupSQL(site_group_name=site_group_name)
    db_session.add(site_group)
    db_session.commit()

    return site_group


def make_user(db_session, email, site_group):
    """Make a user.

    This is mainly used for testing purposes.
    """
    # create a user
    user = UserSQL(email=email, site_group_uuid=site_group.site_group_uuid)
    db_session.add(user)
    db_session.commit()

    return user

# # create functions for site and user
# def create_new_site(
#     session: Session,
#     client_site_id: int,
#     client_site_name: str,
#     latitude: float,
#     longitude: float,
#     capacity_kw: float,
#     dno: Optional[str] = None,
#     gsp: Optional[str] = None,
#     region: Optional[str] = None,
#     orientation: Optional[float] = None,
#     tilt: Optional[float] = None,
#     inverter_capacity_kw: Optional[float] = None,
#     module_capacity_kw: Optional[float] = None,
# ) -> SiteSQL:
#     """Creates a site and adds it to the database.
#     This is used in the OCF Dashboard.
#     :param session: database session
#     :param client_site_id: id the client uses for the site
#     :param client_site_name: name the client uses for the site
#     :param latitude: latitude of site as an integer
#     :param longitude: longitude of site as an integer
#     :param capacity_kw: capacity of site in kw
#     :param dno: dno of site
#     :param gsp: gsp of site
#     :param region: region of site, deafut is uk
#     :param orientation: orientation of site, default is 180
#     :param tilt: tilt of site, default is 35
#     :param inverter_capacity_kw: inverter capacity of site in kw
#     :param module_capacity_kw: module capacity of site in kw

#     """
#     max_ml_id = session.query(func.max(SiteSQL.ml_id)).scalar()

#     if max_ml_id is None:
#         max_ml_id = 0

#     if region in [None, ""]:
#         region = "uk"

#     if orientation in [None, ""]:
#         orientation = 180

#     if tilt in [None, ""]:
#         tilt = 35

#     if inverter_capacity_kw in [None, ""]:
#         inverter_capacity_kw = capacity_kw

#     if module_capacity_kw in [None, ""]:
#         module_capacity_kw = capacity_kw

#     if gsp is None:
#         gsp = get_gsp(latitude=latitude, longitude=longitude)
#         gsp = json.dumps(gsp)

#     if dno is None:
#         dno = get_dno(latitude=latitude, longitude=longitude)
#         dno = json.dumps(dno)

#     site = SiteSQL(
#         ml_id=max_ml_id + 1,
#         client_site_id=client_site_id,
#         client_site_name=client_site_name,
#         latitude=latitude,
#         longitude=longitude,
#         capacity_kw=capacity_kw,
#         dno=dno,
#         gsp=gsp,
#         region=region,
#         orientation=orientation,
#         tilt=tilt,
#         inverter_capacity_kw=inverter_capacity_kw,
#         module_capacity_kw=module_capacity_kw,
#     )

#     session.add(site)

#     session.commit()

#     message = f"Site with client site id {site.client_site_id} and site uuid {site.site_uuid} created successfully"

#     return site, message


def create_user(
    session: Session,
    email: str,
    site_group_name: str,
) -> UserSQL:
    """Create a user.
    :param session: database session
    :param email: email of user being created
    :param site_group: name of the site group this user will be part of
    """

    site_group = (
        session.query(SiteGroupSQL)
        .filter(SiteGroupSQL.site_group_name == site_group_name)
        .first()
    )

    user = UserSQL(email=email, site_group_uuid=site_group.site_group_uuid)

    session.add(user)
    site_group.users.append(user)
    session.commit()

    return user

# delete functions for site, user, and site group
def delete_site(session: Session, site_uuid: str) -> SiteGroupSQL:
    """Delete a site group.
    :param session: database session
    :param site_uuid: unique identifier for site
    """
    site = session.query(SiteSQL).filter(SiteSQL.site_uuid == site_uuid).first()

    forecast_uuids = session.query(ForecastSQL.forecast_uuid).filter(ForecastSQL.site_uuid == site_uuid).all()

    forecast_uuids = [str(forecast_uuid[0]) for forecast_uuid in forecast_uuids]

    # get and delete all forecast values for site 
    stmt = sa.delete(ForecastValueSQL).where(ForecastValueSQL.forecast_uuid.in_(forecast_uuids))
    session.execute(stmt)

    stmt_2 = sa.delete(ForecastSQL).where(ForecastSQL.forecast_uuid.in_(forecast_uuids))
    session.execute(stmt_2)

    # we decided not to delete generation data for the site because it seems sensible to keep it for now

    session.delete(site)

    message = f"Site with site uuid {site.site_uuid} deleted successfully"

    session.commit()

    return message

# delete user
def delete_user(session: Session, email: str) -> UserSQL:
    """Delete a user.
    :param session: database session
    :param email: email of user being deleted
    """
    user = session.query(UserSQL).filter(UserSQL.email == email).first()

    session.delete(user)
    
    message = f"User with email {user.email} and site_group_uuid {user.site_group_uuid} deleted successfully"

    session.commit()

    return message

#delete site group
def delete_site_group(session: Session, site_group_name: str) -> SiteGroupSQL:
    """Delete a site group.
    :param session: database session
    :param site_group_name: name of site group being deleted
    """
    site_group = (
        session.query(SiteGroupSQL)
        .filter(SiteGroupSQL.site_group_name == site_group_name)
        .first()
    )

    site_group_users = site_group.users

    if len(site_group_users) > 0:
        message = f"Site group with name {site_group.site_group_name} and site group uuid {site_group.site_group_uuid} has users and cannot be deleted."
        return message
    
    session.delete(site_group)

    message = f"Site group with name {site_group.site_group_name} and site group uuid {site_group.site_group_uuid} deleted successfully."

    session.commit()

    return message