import itertools
import pandas as pd
from my_package.textfile2df import poscar2df_coords 
from my_package.textfile2df import nnlist2df
from my_package.df2poscar import df2poscar


df_coords = poscar2df_coords(filename='./POSCAR')
df_nnlist = nnlist2df(POSCAR_nnlist='./POSCAR.nnlist')


# df_nnlistでcentral speciesがCのものに絞る
df_nnlist_central_species_C = df_nnlist[df_nnlist['central species'] == 'C']

# さらに，炭酸イオンかどうかを判定するためにに，あるcentral atomのneighboring speciesがCとO３つの計４つでできているか確認したい
# central atomの値を入力すれば，neighboring speciesのリストを返す関数get_neighboring_species_list()を作成
def get_neighboring_species_list(central_atom_id, df=df_nnlist_central_species_C):
        """
        To get all central atoms of a cluster(:neighbors), Input a number of cluster center element number(:central atom)

        Input: central atom column element In df_nnlist
     -> Output: All neighboring atom column element that Input(:elemnt) match central atom column element

        param1: Input: central atom column element In df_nnlist
        """
        # 左側の列から対応する行を選択し、右側の数値を取得
        # result = df_nnlist[df_nnlist['central atom'] == input_value]['neighboring atom'].values
        neighboring_species_list = df[df['central atom'] == central_atom_id]['neighboring species'].tolist()
        return neighboring_species_list


def match_C_O_3(central_atom_id):
    # 原子団の要素数は，Cが1つ，Oが3つの計4つかどうかcheck
    if len(get_neighboring_species_list(central_atom_id)) == 4:
        # 原子団の要素にCが1つだけ含まれているかどうかcheck
        if get_neighboring_species_list(central_atom_id).count('C') == 1:
            # 原子団の要素にOがちょうど3つ含まれているかどうかcheck
            if get_neighboring_species_list(central_atom_id).count('O') == 3:
                return True
        else:
            return False
    else:
        return False


# df_nnlist_central_species_Cに対し，CO3がどうかを確認し，CO3である原子のid一覧を取得
# まず，中心元素がCのid一覧(central atomの値の一覧)を取得
central_species_C_list = df_nnlist_central_species_C['central atom'].unique()
# その中で，match_C_O_3()を用いて，過不足なくCO3だけを含むものに絞る
matched_central_species_C_list = [i for i in central_species_C_list if match_C_O_3(i)]


# CO3の原子団に属するすべての原子のid(central atomの値)を得るための関数
def get_neighboring_atoms_list(central_atom_id, df=df_nnlist_central_species_C):
        """
        To get all central atoms of a cluster(:neighbors), Input a number of cluster center element number(:central atom)

        Input: central atom column element In df_nnlist
     -> Output: All neighboring atom column element that Input(:elemnt) match central atom column element

        param1: Input: central atom column element In df_nnlist
        """
        neighboring_atoms_list = df[df['central atom'] == central_atom_id]['neighboring atom'].tolist()
        return neighboring_atoms_list
    

# CO3の原子団に属するすべての原子のid(central atomの値)を得る
all_C_O_3_list = [get_neighboring_atoms_list(i) for i in matched_central_species_C_list]
# 2重リストを1重リストにflatten
all_C_O_3_list = list(itertools.chain.from_iterable(all_C_O_3_list))


# CO3の原子団に属さないすべての原子のid(central atomの値)を得る
all_non_C_O_3_list = list(set(df_coords['central atom'].tolist()) - set(all_C_O_3_list))


# CO3の中心原子Cと，CO3の原子団に属さないすべての原子をリストにしてから，フィルター作成
all_central_atom_list = matched_central_species_C_list + all_non_C_O_3_list


# all_central_atom_listをfilter化
all_central_atom_filter = df_coords['central atom'].apply(lambda x: x in all_central_atom_list)


# 絶対中心座標のDataFrame
df_coords_abs_center = df_coords[all_central_atom_filter]
# x,y,zカラムを文字列から数値に変換
df_coords_abs_center = df_coords_abs_center.astype({'x': float, 'y': float, 'z': float})


# 相対中心座標を計算
df_nnlist_groupbyed = df_nnlist[['central atom', 'X', 'Y', 'Z']].groupby('central atom').mean()
# # central atomカラムでgroupby.mean()した後、index列(central atom)をカラムにする   
df_nnlist_groupbyed = df_nnlist_groupbyed.reset_index() 
# 相対中心座標のDataFrame
df_relative_center = df_nnlist_groupbyed[all_central_atom_filter]


def sum_abs_relative_coords(df_abs=df_coords_abs_center, df_relative=df_relative_center):
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


df_coords_fix = sum_abs_relative_coords(df_abs=df_coords_abs_center, df_relative=df_relative_center)


# write df to poscar
df2poscar(df=df_coords_fix)
