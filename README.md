## Environment requirements

Used Python version `3.12.2`



## Simple build and run

Scripts `run_app.cmd` and `run_app.sh` are written for Windows and Linux/Mac respectively.
The scripts do:
- Virtual environment creation (if not already present)
- Virtual environment activation
- Installation of dependencies
- Compilation into bytecode
- Run the application

The script will not package the application for distribution.

## Tools Used

Primary tools used are Flask and SQLAlchemy for building the REST API and interaction with the in-memory sqlite database. Postman is used for testing the API.