############################################################################### 
# This section contains the Ipdr Documentation Types, 
# As defined in the TM Forum document: IPDR-XDR_Encoding_Format.pdf
############################################################################### 

from IpdrXdrElementaryTypes import *
from collections import OrderedDict
from xdrlib import Error as XDRError
import copy

class IpdrStructure(object):
    _struc=OrderedDict([])
    def __init__(self,**kwargs):
        for attr in self._struc.keys():
            self.__setattr__(attr,None)
        for attr, value in kwargs.iteritems():
            self.__setattr__(attr,value)
            
    def __getattr__(self,attr):
        return None
                
    def __repr__(self):
        out = []
        for attr in self._struc.keys():
            val=getattr(self,attr)
            if val is not None:
                out += ['%s=%s' % (attr,repr(val))]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(out))
    __str__ = __repr__
    
    def to_xml(self):
        out = ""
        for attr in self._struc.keys():
            value=getattr(self,attr)
            if value is not None:
                #if hasattr(value,"to_xml"):
                #    value=value.to_xml()
                if hasattr(value,"ipdr_type"):
                    out += '<{attr} type=\"{type}\">'.format(attr=attr,type=value.ipdr_type)
                else:
                    out += '<{attr}>'.format(attr=attr)
                if hasattr(value,"to_xml"):
                    value=value.to_xml()
                out += '{value}</{attr}>'.format(attr=attr,value=value)
        return '<{cls}>{inner}</{cls}>'.format(cls=self.__class__.__name__,inner=out)
    
    def pack(self):
        out = ""
        for attr in self._struc.keys():
            val=getattr(self,attr)
            if val is not None:
                out+=val.pack()
        return out

    @classmethod
    def load(cls,filep):
        obj=cls()
        for (k,v) in obj._struc.items():
            if isinstance(v,object):
                v=copy.deepcopy(v)
            obj.__setattr__(k,v.load(filep))
        return obj

class AttributeDescriptor(IpdrStructure):
    # XDR definition:
    # struct AttributeDescriptor {
    #     UTF8String attributeName;
    #     int typeId;
    # };
    _struc=OrderedDict([
        ("attributeName",IpdrString),
        ("typeId",IpdrInt)
    ])
    
    def to_xml(self):
        return "<AttributeDescriptor attributeName=\"{}\" typeId=\"{}\" derivedType=\"{}\"/>".format(self.attributeName,self.typeId,ipdr_class_from_type_id[self.typeId].ipdr_type)
        
#
# Store RecordDescriptors so they can used to unpack RecordData
#
recordDescriptorDict={} 

class RecordDescriptor(IpdrStructure):
    # XDR definition:
    # struct RecordDescriptor {
    #     int descriptorId;
    #     UTF8String typeName;
    #     AttributeDescriptor attributes<>;
    # };
    _struc=OrderedDict([
        ("descriptorId",IpdrInt),
        ("typeName",IpdrString),
        ("attributes",IpdrArray(AttributeDescriptor))
    ])

class IPDRRecordData(IpdrStructure):
    _struc=OrderedDict([])
    
    def __setattr__(self,attr,val):
        if attr != "_struc" and attr not in self._struc:
                self._struc[attr]=None
        return super(IPDRRecordData,self).__setattr__(attr,val)
        
    def __getattr__(self,attr):
        return None
        
    def ___repr__(self):
        out = []
        for attr in self._struc.keys():
            val=getattr(self,attr)
            if val is not None:
                out += ['{}={}({})'.format(attr,val.ipdr_type,val)]
        return (', '.join(out))
        
    def to_xml(self):
        out = ""
        for attr in self._struc.keys():
            val=getattr(self,attr)
            if val is not None:
                out += "<{attr} type=\"{type}\">{value}</{attr}>".format(attr=attr,type=val.ipdr_type,value=val.to_xml())
        return out

        
class IPDRRecord(IpdrStructure):
    # XDR definition:
    # struct IPDRRecord {
    #     int descriptorId;
    #     IPDRRecordData data;
    # };
    _struc=OrderedDict([
        ("descriptorId",IpdrInt),
        ("data",IPDRRecordData)
    ])
    
    def pack(self):
        out=self.descriptorId.pack()
        for el in self.data:
            out+=el.pack()
        return out
    
    @classmethod
    def load(cls,filep):
        obj=cls()
        obj.descriptorId=IpdrInt.load(filep)
        if obj.descriptorId not in recordDescriptorDict:
            raise XDRError, 'value=%d not a previously streamed RecordDescriptor Id' % obj.descriptorId
        list=[]
        for attributeDescriptor in recordDescriptorDict[int(obj.descriptorId)].attributes:
            ipdr_class=ipdr_class_from_type_id[attributeDescriptor.typeId]
            el = IPDRRecordData() 
            attr=attributeDescriptor.attributeName
            val=ipdr_class.load(filep)
            setattr(el,attr,val)
            list.append(el)
        obj.data=list
        return obj
        
    def to_xml(self):
        return '<IPDRRecord descriptorId=\"%s\"><IPDRRecordData>%s</IPDRRecordData></IPDRRecord>' % (self.descriptorId,"".join([x.to_xml() for x in self.data]))
        
    def __repr__(self):
        return 'IPDRRecord(descriptorId=%s,data=%s)' % (repr(self.descriptorId),repr(self.data))

