import json  

def merge_json_data(file_path1, file_path2, output_file_path):  
    with open(file_path1, 'r', encoding='utf-8') as f1:  
        data1 = json.load(f1)  
    
    with open(file_path2, 'r', encoding='utf-8') as f2:  
        data2 = json.load(f2)  

    question_to_info = {item['question'] + ' ' + item['evidence']: (item['err_gold'], item['difficulty']) for item in data2}  
    # print(question_to_info)

    for item in data1:  
        question = item.get('question')  
        if question in question_to_info:  
            item['err_gold'], item['difficulty'] = question_to_info[question]  
        print(item['err_gold'], item['difficulty'])
    
    with open(output_file_path, 'w', encoding='utf-8') as f_out:  
        json.dump(data1, f_out, ensure_ascii=False, indent=2)  
