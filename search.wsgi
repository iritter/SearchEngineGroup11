import sys
import os

sys.path.insert(1, '/home/user089/py/flaskapp')

os.chdir('/home/user089/py/flaskapp')

from flaskapp import app 
application = app