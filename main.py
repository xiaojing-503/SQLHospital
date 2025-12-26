from utils.save_json_file import save_json_file
from utils.read_json_file import read_json_file
import json
import os
import time
from check.check_sql_result import compute_report
from process.correct_process import get_skeketon_schema
from correct.result import correct_result_new
from correct.empty import correct_empty
from correct.system import correct_system
from check.check_system import check_system_error
from check.check_value import check_value
from check.check_mask import check_mask


def identify_error(file_path,output_file,database_file):
    
    data=read_json_file(file_path)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("[")  
        
        for i, item in enumerate(data):
            new_err_type=''
            system_res=check_system_error(item,db_path=database_file)
            if system_res==0:
                new_err_type = 'system'
            else:
                value_res=check_value(item,database_file)
                if value_res == 0:  
                    new_err_type = "empty"  
                else:
                    mask_res,item = check_mask(item,database_file)
                    if mask_res ==0:
                        new_err_type = "result"  
                    else:
                        new_err_type = "correct"  
            item["new_err_type"]=new_err_type
            json.dump(item, f, ensure_ascii=False, indent=2)
            
            if i < len(data) - 1:
                f.write(",\n")
        f.write("]")  
            
     

def compute(file):

    compute_report(file,'err_type1')
    print("----------------------------------------------")
    compute_report(file,'err_type2')
    print("----------------------------------------------")
    compute_report(file,'new_err_type')
    print("----------------------------------------------")


def correct(skeleton_schema_file,corrected_file,database_path):
    
    data = read_json_file(skeleton_schema_file) 
    with open(corrected_file, 'w', encoding='utf-8') as f:
        f.write("[")  
        
        for i, item in enumerate(data):
            new_err_type = item['new_err_type'] 
            
            if new_err_type=='result':
                sql = correct_result_new(item)
                item['sql_new'] = sql
                print("\n")

            elif new_err_type=='empty':
                sql=correct_empty(item,database_path)
                item['sql_new'] = sql
                print("\n")

            elif new_err_type=='system':
                sql=correct_system(item,database_path)
                item['sql_new'] = sql
                print("\n")
        
            else:
                item['sql_new'] = item['err_pred']
                
            json.dump(item, f, ensure_ascii=False, indent=2)
            
            if i < len(data) - 1:
                f.write(",\n")
        f.write("]")  


if __name__ == "__main__":

    file_path='your_path'

    BIRD_DATABASE='/your_path/dev/dev_databases/'
    directory='/your_path'
    

    idenfy_file=os.path.join(directory, 'idenfy.json')
    process_file = os.path.join(directory, 'process.json')
    corrected_file = os.path.join(directory, 'corrected.json')
    evaluate_file=os.path.join(directory, 'evaluated.json')

    identify_error(file_path, idenfy_file,BIRD_DATABASE)
    compute(idenfy_file)
    get_skeketon_schema(idenfy_file,process_file,BIRD_DATABASE)
    correct(file_path,corrected_file,BIRD_DATABASE)
    os.system(f"sh process/run_evaluation.sh {corrected_file} {evaluate_file}")





