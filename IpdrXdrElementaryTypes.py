############################################################################### 
# This section contains the Elementary Types, 
# As defined in the TM Forum document: IPDR-XDR_Encoding_Format.pdf
# Note that unlike the python "xdrlib" module
# the TM Forum XDR format does not zero pad.
############################################################################### 

import os,re,datetime,time,struct
import ipaddress,uuid,binascii
import StringIO


# Most Ipdr datatypes can be represented as long, the few exceptions are string based.
class IpdrNumericalBaseType(long):
    ipdr_type="Undefined"
    type_id=0 
    packed_size=-1
    unpack_str='!?'
    def __init__(self,val=0):
        super(IpdrNumericalBaseType,self).__init__(val)
    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__,int(self))
    @classmethod
    def from_bytes(cls,val):
        return cls(struct.unpack(cls.unpack_str,val[0:cls.packed_size])[0])
    @classmethod
    def load(cls,filep):
        return cls(struct.unpack(cls.unpack_str,filep.read(cls.packed_size))[0])
    def pack(self):
        return struct.pack(self.unpack_str, self) 
    def to_xml(self): return str(self)
    
class IpdrString(str):
    ipdr_type="string"
    type_id=0x00000028
    packed_size=-1
    unpack_str='' # filled in later
    def __init__(self,val=""):
        super(IpdrString,self).__init__(val)
        self.unpack_str="!L%ds" % len(self)
        self.packed_size=4+len(val)
    def __repr__(self):
        return "%s('%s')" % (self.__class__.__name__,str(self))
    @classmethod
    def from_bytes(cls,val):
        length=struct.unpack("!L",(val[0:4]))[0]
        return cls(struct.unpack("%ds" % length,val[4:(4+length)])[0])
    @classmethod
    def load(cls,filep):
        length=struct.unpack("!L",filep.read(4))[0]
        return cls(struct.unpack("%ds" % length,filep.read(length))[0])
    def pack(self):
        #return struct.pack(self.unpack_str, self.packed_size-4,self) 
        return struct.pack(self.unpack_str, len(self),self) 
    def to_xml(self): return str(self)
        
class IpdrBool(IpdrNumericalBaseType):
    ipdr_type="boolean"
    type_id=0x00000029
    packed_size=1
    unpack_str='!?'
    def __init__(self,val=None):
        if isinstance(val,str):
            if val.lower() == "true" or val=="1":
                val=1
            elif val.lower() == "false" or val=="0":
                val=0
        super(IpdrBool,self).__init__(val)
    def __str__(self):
        if self == 0:
            return "false"
        else:
            return "true"
            
class IpdrUByte(IpdrNumericalBaseType):
    ipdr_type="unsignedbyte"
    type_id=0x0000002b
    packed_size=1
    unpack_str='!B'
    
class IpdrByte(IpdrNumericalBaseType):
    ipdr_type="byte"
    type_id=0x0000002a
    packed_size=1
    unpack_str='!b'

class IpdrUShort(IpdrNumericalBaseType):
    ipdr_type="unsignedShort"
    type_id=0x0000002d
    packed_size=2
    unpack_str='!H'

class IpdrShort(IpdrNumericalBaseType):
    ipdr_type="short"
    type_id=0x0000002c
    packed_size=2
    unpack_str='!h'

class IpdrUInt(IpdrNumericalBaseType):
    ipdr_type="unsignedInt"
    type_id=0x00000022
    packed_size=4
    unpack_str='!L'
    
class IpdrInt(IpdrNumericalBaseType):
    ipdr_type="int"
    type_id=0x00000021
    packed_size=4
    unpack_str='!l'
        
class IpdrULong(IpdrNumericalBaseType):
    ipdr_type="unsignedLong"
    type_id=0x00000024 
    packed_size=8
    unpack_str='!Q'

class IpdrLong(IpdrNumericalBaseType):
    ipdr_type="long"
    type_id=0x00000023 
    packed_size=8
    unpack_str='!q'


class IpdrFloat(float):
    ipdr_type="float"
    type_id=0x00000025
    packed_size=4
    unpack_str='!f'
    def __init__(self,val=0):
        super(IpdrFloat,self).__init__(val)
    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__,float(self))
    @classmethod
    def from_bytes(cls,val):
        return cls(struct.unpack(cls.unpack_str,val[0:cls.packed_size])[0])
    @classmethod
    def load(cls,filep):
        return cls(struct.unpack(cls.unpack_str,filep.read(cls.packed_size))[0])
    def pack(self):
        return struct.pack(self.unpack_str, self) 
    def to_xml(self): return str(self)

