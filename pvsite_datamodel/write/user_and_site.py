""" Tools for making fake users and sites in the database."""

import json
from datetime import datetime, timezone
from typing import Optional, Tuple
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.functions import func

from pvsite_datamodel.pydantic_models import PVSiteEditMetadata
from pvsite_datamodel.read import get_or_create_model, get_site_by_uuid, get_user_by_email
from pvsite_datamodel.sqlmodels import (
    ForecastSQL,
    ForecastValueSQL,
    SiteAssetType,
    SiteGroupSQL,
    SiteSQL,
    UserSQL,
)
from pvsite_datamodel.write.data.dno import get_dno
from pvsite_datamodel.write.data.gsp import get_gsp


def make_fake_site(db_session, ml_id=1):
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


def create_site_group(db_session, site_group_name="test_site_group"):
    """Make a site group.

    This is mainly used for testing purposes.
    """
    # create site group
    site_group = SiteGroupSQL(site_group_name=site_group_name)
    db_session.add(site_group)
    db_session.commit()

    return site_group


# make site
def create_site(
    session: Session,
    client_site_id: int,
    client_site_name: str,
    latitude: float,
    longitude: float,
    capacity_kw: float,
    dno: Optional[str] = None,
    gsp: Optional[str] = None,
    country: Optional[str] = "uk",
    region: Optional[str] = None,
    asset_type: Optional[str] = SiteAssetType.pv.name,
    orientation: Optional[float] = None,
    tilt: Optional[float] = None,
    inverter_capacity_kw: Optional[float] = None,
    module_capacity_kw: Optional[float] = None,
    client_uuid: Optional[UUID] = None,
    ml_id: Optional[int] = None,
    user_uuid: Optional[str] = None,
) -> [SiteSQL, str]:
    """
    Create a site and adds it to the database.

    :param session: database session
    :param client_site_id: id the client uses for the site
    :param client_site_name: name the client uses for the site
    :param latitude: latitude of site as an integer
    :param longitude: longitude of site as an integer
    :param capacity_kw: capacity of site in kw
    :param dno: dno of site
    :param gsp: gsp of site
    :param country: country of site, default is uk
    :param region: region of site
    :param asset_type: type of asset (accepts "pv" or "wind")
    :param orientation: orientation of site, default is 180
    :param tilt: tilt of site, default is 35
    :param inverter_capacity_kw: inverter capacity of site in kw
    :param module_capacity_kw: module capacity of site in kw
    :param ml_id: internal ML modelling id
    :param user_uuid: the UUID of the user creating the site

    """
    set_session_user(session, user_uuid)

    max_ml_id = session.query(func.max(SiteSQL.ml_id)).scalar()

    if max_ml_id is None:
        max_ml_id = 0

    if country in [None, ""]:
        country = "uk"

    # if region in [None, ""]:
    #     region = "uk"

    if asset_type not in SiteAssetType.__members__:
        raise ValueError(
            f"""Invalid asset_type. Received: {asset_type},
            but must one of ({', '.join(map(lambda type: type.name, SiteAssetType))})"""
        )

    if orientation in [None, ""]:
        orientation = 180

    if tilt in [None, ""]:
        tilt = 35

    if inverter_capacity_kw in [None, ""]:
        inverter_capacity_kw = capacity_kw

    if module_capacity_kw in [None, ""]:
        module_capacity_kw = capacity_kw

    if gsp is None:
        gsp = get_gsp(latitude=latitude, longitude=longitude)
        gsp = json.dumps(gsp)

    if dno is None:
        dno = get_dno(latitude=latitude, longitude=longitude)
        dno = json.dumps(dno)

    site = SiteSQL(
        ml_id=ml_id if ml_id else max_ml_id + 1,
        client_site_id=client_site_id,
        client_site_name=client_site_name,
        latitude=latitude,
        longitude=longitude,
        capacity_kw=capacity_kw,
        dno=dno,
        gsp=gsp,
        country=country,
        region=region,
        asset_type=asset_type,
        orientation=orientation,
        tilt=tilt,
        inverter_capacity_kw=inverter_capacity_kw,
        module_capacity_kw=module_capacity_kw,
        client_uuid=client_uuid,
    )

    session.add(site)

    session.commit()

    message = (
        f"Site with client site id {site.client_site_id} "
        f"and site uuid {site.site_uuid} created successfully"
    )

    return site, message


