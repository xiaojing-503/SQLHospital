import sqlite3
import os
import re
import argparse
import multiprocessing
from utils.read_json_file import read_json_file
from utils.save_json_file import save_json_file
from sklearn.metrics import precision_score, recall_score, f1_score, classification_report


def execute_sql(database_name, sql):
   
    try:
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        conn.close()
        return result
    except sqlite3.Error as e:
        return f"SQLite error: {e}"


def compare_sql_results(database_path, db_id, sql1, sql2, timeout=5):
    
    database_name = os.path.join(database_path, db_id, f"{db_id}.sqlite")

    with multiprocessing.Pool(processes=1) as pool:
        try:
            result1_async = pool.apply_async(execute_sql, (database_name, sql1))
            result1 = result1_async.get(timeout=timeout)

            result2_async = pool.apply_async(execute_sql, (database_name, sql2))
            result2 = result2_async.get(timeout=timeout)


            if isinstance(result1, str) or isinstance(result2, str):
                return "system"
            return "correct" if result1 == result2 else "result"

        except multiprocessing.TimeoutError:
            
            pool.terminate()
            return "timeout"

        except Exception as e:
            return "timeout"

def get_system_error_desc(database_path, db_id, sql, timeout=5):
   
    database_name = os.path.join(database_path, db_id, f"{db_id}.sqlite")

    try:
        result = execute_sql(database_name, sql)
        

        if isinstance(result, str):
            match = re.search(r'SQLite error: (.+)', result)
            if match:
                result = match.group(1)
            print(f"{result}")
            return result
        return ""  

    except Exception as e:
        return "timeout"


def check_sql(sql_file, save_file, bird_database, new_sql, timeout=5):
    data = read_json_file(sql_file)

    y_true = []
    y_pred = []
    true_err_count=0
    pred_err_count=0
    for item in data:
        sql1 = item['pred_sql']
        sql2 = item[new_sql]
        db_id = item['db_id']
        err_type = item['err_type']

        comparison_result = compare_sql_results(bird_database, db_id, sql1, sql2, timeout)

        item['new_err_type'] = comparison_result
  

        true_label = 1 if err_type == "correct" else 0
        pred_label = 1 if item['new_err_type'] == "correct" else 0

        # if item['new_err_type'] != "timeout":
        y_true.append(true_label)
        y_pred.append(pred_label)

        if item['new_err_type']!='correct':
            pred_err_count+=1
            if err_type!='correct':
                true_err_count+=1

    
   

    save_json_file(save_file, data)

    if y_true and y_pred:

        report = classification_report(y_true, y_pred, target_names=["incorrect", "correct"])
        print(report)
        report_dict = classification_report(y_true, y_pred, target_names=["incorrect", "correct"], output_dict=True)  

        print("Classification Report:")  
        for label, metrics in report_dict.items():  
            if isinstance(metrics, dict): 
                print(f"{label}:")  
                for metric, value in metrics.items():  
                    print(f"  {metric}: {value:.3f}")  
            else:  
                print(f"{label}: {metrics:.3f}")  

        precision = precision_score(y_true, y_pred) * 100
        recall = recall_score(y_true, y_pred) * 100
        f1 = f1_score(y_true, y_pred) * 100

        print("Precision: {:.2f}%".format(precision))
        print("Recall: {:.2f}%".format(recall))
        print("F1-score: {:.2f}%".format(f1))

import json
from sklearn.metrics import classification_report, precision_score, recall_score, f1_score

def compute_report(sql_file, new_err_key):
    print("new_err_key")
    data = read_json_file(sql_file)
    y_true = []
    y_pred = []
    pred_err_count = 0
    true_err_count = 0

    for item in data:
        err_type = item['err_type']
        true_label = 1 if err_type == "correct" else 0
        pred_label = 1 if item.get(new_err_key, '') == "correct" else 0

        y_true.append(true_label)
        y_pred.append(pred_label)

        if item.get(new_err_key, '') != 'correct':
            pred_err_count += 1
            if err_type != 'correct':
                true_err_count += 1

    
    if y_true and y_pred:
        report = classification_report(y_true, y_pred, target_names=["incorrect", "correct"], zero_division=1)
        print(report)

        report_dict = classification_report(y_true, y_pred, target_names=["incorrect", "correct"], output_dict=True, zero_division=1)  

        print("\n--- Classification Report ---")  
        for label, metrics in report_dict.items():  
            if isinstance(metrics, dict):  
                print(f"{label}:")  
                for metric, value in metrics.items():  
                    print(f"  {metric}: {value:.3f}")  
            else:  
                print(f"{label}: {metrics:.3f}")  

        precision = precision_score(y_true, y_pred, zero_division=1) * 100
        recall = recall_score(y_true, y_pred, zero_division=1) * 100
        f1 = f1_score(y_true, y_pred, zero_division=1) * 100

        print("\n--- Evaluation Metrics ---")
        print(f"Precision: {precision:.2f}%")
        print(f"Recall: {recall:.2f}%")
        print(f"F1-score: {f1:.2f}%")
   

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Check SQL results and classify errors.")
#     parser.add_argument('--sql_file', required=True, type=str, help='Path to the input JSON file containing SQL data')
#     parser.add_argument('--save_file', required=True, type=str, help='Path to the output JSON file to save results')
#     parser.add_argument('--bird_database', required=True, type=str, help='Path to the SQLite databases')
#     parser.add_argument('--new_sql_name', required=True, type=str, help='Key for the new SQL in the JSON data')
#     parser.add_argument('--timeout', type=int, default=5, help='Maximum time (seconds) allowed for each SQL query')

#     args = parser.parse_args()

#     check_sql(
#         sql_file=args.sql_file,
#         save_file=args.save_file,
#         bird_database=args.bird_database,
#         new_sql=args.new_sql_name,
#         timeout=args.timeout
#     )


