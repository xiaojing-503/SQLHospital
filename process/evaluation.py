import sys
import json
import argparse
import sqlite3
import multiprocessing as mp
import re
from func_timeout import func_timeout, FunctionTimedOut


def read_json_file(file_path):  
   
    try:  
        with open(file_path, 'r', encoding='utf-8') as file:  
            data = json.load(file)  
        return data  
    except FileNotFoundError:  
        print(f"Error: The file {file_path} was not found.")  
    except json.JSONDecodeError:  
        print(f"Error: The file {file_path} is not a valid JSON file.")  
    except Exception as e:  
        print(f"An unexpected error occurred: {e}")  


def load_json(dir):
    with open(dir, 'r') as j:
        contents = json.loads(j.read())
    return contents

def result_callback(result):
    exec_result.append(result)
    
def write_results_to_json(file_path):  
    with open(file_path, 'w') as f:  
        json.dump(exec_result, f, indent=4) 

def execute_sql(predicted_sql,ground_truth, db_path):
    conn = sqlite3.connect(db_path)
    # Connect to the database
    cursor = conn.cursor()
    cursor.execute(predicted_sql)
    predicted_res = cursor.fetchall()
    # print("predicted_sql:",predicted_sql)
    # print("predicted_res:",predicted_res)
    cursor.execute(ground_truth)
    ground_truth_res = cursor.fetchall()
    # print("ground_truth:",ground_truth)
    # print("ground_truth_res:",ground_truth_res)
    res = 0
    if set(predicted_res) == set(ground_truth_res):
        res = 1
    
    # if res == 0 and len(str(predicted_res)) == len(str(ground_truth_res)):
    #     print(predicted_sql)
    #     print(ground_truth)
    #     print(predicted_res)
    #     print(ground_truth_res)
    #     print("-------------------")
    return res




def extract_db_name_from_path(path):  
    pattern = r'/([^/]+)/\1\.sqlite$'  
    match = re.search(pattern, path)  
    if match:  
        db_name = match.group(1)  
        return db_name  
    return None 


def execute_model(predicted_sql, ground_truth, db_place, idx, meta_time_out):  
    # print("db_place:",db_place)
    db_name=extract_db_name_from_path(db_place)
    # print("db_name:",db_name)
    result = {'sql_idx': idx,'db_id': db_name, 'gold':ground_truth, 'pred':predicted_sql, 'res': None, 'error': None}  
    
    try:  
        res = func_timeout(meta_time_out, execute_sql, args=(predicted_sql, ground_truth, db_place))  
        result['res'] = res  
    except KeyboardInterrupt:  
        sys.exit(0)  
    except FunctionTimedOut:  
        result['error'] = 'timeout'  
        result['res'] = 0  
    except Exception as e:  
        result['error'] = f'system:{e}'  
        result['res'] = 0  
    
    return result  

def package_diff(sql_path):
    diffs = []
    sql_data = read_json_file(sql_path)
    for item in sql_data:
        diff=item.get('difficulty','')

        diffs.append(diff)


    return diffs


def package_sqls(sql_path, db_root_path, mode='gpt'):
    clean_sqls = []
    db_path_list = []
    if mode == 'gpt':
        # sql_data = json.load(open(sql_path, 'r'))
        sql_data = read_json_file(sql_path)
        for item in sql_data:
            sql=item.get('sql_new','')
            # print(sql)
            # sql=item.get('err_pred','')
            db_name=item.get('db_id','')
            # if type(sql_str) == str:
            #     sql, db_name = sql_str.split('\t----- bird -----\t')
            # else:
            #     sql, db_name = " ", "financial"
            clean_sqls.append(sql)
            db_path_list.append(db_root_path + db_name + '/' + db_name + '.sqlite')
            

    elif mode == 'gt':
        # sqls = open(sql_path + data_mode + '_gold.sql')
        # sql_txt = sqls.readlines()
        sql_data = read_json_file(sql_path)
        # sql_txt = [sql.split('\t')[0] for sql in sql_txt]
        for idx, item in enumerate(sql_data):
            # sql, db_name = sql_str.strip().split('\t')
            sql=item.get('err_gold','')
            # sql=item.get('err_gold','')
            db_name=item.get('db_id','')
            clean_sqls.append(sql)
            db_path_list.append(db_root_path + db_name + '/' + db_name + '.sqlite')
            
    return clean_sqls, db_path_list


