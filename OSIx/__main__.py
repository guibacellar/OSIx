"""Main Executor for python -m OSIx."""

import sys
import os
import uvicorn

class WebApp:
    pass


# If we are running from a wheel, add the wheel to sys.path
if __package__ == "OSIx":

    # __file__ is OSIx/__main__.py
    # first dirname call strips of '/__main__.py'
    # Resulting path is the name of the wheel itself
    # Add that to sys.path so we can import pip
    path = os.path.dirname(__file__)
    sys.path.insert(0, path)
    os.chdir(os.path.dirname(__file__))


if __name__ == "__main__":
    # TODO: Ensure data folder

    # Run the uvicorn
    uvicorn.run("OSIxApi:app", host="127.0.0.1", port=5000, log_level="debug")
