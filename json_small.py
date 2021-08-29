import json

with open('rbc_results (3).json', encoding='utf8') as file:
    data = json.loads(file.read())
    print(len(data))
    data = list({v['profile'][3]['ОГРН'][0]: v for v in data}.values())
    print(len(data))

with open('rbc_results0.json', 'w', encoding='utf8') as file:
    file.write(json.dumps(data))