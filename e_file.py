import os

class e_file_get():
    def __init__(self,n):
        self.n = n
    def get(self):
        root_dir = "D:/Datas_cxy"
        files_all=[]
        # 循环遍历文件夹及其子文件夹
        for subdir, dirs, files in os.walk(root_dir):
            # 只处理以 "0" 开头的子文件夹
            if os.path.basename(subdir).startswith(f"{self.n}"):
                for file in files:
                    # 判断文件扩展名是否为.e
                    if file.endswith(".e"):
                        # 获取文件的完整路径
                        file_path = os.path.join(subdir, file)
                        files_all.append(file_path)
        return files_all



