import json

with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    if item['model'] == 'customers.khachhang':
        if 'trang_thai' in item['fields']:
            del item['fields']['trang_thai']

with open('data_clean.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)