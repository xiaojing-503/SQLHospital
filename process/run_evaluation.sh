db_root_path='your_databases/'
data_mode='dev'

num_cpus=16
meta_time_out=30.0
mode_gt='gt'
mode_predict='gpt'


echo '''starting to compare with knowledge for ex'''
python3 -u evaluation.py --db_root_path ${db_root_path} --sql_path $1  \
    --num_cpus ${num_cpus} --mode_gt ${mode_gt} --mode_predict ${mode_predict} \
    --meta_time_out ${meta_time_out} --save_path $2
