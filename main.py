import asmd
import mannc
import sys

try:
    mannc.mannc( sys.argv[1] )
except asmd.ManncError as err:
    print(err)
