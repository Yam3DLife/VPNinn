import json
import base64
import os
from datetime import datetime

# ===== ЗАГРУЗКА ВСЕХ КЛЮЧЕЙ ИЗ ПАПКИ =====
def load_all_keys(tariff):
    """Загружает все JSON-файлы из папки keys/{tariff}/ и объединяет в массив"""
    folder = f"keys/{tariff}"
    
    if not os.path.exists(folder):
        raise FileNotFoundError(f"❌ Папка {folder} не найдена!")
    
    all_keys = []
    
    # Проходим по всем .json файлам в папке
    for filename in sorted(os.listdir(folder)):
        if filename.endswith('.json'):
            path = os.path.join(folder, filename)
            with open(path, 'r', encoding='utf-8') as f:
                try:
                    key_data = json.load(f)
                    all_keys.append(key_data)
                    print(f"  📄 Загружен: {filename}")
                except json.JSONDecodeError as e:
                    print(f"  ❌ Ошибка в {filename}: {e}")
    
    if not all_keys:
        raise ValueError(f"❌ В папке {folder} нет ни одного JSON-файла с ключами!")
    
    return all_keys

# ===== СОЗДАНИЕ ПОДПИСКИ =====
def build_subscription(keys, expire_timestamp, total_bytes, display_name, description):
    """Собирает подписку: заголовки + JSON-массив всех ключей"""
    
    headers = f"""#profile-title: HotVPN {display_name}
#profile-update-interval: 5
#support-url: https://t.me/Wd_Life
#subscription-userinfo: upload=0; download=0; total={total_bytes}; expire={expire_timestamp}
#sub-expire: true
#announce: {description}

"""
    json_part = json.dumps(keys, indent=2, ensure_ascii=False)
    combined = headers + json_part
    return base64.b64encode(combined.encode()).decode()

# ===== ОСНОВНАЯ ФУНКЦИЯ =====
def main():
    os.makedirs('subs', exist_ok=True)
    
    with open('users.json', 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    print(f"📦 Обработка {len(users)} пользователей...")
    
    for user_id, user_info in users.items():
        if user_info.get('status') != 'active':
            if os.path.exists(f'subs/{user_id}.txt'):
                os.remove(f'subs/{user_id}.txt')
                print(f"❌ {user_id}: заблокирован, файл удалён")
            continue
        
        tariff = user_info.get('plan', 'lite')
        
        tariff_info = {
            "vip": {"display_name": "VIP 👑", "description": "Все серверы, безлимитный трафик"},
            "lite": {"display_name": "LITE ⚡", "description": "Доступные серверы, 50 ГБ/мес"},
            "trial": {"display_name": "TRIAL 🔥", "description": "Пробный доступ на 3 дня, 5 ГБ"}
        }
        
        info = tariff_info.get(tariff, {"display_name": tariff.upper(), "description": ""})
        display_name = info["display_name"]
        description = info["description"]
        
        expire_date_str = user_info.get('expire_date')
        if expire_date_str:
            expire_timestamp = int(datetime.strptime(expire_date_str, "%Y-%m-%d").timestamp())
        else:
            expire_timestamp = 0
        
        traffic_limit_gb = user_info.get('traffic_limit_gb', 50)
        total_bytes = traffic_limit_gb * 1073741824
        
        try:
            keys = load_all_keys(tariff)
            print(f"  🔑 Найдено ключей: {len(keys)}")
            
            subscription = build_subscription(keys, expire_timestamp, total_bytes, display_name, description)
            
            with open(f'subs/{user_id}.txt', 'w', encoding='utf-8') as f:
                f.write(subscription)
            
            print(f"✅ {user_id}: {display_name} | ключей: {len(keys)} | истекает: {expire_date_str or 'никогда'}")
        except Exception as e:
            print(f"❌ {user_id}: {e}")

if __name__ == "__main__":
    main()
