import os

from iotdb.Session import Session


# ip = "85.215.224.213"
ip = os.environ["IOTDB_HOST"]
new_password = os.environ["IOTDB_PASSWORD"]

port_ = "6667"
username_ = 'root'
password_ = 'root'

print("Prepare Session...")
session = Session(ip, port_, user=username_, password=password_)

print("Open Session...")
session.open(False)

result = session.execute_non_query_statement(f"ALTER USER root SET PASSWORD '{new_password}';")

if result == -1:
    raise RuntimeError("...")

print(f"Result: {result}")

print("Closing Session...")
session.close()
