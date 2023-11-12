import numpy as np
import os
import subprocess
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import time


print(f"Now loading CO3_contained_nnlist_abspath_list from .npy file...")
CO3_contained_nnlist_abspath_list = np.load('scripts_get_CO3-contained_poscar_path_list/CO3_contained_nnlist_abspath_list.npy', allow_pickle=True)
print(f"CO3_contained_nnlist_abspath_list was loaded from .npy file!!!")
print("len(CO3_contained_nnlist_abspath_list) -> {} ".format(len(CO3_contained_nnlist_abspath_list)))


nnlist_folder_abs_path_list = [os.path.split(p)[0] for p in tqdm(CO3_contained_nnlist_abspath_list)]
print(f"nnlist_folder_abs_path was completely made!!!")


def cd_dir_and_do_script(folder_path):
    # 1. Change current dir to dir that exists a POSCAR file
    os.chdir(folder_path)
    
    # 2. Run script
    error_list = []
    try:
        subprocess.run(['python3', '/mnt/ssd_elecom_black_c2c/scripts_mk_CO2-clusterd_poscar/mk_CO3-clusterd_poscar.py'], 
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

    
wrap_cd_dir_and_do_script(nnlist_folder_abs_path_list)
