import json

def save_json_file(output_file,data):
    with open(output_file, 'w', encoding='utf-8') as final_file:  
        json.dump(data, final_file, ensure_ascii=False, indent=4)  