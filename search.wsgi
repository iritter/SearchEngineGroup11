import sys
import os

sys.path.insert(1, '/home/u089/py')

os.chdir('/home/u089/py')

from flaskapp import app 
application = app