import sys
from subprocess import Popen, PIPE
import glob
import subprocess
import multiprocessing
import logging

# Set up primary logging
logging.basicConfig(
    filename='/home/almalinux/data/detail.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w'
)

# Set up secondary logging
clean_log_file = '/home/almalinux/data/clean.log'
clean_logger = logging.getLogger('clean_logger')
clean_logger.setLevel(logging.INFO)
clean_handler = logging.FileHandler(clean_log_file, mode='w')
clean_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
clean_logger.addHandler(clean_handler)

def run_parser(input_file):
    search_file = input_file + "_search.tsv"
    cmd = ['python', '/home/almalinux/pipeline/results_parser_v1.py', search_file]
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if err:
        return True
    logging.info(f'STEP 2: RUNNING PARSER: {" ".join(cmd)}')
    logging.info(out.decode("utf-8"))

    return False

def move_files(input_file, skip):
    output_dir = sys.argv[2]
    if not skip:
        files_to_move = [f"{input_file}.parsed", f"{input_file}_search.tsv", f"{input_file}_segment.tsv"]
    else:
        files_to_move = [f"{input_file}_segment.tsv"]
    for file in files_to_move:
        result = subprocess.run(["mv", file, output_dir],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            logging.info(f"Moved {file}")
        else:
            logging.error(f"Failed to move {file}: {result.stderr}")

def run_merizo_search(input_file, id):
    cmd = ['python3',
           '/home/almalinux/merizo_search/merizo_search/merizo.py',
           'easy-search',
           input_file,
           '/home/almalinux/data/cath_foldclassdb/cath-4.3-foldclassdb',
           id,
           'tmp',
           '--iterate',
           '--output_headers',
           '-d',
           'cpu',
           '--threads',
           '1'
           ]
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    logging.info(out.decode("utf-8"))
    if err:
        logging.info(err.decode("utf-8"))

def update_progress():
    cmd = ['python3','/home/almalinux/pipeline/progress.py']
    p = Popen(cmd, stdin=PIPE,stdout=PIPE, stderr=PIPE)

def read_dir(input_dir):
    logging.info(f'Reading directory {input_dir}')
    file_ids = list(glob.glob(input_dir + "*.pdb"))
    analysis_files = []
    for file in file_ids:
        id = file.rsplit('/', 1)[-1].split('.')[0]
        analysis_files.append([file, id])
    return analysis_files

def pipeline(filepath, id):
    run_merizo_search(filepath, id)
    skip = run_parser(id)
    move_files(id, skip)
    if not skip:
        logging.info(f'-------------Finished {id}-------------\n')
        clean_logger.info(id)
    else:
        logging.error(f'-------------Skipped: Failed to segment {id}------------\n')
        clean_logger.error(id)
    update_progress()
    
if __name__ == "__main__":
    pdbfiles = read_dir(sys.argv[1])
    p = multiprocessing.Pool(3)
    p.starmap(pipeline, pdbfiles)