class IpdrDouble(IpdrFloat):
    ipdr_type="double"
    type_id=0x00000026
    packed_size=8
    unpack_str='!d'

class IpdrDateTimeMsec(IpdrNumericalBaseType):
    packed_size=8
    unpack_str='!Q'
    ipdr_type="ipdr:dateTimeMsec"
    type_id=0x00000224
    sec_granularity=1000
    def __init__(self,val):
        if isinstance(val,str):
            self=IpdrDateTimeMsec.from_str(val)
        else:
            super(IpdrDateTimeMsec,self).__init__(val)
    def to_datetime(self):
        d1=datetime.datetime.utcfromtimestamp(self/self.sec_granularity)
        microsecs=0
        if self.sec_granularity > 1:
            microsecs=(self % self.sec_granularity) * (1000000/self.sec_granularity)
        return datetime.datetime(d1.year,d1.month,d1.day,d1.hour,d1.minute,d1.second,microsecs)
    @classmethod
    def from_datetime(cls,d1):
        return cls(int((d1-datetime.datetime(1970,1,1)).total_seconds()*cls.sec_granularity))
    def __str__(self):
        s=str(self.to_datetime())
        dt, _, usec= s.partition(".")
        if self.sec_granularity==1:
            return dt
        elif self.sec_granularity==1000:
            usec =  "{0:<03s}".format(usec[0:3])
        elif self.sec_granularity==1000000:
            usec =  "{0:<06s}".format(usec[0:6])
        return "%s.%s" % (dt,usec)
    @classmethod
    def from_str(cls,s):
        dt, _, usec= s.partition(".")
        dt= datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        if len(usec) > 0:
            usec =  "{0:<06s}".format(usec.rstrip("Z")) # use format to ensure RHS zero-padded
            usec= int(usec, 10)
            dt+= datetime.timedelta(microseconds=usec)
        return cls.from_datetime(dt)    
    def to_xml(self): return str(self)
    def __repr__(self):
        return "%s.from_str('%s')" % (self.__class__.__name__,str(self))

class IpdrDateTimeUsec(IpdrDateTimeMsec):
    packed_size=8
    unpack_str='!Q'
    ipdr_type="ipdr:dateTimeUsec"
    type_id=0x00000623
    sec_granularity=1000000
    
class IpdrDateTime(IpdrDateTimeMsec):
    packed_size=4
    unpack_str='!L'
    ipdr_type="dateTime"
    type_id=0x00000122
    sec_granularity=1

class IpdrIpv4Addr(ipaddress.IPv4Address):
    ipdr_type="ipdr:ipV4Addr"
    type_id=0x00000322
    packed_size=4
    unpack_str='!L'
    def __init__(self,val=""):
        if isinstance(val,str):
            val=unicode(val)
        super(IpdrIpv4Addr,self).__init__(val)
    def __repr__(self):
        return "%s('%s')" % (self.__class__.__name__,str(self))
    @classmethod
    def from_bytes(cls,val):
        return cls(ipaddress.ip_address(struct.unpack(cls.unpack_str, val[0:cls.packed_size])[0]))
    @classmethod
    def load(cls,filep):
        return cls(ipaddress.ip_address(struct.unpack(cls.unpack_str, filep.read(cls.packed_size))[0]))
    def pack(self):
        return self.packed
    def to_xml(self): return str(self)

class IpdrIpv6Addr(ipaddress.IPv6Address):
    ipdr_type="ipdr:ipV6Addr"
    type_id=0x00000427
    packed_size=20
    unpack_str='4x16s'
    def __init__(self,val=""):
        if isinstance(val,str):
            val=unicode(val)
        super(IpdrIpv6Addr,self).__init__(val)
    def __repr__(self):
        return "%s('%s')" % (self.__class__.__name__,str(self))
    @classmethod
    def from_bytes(cls,val):
        return cls(ipaddress.IPv6Address(struct.unpack(cls.unpack_str, val[0:cls.packed_size])[0]))
    @classmethod
    def load(cls,filep):
        return cls(ipaddress.IPv6Address(struct.unpack(cls.unpack_str, filep.read(cls.packed_size))[0]))
    def pack(self):
        return struct.pack("4x")+self.packed
    def to_xml(self): return str(self)

