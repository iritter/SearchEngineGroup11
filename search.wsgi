import sys
import os

sys.path.insert(1, '/home/u089/py/flaskapp')

os.chdir('/home/u089/py/flaskapp')

from flaskapp import app 
application = app