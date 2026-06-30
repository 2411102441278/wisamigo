import pymysql

pymysql.install_as_MySQLdb()

# XAMPP bundles an older MariaDB (10.4.x) while modern Django assumes 10.5+.
# 10.4 works fine for this project, so we bypass the version gate...
from django.db.backends.base.base import BaseDatabaseWrapper
BaseDatabaseWrapper.check_database_version_supported = lambda self: None

# ...and disable the MariaDB 10.5+ "INSERT ... RETURNING" feature, which
# MariaDB 10.4 does not support.
from django.db.backends.mysql.features import DatabaseFeatures
DatabaseFeatures.can_return_columns_from_insert = False
DatabaseFeatures.can_return_rows_from_bulk_insert = False