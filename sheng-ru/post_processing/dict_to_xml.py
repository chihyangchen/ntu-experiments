import xml.etree.ElementTree as ET

def dict_to_xml(dictionary, root_name='root'):
    root = ET.Element(root_name)
    for key, value in dictionary.items():
        if isinstance(value, dict):
            child = dict_to_xml(value, key)
            root.append(child)
        else:
            child = ET.Element('pair')
            child.set('key', key)
            child.text = str(value)
            root.append(child)
    return ET.tostring(root, encoding='unicode')

# 示例字典
dictionary = {
    'person': {
        'name': 'John',
        'age': 30,
        'city': 'New York'
    }
}

xml_string = dict_to_xml(dictionary)
print(xml_string)