import json

try:
    with open('modules/modules.json', encoding='utf-8') as F:
        module_data = json.loads(F.read())
except Exception as ex:
    print(str(ex))

print(module_data)
