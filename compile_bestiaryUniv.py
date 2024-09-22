import json
import os
import re

def extract_value(data, key=None):
    if key and isinstance(data, dict):
        data = data.get(key, data)
    
    if isinstance(data, (int, float, str)):
        return data
    elif isinstance(data, list):
        if data and isinstance(data[0], dict):
            return extract_value(data[0])
        elif data:
            return ' '.join(str(item) for item in data if item)
    elif isinstance(data, dict):
        if 'average' in data:
            return data['average']
        elif 'ac' in data:
            return data['ac']
        elif 'walk' in data:
            return data['walk']
        else:
            return next(iter(data.values()), '')
    
    return ''

def extract_speed(speed_data):
    if isinstance(speed_data, dict):
        return speed_data.get('walk', 30)
    elif isinstance(speed_data, str):
        match = re.search(r'\d+', speed_data)
        return int(match.group()) if match else 30
    return extract_value(speed_data)

def extract_actions(actions_data):
    if not isinstance(actions_data, list):
        return []
    return [
        {
            'name': action.get('name', ''),
            'entries': action.get('entries', [])
        }
        for action in actions_data
        if action.get('name') in ['Multiattack', 'Attack', 'Bite', 'Claw', 'Slam']
    ]

def compile_bestiary(index_path, output_path):
    with open(index_path, 'r') as index_file:
        index = json.load(index_file)

    compiled_bestiary = {}

    for book_code, filename in index.items():
        file_path = os.path.join('assets', 'bestiary', filename)
        
        if not os.path.exists(file_path):
            print(f"Warning: File not found - {file_path}")
            continue

        with open(file_path, 'r', encoding='utf-8') as bestiary_file:
            bestiary_data = json.load(bestiary_file)

            for monster in bestiary_data.get('monster', []):
                name = monster.get('name', '')
                if name:
                    compiled_bestiary[name] = {
                        'source': extract_value(monster, 'source'),
                        'type': extract_value(monster, 'type'),
                        'size': extract_value(monster, 'size'),
                        'alignment': extract_value(monster, 'alignment'),
                        'ac': extract_value(monster, 'ac'),
                        'hp': extract_value(monster, 'hp'),
                        'speed': extract_speed(monster.get('speed', 30)),
                        'str': extract_value(monster, 'str'),
                        'dex': extract_value(monster, 'dex'),
                        'con': extract_value(monster, 'con'),
                        'int': extract_value(monster, 'int'),
                        'wis': extract_value(monster, 'wis'),
                        'cha': extract_value(monster, 'cha'),
                        'cr': extract_value(monster, 'cr'),
                        'actions': extract_actions(monster.get('action', []))
                    }

    with open(output_path, 'w', encoding='utf-8') as output_file:
        json.dump(compiled_bestiary, output_file, indent=2)

    print(f"Compiled bestiary saved to {output_path}")

if __name__ == "__main__":
    index_path = 'assets/bestiary/index.json'
    output_path = 'assets/bestiary/compiled_bestiary.json'
    compile_bestiary(index_path, output_path)