import os

from iotdb.Session import Session


ip = "85.215.237.118"
port_ = "6667"
username_ = 'root'
password_ = '607dd864-dd0e-4c08-9df9-2bb1796916d4'

print("Prepare Session...")
session = Session(ip, port_, user=username_, password=password_)

print("Open Session...")
session.open(False)

result = session.execute_query_statement(f"LIST USER").todf()

print(f"Result: {result}")

print("Closing Session...")
session.close()
