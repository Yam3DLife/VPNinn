import json
import base64
import os
from datetime import datetime

def load_all_keys(tariff):
    folder = f"keys/{tariff}"
    all_keys = []
    
    if not os.path.exists(folder):
        return []
    
    for filename in sorted(os.listdir(folder)):
        if filename.endswith('.json'):
            path = os.path.join(folder, filename)
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_keys.extend(data)
                else:
                    all_keys.append(data)
    
    return all_keys

def main():
    os.makedirs('subs', exist_ok=True)
    
    with open('users.json', 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    for user_id, user_info in users.items():
        if user_info.get('status') != 'active':
            continue
        
        tariff = user_info.get('plan', 'lite')
        keys = load_all_keys(tariff)
        
        if not keys:
            print(f"❌ {user_id}: нет ключей")
            continue
        
        # Кодируем JSON-массив в base64
        json_str = json.dumps(keys, indent=2, ensure_ascii=False)
        encoded = base64.b64encode(json_str.encode()).decode()
        
        with open(f'subs/{user_id}.txt', 'w', encoding='utf-8') as f:
            f.write(encoded)
        
        print(f"✅ {user_id}: {len(keys)} серверов")

if __name__ == "__main__":
    main()
