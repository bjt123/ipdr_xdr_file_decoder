# ipdr_xdr_file_decoder

## Introduction

You need to verify the contents of computer generated TM-Forum standardised IPDR XDR files, what do you do? 

You can't use wireshark, you can't read them as text files, they are binary formatted.  

The python scripts contained help solve this problem.

Given an IPDR-XDR file encoded as defined by the TM-Forum encoding format,
these scripts allow you to decode it into an XML format that is human readable. 
(The reason why XML is used is to illustrate the Ipdr Elementary Type of each decoded element).

Included are python scripts that also allow you to load the IPDR-XDR file metadata
into python objects, so you can manipulate and analyse them.


Note that a key difference between the TM-Forum standard for IPDR-XDR files and 
the traditional python xdrlib library, is that the TM-Forum encoding standard does not
quad-align / zero-pad the fields within an XDR file.  As such, the xdrlib python library is not used 
for packing / unpacking XDR structures within this project.

## Limitations

These python scripts are written for the use of analyzing IPDR-XDR files only,
the scripts are not written with the intention of being used to translate IPDR-XDR
files within a business application or production build.  Use at own risk.

## Example Use

Given the "example.xdr" file provide, executing the script:

> ipdr_xdr_to_xml.py example.xdr

Will generate an "example.xdr.xml" file, which contains the following:
```
<?xml version="1.0" ?>
<IPDRDoc>
    <IPDRHeader>
        <ipdrVersion type="int">4</ipdrVersion>
        <ipdrRecorderInfo type="string">Test Ipdr Xdr File</ipdrRecorderInfo>
        <startTime type="ipdr:dateTimeMsec">1970-01-01 00:00:00.001</startTime>
        <defaultNameSpaceURI type="string">test_namespace</defaultNameSpaceURI>
        <otherNameSpaces>
            <array length="0"/>
        </otherNameSpaces>
        <serviceDefinitionURIs>
            <array length="0"/>
        </serviceDefinitionURIs>
        <docId type="ipdr:uuid">12345678-1234-5678-1234-567812345678</docId>
    </IPDRHeader>
    <array length="-1">
        <IPDRStreamElement kind="RECORDDESC">
            <RecordDescriptor>
                <descriptorId type="int">1</descriptorId>
                <typeName type="string">Test Numericals</typeName>
                <attributes>
                    <array length="12">
                        <AttributeDescriptor attributeName="Test_Bool_True" derivedType="boolean" typeId="41"/>
                        <AttributeDescriptor attributeName="Test_Bool_False" derivedType="boolean" typeId="41"/>
                        <AttributeDescriptor attributeName="Test_UByte" derivedType="unsignedbyte" typeId="43"/>
                        <AttributeDescriptor attributeName="Test_Byte" derivedType="byte" typeId="42"/>
                        <AttributeDescriptor attributeName="Test_UShort" derivedType="unsignedShort" typeId="45"/>
                        <AttributeDescriptor attributeName="Test_Short" derivedType="short" typeId="44"/>
                        <AttributeDescriptor attributeName="Test_UInt" derivedType="unsignedInt" typeId="34"/>
                        <AttributeDescriptor attributeName="Test_Int" derivedType="int" typeId="33"/>
                        <AttributeDescriptor attributeName="Test_ULong" derivedType="unsignedLong" typeId="36"/>
                        <AttributeDescriptor attributeName="Test_Long" derivedType="long" typeId="35"/>
                        <AttributeDescriptor attributeName="Test_Float" derivedType="float" typeId="37"/>
                        <AttributeDescriptor attributeName="Test_Double" derivedType="double" typeId="38"/>
                    </array>
                </attributes>
            </RecordDescriptor>
        </IPDRStreamElement>
        <IPDRStreamElement kind="RECORDDESC">
            <RecordDescriptor>
                <descriptorId type="int">2</descriptorId>
                <typeName type="string">Test Non-Numericals</typeName>
                <attributes>
                    <array length="11">
                        <AttributeDescriptor attributeName="Test_String" derivedType="string" typeId="40"/>
                        <AttributeDescriptor attributeName="Test_DateTimeMsec" derivedType="ipdr:dateTimeMsec" typeId="548"/>
                        <AttributeDescriptor attributeName="Test_DateTimeUsec" derivedType="ipdr:dateTimeUsec" typeId="1571"/>
                        <AttributeDescriptor attributeName="Test_DateTime" derivedType="dateTime" typeId="290"/>
                        <AttributeDescriptor attributeName="Test_Ipv4Addr" derivedType="ipdr:ipV4Addr" typeId="802"/>
                        <AttributeDescriptor attributeName="Test_Ipv6Addr" derivedType="ipdr:ipV6Addr" typeId="1063"/>
                        <AttributeDescriptor attributeName="Test_IpAddr_1" derivedType="ipdr:ipAddr" typeId="2087"/>
                        <AttributeDescriptor attributeName="Test_IpAddr_2" derivedType="ipdr:ipAddr" typeId="2087"/>
                        <AttributeDescriptor attributeName="Test_Uuid" derivedType="ipdr:uuid" typeId="1319"/>
                        <AttributeDescriptor attributeName="Test_MacAddr" derivedType="ipdr:macAddress" typeId="1827"/>
                        <AttributeDescriptor attributeName="Test_HexBinary" derivedType="hexBinary" typeId="39"/>
                    </array>
                </attributes>
            </RecordDescriptor>
        </IPDRStreamElement>
        <IPDRStreamElement kind="IPDRREC">
            <IPDRRecord descriptorId="1">
                <IPDRRecordData>
                    <Test_Bool_True type="boolean">true</Test_Bool_True>
                    <Test_Bool_False type="boolean">false</Test_Bool_False>
                    <Test_UByte type="unsignedbyte">255</Test_UByte>
                    <Test_Byte type="byte">-1</Test_Byte>
                    <Test_UShort type="unsignedShort">65535</Test_UShort>
                    <Test_Short type="short">-1</Test_Short>
                    <Test_UInt type="unsignedInt">4294967295</Test_UInt>
                    <Test_Int type="int">-1</Test_Int>
                    <Test_ULong type="unsignedLong">18446744073709551615</Test_ULong>
                    <Test_Long type="long">-1</Test_Long>
                    <Test_Float type="float">3.40282346639e+38</Test_Float>
                    <Test_Double type="double">9.00719925474e+15</Test_Double>
                </IPDRRecordData>
            </IPDRRecord>
        </IPDRStreamElement>
        <IPDRStreamElement kind="IPDRREC">
            <IPDRRecord descriptorId="2">
                <IPDRRecordData>
                    <Test_String type="string">Test_String</Test_String>
                    <Test_DateTimeMsec type="ipdr:dateTimeMsec">1970-01-01 00:00:00.001</Test_DateTimeMsec>
                    <Test_DateTimeUsec type="ipdr:dateTimeUsec">1970-01-01 00:00:00.000001</Test_DateTimeUsec>
                    <Test_DateTime type="dateTime">1970-01-01 00:00:01</Test_DateTime>
                    <Test_Ipv4Addr type="ipdr:ipV4Addr">254.253.252.251</Test_Ipv4Addr>
                    <Test_Ipv6Addr type="ipdr:ipV6Addr">ff:fe:fd:fc:fb:fa:0:1</Test_Ipv6Addr>
                    <Test_IpAddr_1 type="ipdr:ipAddr">1.2.3.4</Test_IpAddr_1>
                    <Test_IpAddr_2 type="ipdr:ipAddr">ff:fe:fd:fc:fb:fa:0:1</Test_IpAddr_2>
                    <Test_Uuid type="ipdr:uuid">12345678-1234-5678-1234-567812345678</Test_Uuid>
                    <Test_MacAddr type="ipdr:macAddress">FF:FE:FD:FC:FB:FA</Test_MacAddr>
                    <Test_HexBinary type="hexBinary">ff00</Test_HexBinary>
                </IPDRRecordData>
            </IPDRRecord>
        </IPDRStreamElement>
        <IPDRStreamElement kind="DOCEND">
            <IPDRDocEnd>
                <count type="int">-1</count>
                <endTime type="ipdr:dateTimeMsec">1970-01-01 00:00:00.001</endTime>
            </IPDRDocEnd>
        </IPDRStreamElement>
    </array>
</IPDRDoc>
```