class IPDRDocEnd(IpdrStructure):
    # XDR definition:
    # struct IPDRDocEnd {
    #     int count;
    #     hyper endTime;
    # };
    _struc=OrderedDict([
        ("count",IpdrInt),
        ("endTime",IpdrDateTimeMsec)
    ])

class IPDRStreamElement(IpdrStructure):
    # XDR definition:
    # union IPDRStreamElement switch(ElementType kind) {
    #     case RECORDDESC:
    #         RecordDescriptor desc;
    #     case IPDRREC:
    #         IPDRRecord rec;
    #     case DOCEND:
    #         IPDRDocEnd docEnd;
    # };
    _struc=OrderedDict([
        ("kind",None),
        ("desc",None),
        ("rec",None),
        ("docEnd",None)
    ])

    def __getattr__(self, attr):
        return getattr(self.switch, attr)

    def __repr__(self):
        out = []
        for attr in self._struc.keys():
            val=getattr(self,attr)
            if val is not None:
                out += ['%s=%s' % (attr,repr(val))]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(out))
        
    def to_xml(self):
        out = "<IPDRStreamElement kind=\"%s\">" % self.kind
        if self.kind == IpdrElementTypeEnum.RECORDDESC:
            out += self.desc.to_xml()
        elif self.kind == IpdrElementTypeEnum.IPDRREC:
            out += self.rec.to_xml()
        elif self.kind == IpdrElementTypeEnum.DOCEND:
            out += self.docEnd.to_xml()
        out += "</IPDRStreamElement>"
        return out
        
    def pack(self):
        out=self.kind.pack()
        if self.kind == IpdrElementTypeEnum.RECORDDESC:
            out += self.desc.pack()
        elif self.kind == IpdrElementTypeEnum.IPDRREC:
            out += self.rec.pack()
        elif self.kind == IpdrElementTypeEnum.DOCEND:
            out += self.docEnd.pack()
        return out
        
    @classmethod
    def load(cls,filep):
        obj=cls()
        obj.kind=IpdrElementTypeEnum.load(filep)
        if obj.kind == IpdrElementTypeEnum.RECORDDESC:
            obj.desc = RecordDescriptor.load(filep)
            recordDescriptorDict[int(obj.desc.descriptorId)]=obj.desc
        elif obj.kind == IpdrElementTypeEnum.IPDRREC:
            obj.rec = IPDRRecord.load(filep)
        elif obj.kind == IpdrElementTypeEnum.DOCEND:
            obj.docEnd = IPDRDocEnd.load(filep)
        else:
            raise XDRError, 'bad switch=%s' % obj.kind
        return obj

class NameSpaceInfo(IpdrStructure):
    # XDR definition:
    # struct NameSpaceInfo {
    #     UTF8String nameSpaceURI;
    #     UTF8String nameSpaceID;
    # };
    _struc=OrderedDict([
        ("nameSpaceURI",IpdrString),
        ("nameSpaceID",IpdrString)
    ])

class IPDRHeader(IpdrStructure):
    # XDR definition:
    # struct IPDRHeader {
    #     int ipdrVersion;
    #     UTF8String ipdrRecorderInfo;
    #     hyper startTime;
    #     UTF8String defaultNameSpaceURI;
    #     NameSpaceInfo otherNameSpaces<>;
    #     UTF8String serviceDefinitionURIs<>;
    #     opaque docId<>;
    # };
    _struc=OrderedDict([
        ("ipdrVersion",IpdrInt),
        ("ipdrRecorderInfo",IpdrString),
        ("startTime",IpdrDateTimeMsec),
        ("defaultNameSpaceURI",IpdrString),
        ("otherNameSpaces",IpdrArray(NameSpaceInfo)),
        ("serviceDefinitionURIs",IpdrArray(IpdrString)),
        ("docId",IpdrUuid)
    ])

class IPDRDoc(IpdrStructure):
    # XDR definition:
    # struct IPDRDoc {
    #     IPDRHeader header;
    #     IPDRStreamElement elements<>;
    # };
    _struc=OrderedDict([
        ("header",IPDRHeader),
        ("elements",IpdrArray(IPDRStreamElement))
    ])
    def to_xml(self):
        out = ""
        for attr in self._struc.keys():
            val=getattr(self,attr)
            if val is not None:
                out += val.to_xml()
        return '<%s>%s</%s>' % (self.__class__.__name__,out,self.__class__.__name__)

