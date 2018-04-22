############################################################################### 
# Convert an Ipdr-Xdr file into a python representation
############################################################################### 

import sys
from IpdrXdrDocumentClasses import *

def mypprint(s):
    indent = 0
    max_indent=15
    new_s = ''
    a_new_line=False
    for c in s:
      if c == '\t' or c=='\n':
        continue
      if c == ' ' and a_new_line:
        continue
      a_new_line=False
      if c == ')'  or c==']':
        indent -= 2
        if indent < (max_indent-2):
            new_s += '\n' + ' '*indent
      new_s += c
      if c == '(' or c=='[':
        indent += 2
        if indent < max_indent:
            new_s += '\n' + ' '*indent
      if c == ',':
        if indent < max_indent:
            new_s += '\n' + ' '*indent
            a_new_line=True
    return new_s

with open(sys.argv[1],"rb") as filep:
    ipdr=IPDRDoc.load(filep)    
    

with open(sys.argv[1],"rb") as filep:
    ipdr=None
    ipdr=IPDRDoc.load(filep)    
    repr_file = "%s.repr" % sys.argv[1]
    print "Decoding IPDR-XDR file \"%s\" to a file containing the python representation: %s" % (sys.argv[1],repr_file) 
    with open(repr_file,"w") as outp:
        outp.write(mypprint(str(ipdr)))

