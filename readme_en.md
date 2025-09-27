# Installation & Run

## Prerequisites
- Python 3.10+
- MySQL 8+ installed and accessible

## 1) Create and activate a virtual environment

- Anaconda/Miniconda (optional)
  ```bash
  conda create -n cityu python=3.10 -y
  conda activate cityu
  ```

## 2) Install dependencies
```bash
pip install -r requirements.txt
```

## 3) Initialize the database

Assuming MySQL CLI is installed locally

```bash
cd test_db  # go to the test_db directory
mysql -h 127.0.0.1 -P 3306 -u root < employees.sql  # import base data
```

## 4) Start the service
```bash
uvicorn main:app --reload
```

## 5) Access
- http://127.0.0.1:8000/docs (view all defined APIs)

# Project Structure
- main.py: Application entry point, registers routers and middleware, defines startup/shutdown events and a root health check
- app/router/: API layer (HTTP)
  - employee.py: Sample endpoints (department-related)
  - executor.py: SQL execution endpoints (call the DB layer)
- app/db/: Data access layer (DB connection and SQL execution)
  - init.py: DB connection config and engine
  - employee.py: Sample query/response
  - executor.py: Execute incoming SQL, return result rows or affected row count
- requirements.txt: Dependencies
- readme.md: Usage guide

Request flow (diagram)
Client → app/router → app/db → MySQL → app/router → Client

### Code organization

Typically, organize code by feature. Create corresponding folders/files under router and db, and keep each module’s logic focused.

For example, both router and db have an employee.py for employee-related logic. If you want to handle department-related logic, create a new department.py instead of mixing code together.

### app/router API layer

Wrap business logic as HTTP APIs. Usually just add a thin wrapper: accept parameters and call the data access layer.

### app/db data access layer

Implement main data logic here. Accept parameters from the API layer, build SQL to operate the database, get results and assemble data for the frontend.