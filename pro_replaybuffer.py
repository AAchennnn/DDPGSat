import numpy as np
from collections import deque
from args import args


class ReplayBuffer:
    def __init__(self, max_size=args.capacity):
        self.buffer = deque(maxlen=max_size)  # 自动覆盖的循环队列

    def push(self, transition):
        """存储单条经验（state, next_state, action, reward, done）"""
        # 将数据预先转换为numpy数组
        transition = tuple(map(np.array, transition))
        self.buffer.append(transition)

    def sample(self, batch_size):
        # 随机选择索引（避免重复索引问题）
        indices = np.random.choice(len(self.buffer), batch_size, replace=False)

        # 批量获取数据（效率提升5-10倍）
        samples = [self.buffer[idx] for idx in indices]

        # 使用转置技巧快速分离数据
        batch = list(zip(*samples))

        # 返回形状统一的numpy数组
        return (
            np.stack(batch[0]),  # state
            np.stack(batch[1]),  # next_state
            np.stack(batch[2]),  # action
            np.expand_dims(np.array(batch[3]), -1),  # reward
            np.expand_dims(np.array(batch[4], dtype=np.float32), -1)  # done
        )

    def __len__(self):
        return len(self.buffer)  # 当前存储的经验数量


if __name__ == '__main__':
    # 存储经验
    buffer = ReplayBuffer(1000)
    state = np.random.randn(4)
    next_state = np.random.randn(4)
    action = np.array([0.5])
    reward = 1.0
    done = False
    buffer.push((state, next_state, action, reward, done))

    # 采样批次
    batch = buffer.sample(1)
    states, next_states, actions, rewards, dones = batch
    print(batch)