def create_user(
    session: Session,
    email: str,
    site_group_name: str,
) -> UserSQL:
    """Create a user.

    :param session: database session
    :param email: email of user being created
    :param site_group_name: name of the site group this user will be part of
    """

    site_group = (
        session.query(SiteGroupSQL).filter(SiteGroupSQL.site_group_name == site_group_name).first()
    )

    user = UserSQL(email=email, site_group_uuid=site_group.site_group_uuid)

    session.add(user)
    site_group.users.append(user)
    session.commit()

    return user


# update functions for site and site group
def add_site_to_site_group(session: Session, site_uuid: str, site_group_name: str) -> SiteGroupSQL:
    """Add a site to a site group.

    NB: Sites can belong to many site groups.
    :param session: database session
    :param site_uuid: uuid of site
    :param site_group_name: name of site group
    """
    site_group = (
        session.query(SiteGroupSQL).filter(SiteGroupSQL.site_group_name == site_group_name).first()
    )

    site = session.query(SiteSQL).filter(SiteSQL.site_uuid == site_uuid).one()

    if site not in site_group.sites:
        site_group.sites.append(site)

    session.commit()

    return site_group.sites


def remove_site_from_site_group(
    session: Session, site_uuid: str, site_group_name: str
) -> [SiteSQL]:
    """Remove a site to a site group.

    NB: Sites can belong to many site groups.
    :param session: database session
    :param site_uuid: uuid of site
    :param site_group_name: name of site group
    """
    site_group = (
        session.query(SiteGroupSQL).filter(SiteGroupSQL.site_group_name == site_group_name).first()
    )

    site = session.query(SiteSQL).filter(SiteSQL.site_uuid == site_uuid).one()

    if site in site_group.sites:
        new_sites = [site for site in site_group.sites if str(site.site_uuid) != site_uuid]
        site_group.sites = new_sites

    session.commit()

    return site_group.sites


# change site group for user
def change_user_site_group(session, email: str, site_group_name: str):
    """
    Change user to a specific site group name.

    :param session: the database session
    :param email: the email of the user
    :param site_group_name: the name of the site group
    """
    update_user_site_group(session=session, email=email, site_group_name=site_group_name)
    user = get_user_by_email(session=session, email=email)
    user_site_group = user.site_group.site_group_name
    user = user.email
    return user, user_site_group


def update_user_site_group(session: Session, email: str, site_group_name: str) -> UserSQL:
    """Change site group for user.

    :param session: database session
    :param email: email of user
    :param site_group_name: name of site group
    """
    site_group = (
        session.query(SiteGroupSQL).filter(SiteGroupSQL.site_group_name == site_group_name).first()
    )

    user = session.query(UserSQL).filter(UserSQL.email == email)

    user = user.update({"site_group_uuid": site_group.site_group_uuid})

    session.commit()

    return user


# update site metadata
def edit_site(
    session: Session, site_uuid: str, site_info: PVSiteEditMetadata, user_uuid: str = None
) -> Tuple[SiteSQL, str]:
    """
    Edit an existing site. Fill in only the fields that need to be updated.

    :param session: database session
    :param site_uuid: the existing site uuid
    :param site_info: metadata for editing the site, should be an instance of PVSiteEditMetadata
        - client_site_id: id the client uses for the site
        - client_site_name: name the client uses for the site
        - orientation: orientation of site
        - tilt: tilt of site
        - latitude: latitude of site as an integer
        - longitude: longitude of site as an integer
        - inverter_capacity_kw: inverter capacity of site in kw
        - module_capacity_kw: module capacity of site in kw
        - capacity_kw: capacity of site in kw
        - dno: dno of site
        - gsp: gsp of site
        - client_uuid: The UUID of the client this site belongs to
    :param user_uuid: the UUID of the user editing the site
    """
    set_session_user(session, user_uuid)

    site = session.query(SiteSQL).filter(SiteSQL.site_uuid == site_uuid).first()

    update_data = site_info.model_dump(exclude_unset=True, exclude_none=False)

    # Update model class variable from requested fields
    for var, value in update_data.items():
        setattr(site, var, value)

    session.add(site)
    session.commit()
    session.refresh(site)

    message = f"Site with site uuid {site.site_uuid} updated successfully"

    return site, message


