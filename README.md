# SQLHospital

Code for the paper "SQLHospital: Excising the Root of Text-to-SQL Hallucinations"

## Overview 

SQLHospital is a toolchain for detecting, repairing, and evaluating automatically generated SQL queries. Typical workflow: model (LLM or other) generates SQL → detect execution/value/semantic errors → apply targeted repairs based on error type → evaluate repaired queries against local SQLite databases.

Core responsibilities:
- Detect whether a predicted SQL is executable ("system"), contains wrong values ("empty"), has logical/skeleton issues ("result"), or is correct ("correct").
- Apply different correction strategies for each error type (system fixes, value-replacement fixes, skeleton/result fixes).
- Evaluate repaired SQLs by executing them against per-database SQLite files and computing accuracy.


## Quick start
1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure LLM endpoint:
- `utils/get_response.py` currently has placeholders for `url` and `headers['api-key']`. Replace them with your endpoint and API key, or modify the code to read from environment variables.
- Prompts are defined in `utils/prompt.py`. The LLM should return raw SQL text (no extra explanations).

3. Run the example pipeline:
- Edit the dataset and db paths in `main.py` (`file_path`, `BIRD_DATABASE`, `directory`).
- Run:

```bash
python3 main.py
```

The pipeline will write intermediate files such as `idenfy.json`, `process.json`, `corrected.json`, and `evaluated.json`.

4. Evaluate repaired outputs:
- Using provided script:

```bash
sh process/run_evaluation.sh <corrected_file.json> <evaluated_out.json>
```

- Or directly call the evaluation script:

```bash
python3 process/evaluation.py --sql_path <file> --db_root_path <path_to_dbs> --save_path <out.json>
```

