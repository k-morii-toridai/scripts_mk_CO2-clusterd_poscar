import pandas as pd
%load_ext autoreload
%autoreload 2
from my_package.textfile2df import poscar2df_coords 
from my_package.textfile2df import nnlist2df
from my_package import df2poscar


df_coords = poscar2df_coords(filename='./POSCAR')
df_nnlist = nnlist2df(POSCAR_nnlist='POSCAR.nnlist')


def get_elem_max_filter(df_nnlist=df_nnlist):
    """
    To get cluster center abs coords from df_coords, Please use this filter.
    
    Input: df_nnlist 
 -> Output: The max number of element 
            in neighboring column of df_nnlist, 
            when df_nnlist groupbyed neighboring column and .count() 
    """
    elem_max_num = df_nnlist.groupby('central atom').count()['neighboring atom'].max()
    elem_max_num_filter = df_nnlist.groupby('central atom').count()['neighboring atom'] == elem_max_num
    # elem_max_num_filter_list = elem_max_num_filter.to_list()
    elem_max_num_filter_list = pd.Series(elem_max_num_filter.to_list())
    return elem_max_num_filter_list


def get_all_non_clusterd_atom(df_nnlist=df_nnlist, df_coords=df_coords):
    """
    dependency: get_elem_max_filter(), get_right_value()
    
    To get non-clusterd central atom list, Use this func.
    
    Input: DataFrames
 -> Output: a list 
    
    param1: df_nnlist=df_nnlist
    param2: df_coords=df_coords
    """
    
    # 入力値が左側の数値と同じ場合、対応する右側の数値を返す関数
    def get_neighboring_atoms_list(central_atom_id, df_nnlist=df_nnlist):
        """
        To get all central atoms of a cluster(:neighbors), Input a number of cluster center element number(:central atom)

        Input: central atom column element In df_nnlist
     -> Output: All neighboring atom column element that Input(:elemnt) match central atom column element

        param1: Input: central atom column element In df_nnlist
        """
        # 左側の列から対応する行を選択し、右側の数値を取得
        # result = df_nnlist[df_nnlist['central atom'] == input_value]['neighboring atom'].values
        neighboring_atoms_list = df_nnlist[df_nnlist['central atom'] == central_atom_id]['neighboring atom'].tolist()
        return neighboring_atoms_list
    
    
    elem_max_num_filter = get_elem_max_filter(df_nnlist=df_nnlist)
    # クラスタ(原子団)の中心の原子のid(central atomの値)のリスト
    cluster_central_atom_list = df_coords[elem_max_num_filter]['central atom'].tolist()
    # クラスタ(原子団)に属するすべての原子のid(central atomの値)を取得
    cluster_all_atom_list_duplicated = [get_neighboring_atoms_list(elem) for elem in cluster_central_atom_list]
    # 2重リストを1重リストにflatten
    cluster_all_atom_list_duplicated_flatten = [item for sublist in cluster_all_atom_list_duplicated for item in sublist]
    # flat_listの重複削除
    cluster_all_atom_set = set(cluster_all_atom_list_duplicated_flatten)
    
    # 元のposcarのcentral atomの一覧を取得
    all_central_atom_set = set(df_coords['central atom'].tolist())
    
    # クラスタ(原子団)に属さない原子のid(central atomの値)を取得
    all_non_clusterd_atom_list = list(all_central_atom_set.difference(cluster_all_atom_set))
    
    return all_non_clusterd_atom_list


def get_all_non_clusterd_atom_filter(df_nnlist=df_nnlist, df_coords=df_coords):
    """
    To convert list to filter, Use thie func.
    """
    all_non_clusterd_atom_list = get_all_non_clusterd_atom(df_nnlist=df_nnlist, df_coords=df_coords)
    all_non_clusterd_atom_filter = df_coords['central atom'].apply(lambda row: row in all_non_clusterd_atom_list)
    return all_non_clusterd_atom_filter


central_atom_filter_fix = get_elem_max_filter() | get_all_non_clusterd_atom_filter()
df_coords_abs_center = df_coords[central_atom_filter_fix]


def df_elem_str2num(df_coords_abs_center=df_coords_abs_center):
    # 文字列を数値化する
    df_coords_abs_center['x'] = pd.to_numeric(df_coords_abs_center['x'], errors='coerce')
    df_coords_abs_center['y'] = pd.to_numeric(df_coords_abs_center['y'], errors='coerce')
    df_coords_abs_center['z'] = pd.to_numeric(df_coords_abs_center['z'], errors='coerce')
    return df_coords_abs_center


df_coords_abs_center = df_elem_str2num(df_coords_abs_center=df_coords_abs_center)

df_nnlist_grouped = df_nnlist.groupby('central atom').mean()
# central atomカラムでgroupby.mean()した後、index列(central atom)をカラムにする   
df_nnlist_grouped = df_nnlist_grouped.reset_index()   
# 意味のないカラムを落とす
df_nnlist_grouped = df_nnlist_grouped[['central atom', 'X', 'Y', 'Z']]

# フィルターで必要なクラスタの相対中心座標に絞る
df_cluster_relative_center = df_nnlist_grouped[central_atom_filter_fix]


def get_clusterd_coords(df_abs=df_coords_abs_center, df_relative=df_cluster_relative_center):
    df_coords_x = df_abs['x'] + df_relative['X']
    df_coords_y = df_abs['y'] + df_relative['Y']
    df_coords_z = df_abs['z'] + df_relative['Z']
    df_coords_species = df_abs['Species']

    # カラム名を指定してデータフレームを作成
    df_coords_fix = pd.DataFrame({
        'X': df_coords_x,
        'Y': df_coords_y,
        'Z': df_coords_z,
        'Species': df_coords_species,
    })

    return df_coords_fix


df_coords_fix = get_clusterd_coords(df_abs=df_coords_abs_center, df_relative=df_cluster_relative_center)

# write df to poscar
df2poscar.df2poscar(df=df_coords_fix)