# The standard allows for a generic IpAddress datatype. 
# This IpdrIpAddr has to be a wrapper class for IpdrIpv4Addr and IpdrIpv6Addr.
class IpdrIpAddr(object):
    ipdr_type="ipdr:ipAddr"
    type_id=0x00000827
    packed_size=-1
    unpack_str=''
    def __init__(self,val=""):
        if isinstance(val,str):
            val=unicode(val)
        self.__ipaddress=ipaddress.ip_address(val)
        if isinstance(self.__ipaddress,ipaddress.IPv4Address):
            self.packed_size=8
            self.unpack_str='!4xL'
        elif isinstance(self.__ipaddress,ipaddress.IPv6Address):
            self.packed_size=20
            self.unpack_str='4x16s'
    def __str__(self):
        return str(self.__ipaddress)
    def __int__(self):
        return int(self.__ipaddress)
    def __repr__(self):
        return "%s('%s')" % (self.__class__.__name__,str(self.__ipaddress))
    @classmethod
    def from_bytes(cls,val):
        length=struct.unpack("!L",val[0:4])[0]
        if length==4:
            local_unpack_str='!L'
        else:
            local_unpack_str="!%ds" % length
        assert(length <= len(val)+4)
        return cls(ipaddress.ip_address(struct.unpack(local_unpack_str, val[4:(length+4)])[0]))
    @classmethod
    def load(cls,filep):
        length=struct.unpack("!L",filep.read(4))[0]
        if length==4:
            local_unpack_str='!L'
        else:
            local_unpack_str="!%ds" % length
        return cls(ipaddress.ip_address(struct.unpack(local_unpack_str, filep.read(length))[0]))
    def pack(self):
        b=self.__ipaddress.packed
        return struct.pack("!L",len(b)) + b
    def to_xml(self): return str(self)
       
class IpdrUuid(uuid.UUID):
    ipdr_type="ipdr:uuid"
    type_id=0x00000527
    packed_size=20
    unpack_str='4x16s'
    def __repr__(self):
        return "%s('%s')" % (self.__class__.__name__,str(self))
    @classmethod
    def from_bytes(cls,val):
        return cls(str(uuid.UUID(bytes=struct.unpack(cls.unpack_str, val[0:cls.packed_size])[0])))
    @classmethod
    def load(cls,filep):
        return cls(str(uuid.UUID(bytes=struct.unpack(cls.unpack_str, filep.read(cls.packed_size))[0])))
    def pack(self):
        return struct.pack("!L",16)+self.bytes
    def to_xml(self): return str(self)

class IpdrMacAddr(str):
    ipdr_type="ipdr:macAddress"
    type_id=0x00000723
    packed_size=8
    unpack_str="!Q"
    def __init__(self,val=0):
        if isinstance(val,long) or isinstance(val,int):
            val="%02X:%02X:%02X:%02X:%02X:%02X" % struct.unpack("xxBBBBBB",struct.pack("!Q",val)) 
        val=val.upper()
        assert(len(val)==17)
        super(IpdrMacAddr,self).__init__(val)
    def __int__(self):
        return long(self.replace(":",""),16)
    def __repr__(self):
        return "%s('%s')" % (self.__class__.__name__,str(self))
    @classmethod
    def from_bytes(cls,val):
        return cls("%02X:%02X:%02X:%02X:%02X:%02X" % struct.unpack("xxBBBBBB",val[0:cls.packed_size]))
    @classmethod
    def load(cls,filep):
        return cls("%02X:%02X:%02X:%02X:%02X:%02X" % struct.unpack("xxBBBBBB",filep.read(cls.packed_size)))
    def pack(self):
        return struct.pack("!Q",int(self))
    def to_xml(self): return str(self)

