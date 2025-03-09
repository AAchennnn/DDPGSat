import os
import shutil

def delete_subfolders(directory):
    # 遍历目录中的所有文件和文件夹
    for folder_name in os.listdir(directory):
        folder_path = os.path.join(directory, folder_name)
        # 确保它是一个文件夹
        if os.path.isdir(folder_path):
            # 删除文件夹及其内容
            shutil.rmtree(folder_path)

delete_subfolders(r"D:\Datas_cxy")