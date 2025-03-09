from datetime import datetime
class EphemerisDataExtractor:
    def __init__(self, file_path):
        self.file_path = file_path

    def extract_initial_position_velocity(self):
        """
        提取文件中的初始时间（t=0）对应的位置和速度信息
        """
        # 打开并读取文件内容
        with open(self.file_path, 'r') as file:
            file_contents = file.readlines()

        # 查找包含位置和速度的部分（EphemerisTimePosVel）
        start_data = False
        initial_position_velocity = None
        for line in file_contents:
            if line.startswith("EphemerisTimePosVel"):
                start_data = True  # 开始读取数据行
            elif start_data:
                if line.strip() == "":  # 跳过空行
                    continue
                # 提取数据行，去除空白并分割
                initial_position_velocity = line.strip().split()
                break  # 只读取第一行数据

        # 返回初始时间的位置和速度数据
        if initial_position_velocity:
            time = float(initial_position_velocity[0])
            x = float(initial_position_velocity[1])/1000
            y = float(initial_position_velocity[2])/1000
            z = float(initial_position_velocity[3])/1000
            vx = float(initial_position_velocity[4])/1000
            vy = float(initial_position_velocity[5])/1000
            vz = float(initial_position_velocity[6])/1000

            return x,y,z,vx,vy,vz

    def extract_scenario_epoch(self):
        """
        提取文件中的 ScenarioEpoch 的值
        """
        with open(self.file_path, 'r') as file:
            file_contents = file.readlines()

        for line in file_contents:
            if line.startswith("ScenarioEpoch"):
                # 提取 ScenarioEpoch 后面的时间值
                scenario_epoch = line.split("\t")[1].strip()
                time_str = scenario_epoch
                time_obj = datetime.strptime(time_str[:20], "%d %b %Y %H:%M:%S")
                midnight = datetime.strptime("12 Jan 2025 00:00:00", "%d %b %Y %H:%M:%S")
                seconds_since_midnight = (time_obj - midnight).total_seconds()
                return scenario_epoch, seconds_since_midnight

