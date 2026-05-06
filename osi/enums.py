"""OSI enumerations: Dialect and Vendor."""
from enum import Enum


class Dialect(str, Enum):
    ANSI_SQL = "ANSI_SQL"
    SNOWFLAKE = "SNOWFLAKE"
    MDX = "MDX"
    TABLEAU = "TABLEAU"
    DATABRICKS = "DATABRICKS"


class Vendor(str, Enum):
    COMMON = "COMMON"
    SNOWFLAKE = "SNOWFLAKE"
    SALESFORCE = "SALESFORCE"
    DBT = "DBT"
    DATABRICKS = "DATABRICKS"
