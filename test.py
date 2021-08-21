import os

from iotdb.Session import Session


ip = "85.215.224.213"
port_ = "6667"
username_ = 'root'
password_ = 'b82a11e6-60e0-451a-b6d8-4f64b7c26f38'

print("Prepare Session...")
session = Session(ip, port_, user=username_, password=password_)

print("Open Session...")
session.open(False)

result = session.execute_query_statement(f"LIST USER").todf()

print(f"Result: {result}")

print("Closing Session...")
session.close()
