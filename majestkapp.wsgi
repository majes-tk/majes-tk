# Import sys and os for path manipulation
import sys, os

# Change into the SimpleOrder Install Directory so we find all imports and language files.
os.chdir('/opt/simpleorder')

# Add all files in the SimpleOrder install Directory to the path, just to make sure we find all files we need.
sys.path.insert(0, '/opt/simpleorder')

# import the flask app as application so wsgi can access and load it
from majestkapp import app as application

