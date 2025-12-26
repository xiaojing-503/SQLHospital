import json
import sqlite3

def check_system_error(item, db_path):

    sql=item["err_pred"]
    db_id=item["db_id"]
    try:
        db_file = f"{db_path}/{db_id}/{db_id}.sqlite"
        
        conn = sqlite3.connect(db_file)
        
        cursor = conn.cursor()
        
        cursor.execute(sql)
        
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return 1
    
    except Exception as e:
        print(f"Error: {e}")
        return 0


def check_system_with_eval_result(results_file, bird_file, output_file):
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    with open(bird_file, 'r', encoding='utf-8') as f:
        bird_data = json.load(f)
    
    processed_results = []
    
    for result, bird_entry in zip(results, bird_data):
        db_id = result['db_id']
        res = result['res']
        error = result['error']
        
        if res == 1:
            err_type = "correct"
        elif res == 0 and error is None:
            err_type = "result"
        else:
            err_type = "system"
        
        difficulty = bird_entry.get('difficulty', 'moderate')  
        schema_sequence = bird_entry.get('schema_sequence', '') 
        
        processed_result = {
            "db_id": db_id,
            "question": bird_entry['question'],  
            "evidence":  bird_entry['evidence'], 
            "difficulty": difficulty,
            "schema_sequence": schema_sequence,
            "id": result['sql_idx'],  
            "err_gold": result['gold'],  
            "err_pred": result['pred'],  
            "err_type": err_type,
            "new_err_type": ""  
        }
        
        processed_results.append(processed_result)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_results, f, ensure_ascii=False, indent=4)

