# to run the server
python3 -m uvicorn app.main:app --reload
# syntax:
# -m = run a module, not a file
# app.main:app = import the module app.main(the file app/main.py) and take the variable app from it
# --reload = restart the server when files change(development only)

# Start venv - virtual environment
# go to backend folder first, where .venv folder is
source .venv/bin/activate

# Test with pytest
python3 -m pytest -v
# sytnax:
# -m pytest = run module pytest, not the command
# -v = verbose - full description wiht each line to each test



