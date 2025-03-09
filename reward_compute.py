import numpy as np


class EscapeSatelliteReward:
    def __init__(
            self,
            # 环境参数
            safe_distance: float = 1000.0,  # 安全距离阈值（米）
            capture_radius: float = 500.0,  # 捕获判定半径（米）
            #max_steps: int = 1000,  # 最大存活时间步
            earth_min_altitude: float = 160.0,  # 最低地球安全高度（km）
            max_time: float = 43200,
            # 奖励参数
            base_survival: float = 2.0,  # 基础存活奖励（大幅提升）
            distance_decay: float = 0.005,  # 距离衰减系数
            velocity_align: float = 1.2,  # 速度对齐奖励系数（增强方向引导）
            earth_penalty: float = 80.0,  # 地球接近惩罚（提高安全性）
            capture_penalty: float = 1000.0,  # 被捕获惩罚
            proximity_penalty: float = 0.1,  # 近距离持续惩罚
            time_complete: float = 500,
    ):
        # 环境参数初始化
        self.safe_dist = safe_distance
        self.capture_radius = capture_radius
        #self.max_steps = max_steps
        self.earth_min = earth_min_altitude
        self.max_time = max_time
        # 奖励参数初始化
        self.base_survival = base_survival
        self.distance_decay = distance_decay
        self.velocity_align = velocity_align
        self.earth_penalty = earth_penalty
        self.capture_penalty = capture_penalty
        self.proximity_penalty = proximity_penalty
        self.time_complete = time_complete
        # 状态跟踪
        self.current_step = 0
        self.best_distance = 0.0  # 历史最远距离记录
        self.danger_duration = 0  # 处于危险区域的连续时间步

    def reset(self):
        """环境重置时需要更新的参数"""
        self.current_step = 0
        self.best_distance = 0.0
        self.danger_duration = 0

    def calculate_reward(
            self,
            relative_positions: list,  # 所有追踪器相对位置矢量列表
            distances: list,  # 对应距离列表
            relative_velocities: list,  # 所有追踪器相对速度矢量
            min_to_earth: float,  # 距地球最近高度（km）
            current_time: float
            #is_orbit_safe: bool  # 轨道是否安全（避免坠毁）
    ) -> (float, bool, dict):
        """
        新版奖励函数核心设计：
        1. 指数增长的存活奖励 - 鼓励长期生存
        2. 动态距离记录系统 - 鼓励创造新的安全距离
        3. 连续危险区域惩罚 - 防止在危险边缘徘徊
        4. 速度方向强化引导 - 加速逃离趋势
        5. 地球安全区保护 - 确保轨道安全
        """
        self.current_step += 1
        done = False
        info = {"terminate_reason": None}
        rewards = {}

        # ========== 核心奖励项 ==========#
        # 指数型存活奖励（随时间加速增长）
        rewards["survival"] = self.base_survival * (np.exp(0.002 * self.current_step) - 1)

        # 动态距离奖励系统
        current_min_dist = min(distances)
        if current_min_dist > self.best_distance:
            delta_dist = current_min_dist - self.best_distance
            rewards["distance_record"] = delta_dist * self.distance_decay
            self.best_distance = current_min_dist
            self.danger_duration = 0  # 刷新安全记录重置危险计时
        else:
            # 持续危险区域惩罚
            if current_min_dist < self.safe_dist:
                self.danger_duration += 1
                penalty = self.proximity_penalty * (self.safe_dist - current_min_dist) * np.sqrt(self.danger_duration)
                rewards["proximity_penalty"] = -penalty

        # ========== 速度方向奖励 ==========#
        velocity_reward = 0.0
        for pos_vec, vel_vec in zip(relative_positions, relative_velocities):
            # 计算速度在逃离方向上的投影
            escape_direction = -pos_vec / (np.linalg.norm(pos_vec) + 1e-6)
            velocity_projection = np.dot(vel_vec, escape_direction)

            # 非线性奖励：平方关系强化有效逃离
            velocity_reward += np.sign(velocity_projection) * (abs(velocity_projection)) ** 1.5

        rewards["velocity_align"] = self.velocity_align * (velocity_reward / len(relative_positions))

        # ========== 地球安全保护 ==========#
        if min_to_earth < self.earth_min:
            altitude_ratio = (self.earth_min - min_to_earth) / self.earth_min
            rewards["earth_penalty"] = -self.earth_penalty * (altitude_ratio ** 2)

        #if not is_orbit_safe:
            #rewards["orbit_penalty"] = -self.earth_penalty * 3
            #done = True
            #info["terminate_reason"] = "unsafe_orbit"

        # ========== 终止条件 ==========#
        # 被捕获判定
        if current_min_dist <= self.capture_radius:
            rewards["capture"] = -self.capture_penalty
            done = True
            info["terminate_reason"] = "captured"

        # 成功存活到max_steps（重大成功）
        if current_time >= self.max_time:
            done = True
            info["terminate_reason"] = "mission_complete"
            rewards["success_bonus"] = self.time_complete


        # ========== 奖励汇总 ==========#
        total_reward = sum(rewards.values())
        return total_reward, done, info


# 测试案例
if __name__ == "__main__":
    reward_system = EscapeSatelliteReward()

    # 理想规避场景测试
    good_case = {
        "relative_positions": [np.array([2000, 300, 0]), np.array([1800, 500, 100])],
        "distances": [2030.0, 1870.0],
        "relative_velocities": [np.array([-15, 0, 0]), np.array([-12, -5, 2])],
        "min_to_earth": 300.0,
        'current_time':43200
    }

    # 危险场景测试
    danger_case = {
        "relative_positions": [np.array([600, 0, 0]), np.array([550, 100, 0])],
        "distances": [600.0, 560.0],
        "relative_velocities": [np.array([10, 0, 0]), np.array([8, 0, 0])],  # 错误方向
        "min_to_earth": 150.0,
        #"is_orbit_safe": False
        'current_time': 23200
    }

    print("=== 良好规避场景 ===")
    total_reward, done, info = reward_system.calculate_reward(**good_case)
    print(total_reward)
    print(f"Total Reward: {total_reward:.2f}")
    print(f"Termination: {done}, Reason: {info['terminate_reason']}")

    print("\n=== 危险场景测试 ===")
    reward_system.reset()
    total_reward, done, info = reward_system.calculate_reward(**danger_case)
    print(f"Total Reward: {total_reward:.2f}")
    print(f"Termination: {done}, Reason: {info['terminate_reason']}")