class IpdrHexBinary(str):
    ipdr_type="hexBinary"
    type_id=0x00000027
    packed_size=-1
    unpack_str=""
    def __init__(self,val=""):
        super(IpdrHexBinary,self).__init__(val)
        self.packed_size=4+-(-len(self)//2) # double negatives for ceiling division, because // is floor division
    def __repr__(self):
        return "%s('%s')" % (self.__class__.__name__,str(self))
    @classmethod
    def from_bytes(cls,val):
        length=struct.unpack("!L",(val[0:4]))[0]
        assert(length <= len(val)+4)
        return cls(binascii.hexlify(val[4:(4+length)]))
    @classmethod
    def load(cls,filep):
        length=struct.unpack("!L",filep.read(4))[0]
        return cls(binascii.hexlify(filep.read(length)))
    def pack(self):
        in_bytes=binascii.unhexlify(self)
        length=len(in_bytes)
        return (struct.pack("!L",length)+in_bytes)
    def to_xml(self): return str(self)
    
ipdr_classes=[
    IpdrString, 
    IpdrBool, 
    IpdrUByte, 
    IpdrByte, 
    IpdrUShort, 
    IpdrShort, 
    IpdrUInt, 
    IpdrInt, 
    IpdrULong, 
    IpdrLong, 
    IpdrFloat, 
    IpdrDouble, 
    IpdrDateTimeMsec, 
    IpdrDateTimeUsec, 
    IpdrDateTime, 
    IpdrIpv4Addr, 
    IpdrIpv6Addr, 
    IpdrIpAddr, 
    IpdrUuid, 
    IpdrMacAddr, 
    IpdrHexBinary
]
ipdr_class_from_type_id={cls.type_id:cls for cls in ipdr_classes}

class IpdrArray(list):
    length=0
    def __init__(self,types,length=None,array=[]):
        self.cls=types
        if length is None:
            length = len(array)
        self.length = IpdrInt(length)
        # tbd map kwargs to cls.
        super(IpdrArray,self).__init__(array)
    def load(self,filep):
        self.length = IpdrInt.load(filep)
        i=1
        while(i<=self.length or self.length < 0):
            obj=self.cls.load(filep)
            self.append(obj)
            i+=1
            # A semi-standard is to use length==0xffffffff to signify an unlimited array-size
            # Additionally, RFC1832 can be mis-read to indicate that length value greater than
            # what is presented should still be digested.
            # For this reason we check for EOF after consuming each element,
            # if stream is a pipe, this should be modified.
            if isinstance(filep,StringIO.StringIO):
                # StringIO has no "fileno" method.
                if filep.tell() == filep.len:
                    break
            elif filep.tell() == os.fstat(filep.fileno()).st_size:
                    break
            
        return self 
    def pack(self):
        out=self.length.pack() 
        for x in self:
            out+= x.pack()
        return out
        
    def __repr__(self):
        return "%s(types=%s,length=%s,array=%s)" % (self.__class__.__name__, self.cls.__name__,self.length, super(IpdrArray,self).__repr__())
        
    def __str__(self):
        return (super(IpdrArray,self).__repr__())
    
    def to_xml(self):
        return "<array length=\"%s\">%s</array>" % (self.length,"".join([x.to_xml() for x in self]))

class IpdrElementTypeEnum(IpdrInt):
    RECORDDESC = 1
    IPDRREC = 2
    DOCEND = 3
    enum= {
        1 : 'RECORDDESC',
        2 : 'IPDRREC',
        3 : 'DOCEND'
    }
    ipdr_type='ElementType'
    element_type="UNDEFINED"
    def __init__(self,val=1):
        self.element_type=self.enum[val]
        super(IpdrElementTypeEnum,self).__init__(val)
    def __str__(self):
        return self.element_type
    to_xml = __str__
    @classmethod
    def __contains__(cls,val):
        return (val in cls.enum.keys()) or (val in cls.enum.values())
    @classmethod
    def ElementType(cls,num):
        return cls.enum[num]
    
def test():
    # test DateTime classes
    assert(IpdrDateTimeMsec(1520388001039)==IpdrDateTimeMsec.from_datetime(IpdrDateTimeMsec(1520388001039).to_datetime()))
    assert(IpdrDateTimeMsec(1520388001039)==IpdrDateTimeMsec.from_str(str(IpdrDateTimeMsec(1520388001039))))
    assert(int(IpdrDateTimeMsec(1520388001039))==1520388001039)
    assert(IpdrDateTimeMsec(1520388001039)==IpdrDateTimeMsec.from_bytes(IpdrDateTimeMsec(1520388001039).pack()))
    assert(str(IpdrDateTimeMsec(1))=='1970-01-01 00:00:00.001')
    assert(str(IpdrDateTimeUsec(1))=='1970-01-01 00:00:00.000001')
    assert(str(IpdrDateTime(1))=='1970-01-01 00:00:01')
    # Test IpAddr classes
    assert(int(IpdrIpv4Addr('254.253.252.251'))==4278058235)
    assert(int(IpdrIpAddr('254.253.252.251'))==4278058235)
    assert(str(IpdrIpv4Addr.from_bytes(struct.pack("!L",4278058235)))=='254.253.252.251')
    assert(str(IpdrIpAddr.from_bytes(struct.pack("!LL",4,4278058235)))=='254.253.252.251')
    assert(IpdrIpAddr('ff:fe:fd:fc:fb:fa::1').pack().encode("hex") == '0000001000ff00fe00fd00fc00fb00fa00000001')
    assert(IpdrIpv6Addr('ff:fe:fd:fc:fb:fa::1').pack().encode("hex") == '0000000000ff00fe00fd00fc00fb00fa00000001')
    assert(IpdrIpv6Addr.from_bytes(IpdrIpv6Addr('ff:fe:fd:fc:fb:fa::1').pack())==IpdrIpv6Addr('ff:fe:fd:fc:fb:fa::1'))
    assert(int(IpdrUuid('12345678-1234-5678-1234-567812345678'))==24197857161011715162171839636988778104)
    assert(int(IpdrUuid(bytes=IpdrUuid('12345678-1234-5678-1234-567812345678').pack()[4:]))==24197857161011715162171839636988778104)
    # IpdrMacAddr classes
    assert(int(IpdrMacAddr('FF:FE:FD:FC:FB:FA'))==281470647991290)
    assert(int(IpdrMacAddr.from_bytes(IpdrMacAddr('FF:FE:FD:FC:FB:FA').pack()))==281470647991290)
    # hexBinary and String Classes
    assert(str(IpdrHexBinary.from_bytes('\x00\x00\x00\x02\xFF\x00'))=='ff00')
    assert(IpdrHexBinary('6142634465').pack()=='\x00\x00\x00\x05aBcDe')
    assert(IpdrString("12345").pack()=='\x00\x00\x00\x0512345')
    assert(str(IpdrString.from_bytes(IpdrHexBinary('6142634465').pack()))=='aBcDe')
    # Int and UInt
    assert(IpdrInt(-1).pack()=='\xff\xff\xff\xff')
    assert(IpdrUInt(4294967295).pack()=='\xff\xff\xff\xff')
    assert(int(IpdrUInt.from_bytes('\xff\xff\xff\xff'))==4294967295)
    assert(int(IpdrInt.from_bytes('\xff\xff\xff\xff'))==-1)
    # Long and ULong
    assert(int(IpdrULong.from_bytes('\xff\xff\xff\xff\xff\xff\xff\xff'))==18446744073709551615)
    assert(int(IpdrLong.from_bytes('\xff\xff\xff\xff\xff\xff\xff\xff'))==-1)
    assert(IpdrULong(18446744073709551615).pack()=='\xff\xff\xff\xff\xff\xff\xff\xff')
    assert(IpdrLong(-1).pack()=='\xff\xff\xff\xff\xff\xff\xff\xff')
    # Byte and UByte
    assert(IpdrUByte(255).pack()=='\xff')
    assert(IpdrByte(-1).pack()=='\xff')
    assert(int(IpdrUByte.from_bytes('\xff'))==255)
    assert(int(IpdrByte.from_bytes('\xff'))==-1)
    # Short and UShort
    assert(IpdrUShort(65535).pack()=='\xff\xff')
    assert(IpdrShort(-1).pack()=='\xff\xff')
    assert(int(IpdrUShort.from_bytes('\xff\xff'))==65535)
    assert(int(IpdrShort.from_bytes('\xff\xff'))==-1)
    # Float and Double
    assert(str(IpdrFloat.from_bytes('\x7f\x7f\xff\xff'))=='3.40282346639e+38')
    assert(IpdrFloat(3.40282346639e+38).pack()=='\x7f\x7f\xff\xff')
    assert(str(IpdrFloat.from_bytes('\x00\x80\x00\x00'))=='1.17549435082e-38')
    assert(IpdrFloat(1.17549435082e-38).pack()=='\x00\x80\x00\x00')
    assert(str(IpdrDouble(9007199254740992))=='9.00719925474e+15')
    assert(str(IpdrDouble.from_bytes('\xff\x7f\xff\xff\xff\xff\xff\xff'))=='-1.40444776161e+306')
