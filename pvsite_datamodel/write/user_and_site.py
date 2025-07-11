""" Tools for making fake users and sites in the database."""

import json
import logging
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
    LocationAssetType,
    LocationGroupSQL,
    LocationSQL,
    UserSQL,
)
from pvsite_datamodel.write.data.dno import get_dno
from pvsite_datamodel.write.data.gsp import get_gsp

logger = logging.getLogger(__name__)


def make_fake_site(db_session, ml_id=1):
    """Make a site.

    This is mainly used for testing purposes.
    """

    site = LocationSQL(
        client_location_id=1,
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
    site_group = LocationGroupSQL(location_group_name=site_group_name)
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
    asset_type: Optional[str] = LocationAssetType.pv.name,
    orientation: Optional[float] = None,
    tilt: Optional[float] = None,
    inverter_capacity_kw: Optional[float] = None,
    module_capacity_kw: Optional[float] = None,
    client_uuid: Optional[UUID] = None,
    ml_id: Optional[int] = None,
    user_uuid: Optional[str] = None,
) -> [LocationSQL, str]:
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

    max_ml_id = session.query(func.max(LocationSQL.ml_id)).scalar()

    if max_ml_id is None:
        max_ml_id = 0

    if country in [None, ""]:
        country = "uk"

    # if region in [None, ""]:
    #     region = "uk"

    if asset_type not in LocationAssetType.__members__:
        raise ValueError(
            f"""Invalid asset_type. Received: {asset_type},
            but must one of ({', '.join(map(lambda type: type.name, LocationAssetType))})"""
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

    site = LocationSQL(
        ml_id=ml_id if ml_id else max_ml_id + 1,
        client_location_id=client_site_id,
        client_location_name=client_site_name,
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
        f"Site with client location id {site.client_location_id} "
        f"and location uuid {site.location_uuid} created successfully"
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
        session.query(LocationGroupSQL)
        .filter(LocationGroupSQL.location_group_name == site_group_name)
        .first()
    )

    user = UserSQL(email=email, location_group_uuid=site_group.location_group_uuid)

    session.add(user)
    site_group.users.append(user)
    session.commit()

    return user


# update functions for site and site group
def add_site_to_site_group(
    session: Session, site_uuid: str, site_group_name: str
) -> LocationGroupSQL:
    """Add a site to a site group.

    NB: Sites can belong to many site groups.
    :param session: database session
    :param site_uuid: uuid of site
    :param site_group_name: name of site group
    """
    site_group = (
        session.query(LocationGroupSQL)
        .filter(LocationGroupSQL.location_group_name == site_group_name)
        .first()
    )

    site = session.query(LocationSQL).filter(LocationSQL.location_uuid == site_uuid).one()

    if site not in site_group.locations:
        site_group.locations.append(site)

    session.commit()

    return site_group.locations


def remove_site_from_site_group(
    session: Session, site_uuid: str, site_group_name: str
) -> [LocationSQL]:
    """Remove a site to a site group.

    NB: Sites can belong to many site groups.
    :param session: database session
    :param site_uuid: uuid of site
    :param site_group_name: name of site group
    """
    site_group = (
        session.query(LocationGroupSQL)
        .filter(LocationGroupSQL.location_group_name == site_group_name)
        .first()
    )

    site = session.query(LocationSQL).filter(LocationSQL.location_uuid == site_uuid).one()

    if site in site_group.locations:
        new_sites = [site for site in site_group.locations if str(site.location_uuid) != site_uuid]
        site_group.locations = new_sites

    session.commit()

    return site_group.locations


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
    user_site_group = user.location_group.location_group_name
    user = user.email
    return user, user_site_group


def update_user_site_group(session: Session, email: str, site_group_name: str) -> UserSQL:
    """Change site group for user.

    :param session: database session
    :param email: email of user
    :param site_group_name: name of site group
    """
    site_group = (
        session.query(LocationGroupSQL)
        .filter(LocationGroupSQL.location_group_name == site_group_name)
        .first()
    )

    user = session.query(UserSQL).filter(UserSQL.email == email)

    user = user.update({"location_group_uuid": site_group.location_group_uuid})

    session.commit()

    return user


# update site metadata
def edit_site(
    session: Session, site_uuid: str, site_info: PVSiteEditMetadata, user_uuid: str = None
) -> Tuple[LocationSQL, str]:
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

    site = session.query(LocationSQL).filter(LocationSQL.location_uuid == site_uuid).first()

    update_data = site_info.model_dump(exclude_unset=True, exclude_none=False)

    if "client_site_name" in update_data:
        site.client_location_name = update_data.pop("client_site_name")
    if "client_site_id" in update_data:
        site.client_location_id = update_data.pop("client_site_id")

    # Update model class variable from requested fields
    for var, value in update_data.items():
        setattr(site, var, value)

    session.add(site)
    session.commit()
    session.refresh(site)

    message = f"Location with location uuid {site.location_uuid} updated successfully"

    return site, message


def set_site_to_inactive_if_not_in_site_group(
    session: Session, site_uuid: str, user_uuid: str, ignore_ocf_site_group: Optional[bool] = True
):
    """Set to inactive, if not in a site group.

    :param session: database session
    :param site_uuid: the site uuid
    :param user_uuid: the UUID of the user setting the site to inactive
    :param ignore_ocf_site_group: if True,
        ignore the "ocf" site group when checking if the site is in a site group
    """

    set_session_user(session, user_uuid)

    # get site
    site = session.query(LocationSQL).filter(LocationSQL.location_uuid == site_uuid).first()

    # check if site is in any other site group
    site_groups: [LocationGroupSQL] = site.location_groups
    if ignore_ocf_site_group:
        # only look at sites groups that are not called "ocf"
        site_groups = [sg for sg in site_groups if sg.location_group_name != "ocf"]

    logger.info(f"Site {site_uuid} is in {len(site_groups)} site groups.")

    if len(site_groups) == 0:
        logger.info(f"Site {site_uuid} is not in any site group, setting it to inactive.")

        site.active = False
        session.commit()


# delete functions for site, user, and site group
def delete_site(
    session: Session, site_uuid: str, user_uuid: Optional[str] = None
) -> LocationGroupSQL:
    """Delete a site group.

    :param session: database session
    :param site_uuid: unique identifier for site
    :param user_uuid: the UUID of the user deleting the site
    """
    set_session_user(session, user_uuid)

    site = session.query(LocationSQL).filter(LocationSQL.location_uuid == site_uuid).first()

    forecast_uuids = (
        session.query(ForecastSQL.forecast_uuid)
        .filter(ForecastSQL.location_uuid == site_uuid)
        .all()
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

    message = f"Location with location uuid {site.location_uuid} deleted successfully"

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
        f"User with email {user.email} and location_group_uuid "
        f"{user.location_group_uuid} deleted successfully"
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
        session.query(LocationGroupSQL)
        .filter(LocationGroupSQL.location_group_name == site_group_name)
        .first()
    )

    site_group_users = site_group.users

    if len(site_group_users) > 0:
        message = (
            f"Location group with name {site_group.location_group_name} and "
            f"location group uuid {site_group.location_group_uuid} has users and cannot be deleted."
        )
        return message

    session.delete(site_group)

    message = (
        f"Location group with name {site_group.location_group_name} "
        f"and location group uuid {site_group.location_group_uuid} deleted successfully."
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


def add_child_location_to_parent_location(
    session: Session, child_location_uuid: str, parent_location_uuid: str
) -> None:
    """Add a child location to a parent location.

    :param session: database session
    :param child_location_uuid: the UUID of the child location
    :param parent_location_uuid: the UUID of the parent location
    """
    child_location = get_site_by_uuid(session=session, site_uuid=child_location_uuid)
    parent_location = get_site_by_uuid(session=session, site_uuid=parent_location_uuid)

    if parent_location not in child_location.parent_locations:
        parent_location.child_locations.append(child_location)
        # note this also adds the parent to the child_location.parent_locations

    session.commit()
