# An example of a Flask app with a MongoDB backend
## Assumes that you have a MongoDB with the required data from BIOL61860 pre-loaded (loading script not included)

- Install requirements.txt
- Inside helper.py specify your database connection (currently set up for a local database)
- On Windows run_app.bat can be used to run the app (will be one 127.0.0.1:5000)
  - Otherwise in the terminal, in the same directory as the app, run `python -m flask run`
  - If you need auto reloading set the following environment variable `FLASK_ENV=development` (this is set for you if using the run_app.bat script)
