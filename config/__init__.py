import pymysql

# Django talks to MySQL through the "MySQLdb" module. PyMySQL is a pure-Python
# driver that installs without compiling C code (easier on Windows and Vercel),
# so we register it under the MySQLdb name.
pymysql.install_as_MySQLdb()
