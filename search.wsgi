import sys
import os

sys.path.insert(1, '/home/u089/SearchEngineGroup11')

os.chdir('/home/u089/SearchEngineGroup11')

from SearchEngineGroup11.flaskapp import app 
application = app