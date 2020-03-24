import pymysql
from libs.orm import patch_orm

# Monkey Patch
pymysql.install_as_MySQLdb()
patch_orm()
