import sys
from IpdrDoc import *

with open(sys.argv[1],"rb") as filep:
    ipdr=None
    ipdr=IPDRDoc.load(filep)    
    with open("%s.xdr" % sys.argv[1],"wb") as outp:
        outp.write(ipdr.pack())
