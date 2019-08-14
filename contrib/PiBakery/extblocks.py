import xml.etree.ElementTree as ET


def find_rec(node, element, result):
     print 'foo', element, node
     for item in node.findall(element):
         print 'b'
         result.append(item)
         find_rec(item, element, result)
     return result

def find_recR(node, element):
    def _find_rec(node, element, result):
        for el in node.getchildren():
            _find_rec(el, element, result)
        if node.tag == element:
            result.append(node)
    res = list()
    _find_rec(node, element, res)
    return res

tree = ET.parse("AlarmDecoder_WebApp_PiBakery_Recipe.xml")
for  elt in tree.iter():
    if elt.tag[-5:] == 'field':
       print "'%s'" % (elt.text.strip())
    #else:
       #print "****** %s: '%s'" % (elt.tag, elt.text.strip())

#find_recR(ET.parse("AlarmDecoder_WebApp_PiBakery_Recipe.xml"), 'block')

