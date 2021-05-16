import xml.etree.ElementTree as ET

tree = ET.parse("AlarmDecoder_WebApp_PiBakery_Recipe.xml")
root = tree.getroot()
for elt in root.iter("{http://www.w3.org/1999/xhtml}block"):

    if elt.attrib.get('type') == 'runcommand':
        print("run commannd as user %s: %s" % (elt[1].text.strip(), elt[0].text.strip()))
    elif elt.attrib.get('type') == 'packageinstall':
        print("install package %s" % (elt[0].text.strip()))

