import numpy as np
from tqdm import tqdm 
from multiprocessing import Pool, cpu_count


poscar_path_list_loaded = np.load('poscar_path_list.npy', allow_pickle=True)
print(f"len(poscar_path_list_loaded): {len(poscar_path_list_loaded)}")


def return_C_O_exist(poscar_path):
    def get_species_from_poscar(poscar_path):
        # POSCARファイルから元素種の行から元素種を取り出す
        with open(poscar_path, mode='r') as f:
            poscar_line_list = f.readlines()
            # poscarからspeciesをリストで取得
            species_list = set(poscar_line_list[5][:-1].split(' '))
            species_list.discard('')
            return species_list

    return set(['C', 'O']) <= set(get_species_from_poscar(poscar_path))


# return_C_O_exist()を並列化して実行
p = Pool(cpu_count() - 1)
bool_C_O_exist_list = list(tqdm(p.imap(return_C_O_exist, poscar_path_list_loaded), total=len(poscar_path_list_loaded)))
p.close()
p.join()

# CとOを含むPOSCARファイルを抽出し，そのリストを.npy形式で保存
C_O_existed_poscar_path_list = poscar_path_list_loaded[bool_C_O_exist_list]
np.save('C_O_existed_poscar_path_list.npy', C_O_existed_poscar_path_list)
