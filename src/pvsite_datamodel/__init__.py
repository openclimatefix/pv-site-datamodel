"""Python SDK for reading/writing to/from pvsite database."""

from .connection import DatabaseConnection
from .management import (
    add_all_sites_to_site_group,
    change_user_site_group,
    get_all_client_site_ids,
    get_all_site_uuids,
    select_site_by_client_id,
    select_site_by_uuid,
    update_site_group,
    validate_email,
)
from .sqlmodels import (
    APIRequestSQL,
    ClientSQL,
    ForecastSQL,
    ForecastValueSQL,
    GenerationSQL,
    InverterSQL,
    LocationGroupSQL,
    LocationSQL,
    StatusSQL,
    UserSQL,
)

__version__ = "1.2.3"