def run_sqls_parallel(sqls, db_places, num_cpus=1, meta_time_out=30.0):  
    pool = mp.Pool(processes=num_cpus)  
    for i, sql_pair in enumerate(sqls):  
        
        predicted_sql, ground_truth = sql_pair  
        pool.apply_async(  
            execute_model,   
            args=(predicted_sql, ground_truth, db_places[i], i, meta_time_out),   
            callback=result_callback  
        )  
    pool.close()  
    pool.join()  

def sort_results(list_of_dicts):
  return sorted(list_of_dicts, key=lambda x: x['sql_idx'])

def compute_acc_by_diff(exec_results,contents):
    num_queries = len(exec_results)
    results = [res['res'] for res in exec_results]
    # contents = load_json(diff_json_path)
    simple_results, moderate_results, challenging_results = [], [], []

    for i,content in enumerate(contents):
        if content == 'simple':
            simple_results.append(exec_results[i])

        if content == 'moderate':
            moderate_results.append(exec_results[i])

        if content == 'challenging':
            challenging_results.append(exec_results[i])

    # simple_acc = sum([res['res'] for res in simple_results])/len(simple_results)
    # moderate_acc = sum([res['res'] for res in moderate_results])/len(moderate_results)
    # challenging_acc = sum([res['res'] for res in challenging_results])/len(challenging_results)
    # all_acc = sum(results)/num_queries
    # count_lists = [len(simple_results), len(moderate_results), len(challenging_results), num_queries]
    # return simple_acc * 100, moderate_acc * 100, challenging_acc * 100, all_acc * 100, count_lists
    # 安全地计算准确率  
    simple_acc = sum([res['res'] for res in simple_results]) / len(simple_results) if simple_results else 0  
    moderate_acc = sum([res['res'] for res in moderate_results]) / len(moderate_results) if moderate_results else 0  
    challenging_acc = sum([res['res'] for res in challenging_results]) / len(challenging_results) if challenging_results else 0  
    all_acc = sum(results) / num_queries if num_queries else 0  
    
    count_lists = [len(simple_results), len(moderate_results), len(challenging_results), num_queries]  
    return simple_acc * 100, moderate_acc * 100, challenging_acc * 100, all_acc * 100, count_lists  



def print_data(score_lists,count_lists):
    levels = ['simple', 'moderate', 'challenging', 'total']
    print("{:20} {:20} {:20} {:20} {:20}".format("", *levels))
    print("{:20} {:<20} {:<20} {:<20} {:<20}".format('count', *count_lists))

    print('======================================    ACCURACY    =====================================')
    print("{:20} {:<20.2f} {:<20.2f} {:<20.2f} {:<20.2f}".format('accuracy', *score_lists))


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('--sql_path', type=str, required=True, default='')
    args_parser.add_argument('--db_root_path', type=str, required=True, default='')
    args_parser.add_argument('--num_cpus', type=int, default=1)
    args_parser.add_argument('--meta_time_out', type=float, default=30.0)
    args_parser.add_argument('--mode_gt', type=str, default='gt')
    args_parser.add_argument('--mode_predict', type=str, default='gpt')
    args_parser.add_argument('--difficulty',type=str,default='simple')
    args_parser.add_argument('--save_path',type=str,default='')
    args = args_parser.parse_args()
    exec_result = []

    pred_queries, db_paths = package_sqls(args.sql_path, args.db_root_path, mode=args.mode_predict)
    # generate gt sqls:
    gt_queries, db_paths_gt = package_sqls(args.sql_path, args.db_root_path, mode='gt')

    # print("pred_queries:\n",pred_queries)
    # print("gt_queries:\n",gt_queries)

    query_pairs = list(zip(pred_queries,gt_queries))
    run_sqls_parallel(query_pairs, db_places=db_paths, num_cpus=args.num_cpus, meta_time_out=args.meta_time_out)
    exec_result = sort_results(exec_result)
    
    # with open("exec_result.json", "w", encoding="utf-8") as f:
    #     f.write(json.dumps(exec_result, indent=2, ensure_ascii=False))

    # print("exec_result:",exec_result)
    write_results_to_json(args.save_path)  

    diffs=package_diff(args.sql_path)
    print('start calculate')
    simple_acc, moderate_acc, challenging_acc, acc, count_lists = \
        compute_acc_by_diff(exec_result,diffs)
    score_lists = [simple_acc, moderate_acc, challenging_acc, acc]
    print_data(score_lists,count_lists)
    print('===========================================================================================')
    print("Finished evaluation")


    