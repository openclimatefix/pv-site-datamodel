"""Python SDK for reading/writing to/from pvsite database."""

from .connection import DatabaseConnection
from .read.site import (
    get_all_client_site_ids,
)
from .write.site_group import (
    add_all_sites_to_site_group,
    change_user_site_group,
    update_site_group,
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

__all__ = [
    "DatabaseConnection",
    "get_all_client_site_ids",
    "add_all_sites_to_site_group",
    "change_user_site_group",
    "update_site_group",
    "APIRequestSQL",
    "ClientSQL",
    "ForecastSQL",
    "ForecastValueSQL",
    "GenerationSQL",
    "InverterSQL",
    "LocationGroupSQL",
    "LocationSQL",
    "StatusSQL",
    "UserSQL",
]
