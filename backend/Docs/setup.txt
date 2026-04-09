step 1 -> Create the folder architecture
step 2 -> Create the requirement.txt file
step 3 -> Modify the requirement.txt file with required dependency and version.
step 4 -> Create the venv file "python -m venv .venv" (python verion "3.12.7")
step 5 -> Enable  the .venv ".venv/Scripts/activate"
step 6 -> pip install -r requirement.txt
step 7 -> write the server file in service/main.py
step 8 -> check health
step 9 -> Setup Common DB for each service
step 10 -> Create the core/db.py file and setup engine and session
step 11 -> Create database.py file and write the dependency ingestion for the fastAPI
step 12 -> alembic init alembic in service then 
"
from core.db import Base 
from models.employee import Employee
target_metadata = Base.metadata
connectable = engine
"
step 13 -> Create api, service, repo and model layer.
step 14 -> Check Database Connectivity.
step 14 -> Run "alembic -c apps/employeeService/alembic.ini revision --autogenerate -m "create auth table"".
step 15 -> create custom JSON_Serialiser and customResponse