# delete functions for site, user, and site group
def delete_site(session: Session, site_uuid: str, user_uuid: Optional[str] = None) -> SiteGroupSQL:
    """Delete a site group.

    :param session: database session
    :param site_uuid: unique identifier for site
    :param user_uuid: the UUID of the user deleting the site
    """
    set_session_user(session, user_uuid)

    site = session.query(SiteSQL).filter(SiteSQL.site_uuid == site_uuid).first()

    forecast_uuids = (
        session.query(ForecastSQL.forecast_uuid).filter(ForecastSQL.site_uuid == site_uuid).all()
    )

    forecast_uuids = [str(forecast_uuid[0]) for forecast_uuid in forecast_uuids]

    # get and delete all forecast values for site
    stmt = sa.delete(ForecastValueSQL).where(ForecastValueSQL.forecast_uuid.in_(forecast_uuids))
    session.execute(stmt)

    stmt_2 = sa.delete(ForecastSQL).where(ForecastSQL.forecast_uuid.in_(forecast_uuids))
    session.execute(stmt_2)

    # we decided not to delete generation data for the site
    # because it seems sensible to keep it for now

    session.delete(site)

    message = f"Site with site uuid {site.site_uuid} deleted successfully"

    session.commit()

    return message


# delete user
def delete_user(session: Session, email: str) -> str:
    """Delete a user.

    :param session: database session
    :param email: email of user being deleted
    """
    user = session.query(UserSQL).filter(UserSQL.email == email).first()

    session.delete(user)

    message = (
        f"User with email {user.email} and site_group_uuid "
        f"{user.site_group_uuid} deleted successfully"
    )

    session.commit()

    return message


# delete site group
def delete_site_group(session: Session, site_group_name: str) -> str:
    """Delete a site group.

    :param session: database session
    :param site_group_name: name of site group being deleted
    """
    site_group = (
        session.query(SiteGroupSQL).filter(SiteGroupSQL.site_group_name == site_group_name).first()
    )

    site_group_users = site_group.users

    if len(site_group_users) > 0:
        message = (
            f"Site group with name {site_group.site_group_name} and "
            f"site group uuid {site_group.site_group_uuid} has users and cannot be deleted."
        )
        return message

    session.delete(site_group)

    message = (
        f"Site group with name {site_group.site_group_name} "
        f"and site group uuid {site_group.site_group_uuid} deleted successfully."
    )

    session.commit()

    return message


def assign_model_name_to_site(session: Session, site_uuid, model_name):
    """Assign model to site.

    :param session: database session
    :param site_uuid: site uuid
    :param model_name: name of the model
    """

    site = get_site_by_uuid(session=session, site_uuid=site_uuid)

    model = get_or_create_model(session=session, name=model_name)

    site.ml_model_uuid = model.model_uuid
    session.commit()


def set_session_user(session: Session, user_uuid: str):
    """Set user session variable.

    Sets a variable which is then used by the log_site_changes function when updating
    the site history table.

    :param session: the session
    :param user_uuid: the user UUID
    """
    if user_uuid is not None:
        session.execute(text(f"SET pvsite_datamodel.current_user_uuid = '{user_uuid}'"))
    else:
        session.execute(text("RESET pvsite_datamodel.current_user_uuid"))
