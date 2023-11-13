import os
import sys
import time
import subprocess
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
import numpy as np


args = sys.argv
print(f"Now loading CO3_contained_poscar_folder_abs_path_list from .npy file...")
print(args[1])
CO3_contained_poscar_folder_abs_path_list = np.load(args[1], allow_pickle=True)
print("len(CO3_contained_poscar_folder_abs_path_list): {} ".format(len(CO3_contained_poscar_folder_abs_path_list)))


def cd_dir_and_do_script(folder_path):
    # 1. Change current dir to dir that exists a POSCAR file
    os.chdir(folder_path)
    
    # 2. Run script
    error_list = []
    try:
        subprocess.run(['python3', './mk_CO3-clusterd_poscar.py'], 
                       stdout=subprocess.DEVNULL, 
                       stderr=subprocess.DEVNULL,)
    except Exception as e:
        error_list.append(poscar_folder_path)

        
def wrap_cd_dir_and_do_script(nnlist_folder_abs_path_list):
    before = time.time()
    try:
        p = Pool(cpu_count() - 1)
        print(f"Now make some CO3-clusterd poscar file!!!")
        list(tqdm(p.imap(cd_dir_and_do_script, nnlist_folder_abs_path_list), total=len(nnlist_folder_abs_path_list)))

    finally:
        p.close()
        p.join()
    after = time.time()
    print(f"it took {after - before}sec.")

    
wrap_cd_dir_and_do_script(CO3_contained_poscar_folder_abs_path_list[0:100])
