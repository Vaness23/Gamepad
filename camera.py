from onvif import ONVIFCamera

myCam = ONVIFCamera('192.168.15.43', 80, 'student', 'studentpass.2019', '/etc/onvif/wsdl/')


def zeep_pythonvalue(self, xmlvalue):
    return xmlvalue

zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue