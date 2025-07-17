"""Utils for GSP and DNO."""

try:
    import pyproj
except ImportError:
    print("You might want to install pyproj")  # noqa

# OSGB is also called "OSGB 1936 / British National Grid -- United
# Kingdom Ordnance Survey".  OSGB is used in many UK electricity
# system maps, and is used by the UK Met Office UKV model.  OSGB is a
# Transverse Mercator projection, using 'easting' and 'northing'
# coordinates which are in meters.  See https://epsg.io/27700

# WGS84 is short for "World Geodetic System 1984", used in GPS. Uses
# latitude and longitude.

OSGB = 27700
WGS84 = 4326
WGS84_CRS = f"EPSG:{WGS84}"


def lat_lon_to_osgb(lat: float, lon: float) -> [float, float]:
    """Change lat, lon to a OSGB coordinates.

    lat: latitude
    lon: longitude

    Return: 2-tuple of x (east-west), y (north-south).

    """
    return transformers.lat_lon_to_osgb.transform(lat, lon)


class Transformers:
    """Class to store transformation from one Grid to another.

    Its good to make this only once, but need the
    option of updating them, due to out of data grids.
    """

    def __init__(self) -> None:
        """Init."""
        self._osgb_to_lat_lon = None
        self._lat_lon_to_osgb = None
        self._osgb_to_geostationary = None
        self.make_transformers()

    def make_transformers(self) -> None:
        """Make transformers.

        Nice to only make these once, as it makes calling the functions below quicker
        """
        self._lat_lon_to_osgb = pyproj.Transformer.from_crs(crs_from=WGS84, crs_to=OSGB)

    @property
    def lat_lon_to_osgb(self):
        """lat-lon to OSGB property."""
        return self._lat_lon_to_osgb


transformers = Transformers()
