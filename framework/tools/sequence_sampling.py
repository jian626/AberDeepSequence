from tensorflow.keras.utils import Sequence
import numpy as np
class SequenceGenerator(Sequence):
    def __init__(self, data_manager, batch_size):
        self.data_manager = data_manager
        self.batch_size = batch_size
        x, y = self.data_manager.get_training_data()

        print('Cluster info:')
        print(x['Cluster name'])
        self.len = int(np.floor(len(x) / self.batch_size))

    def __getitem__(self, index):
        x, y = self.data_manager.get_training_data()
        task_num = self.data_manager.get_task_num()
        rx = x[index * self.batch_size : (index + 1) * self.batch_size] 
        ry = []
        for i in range(task_num):
            ry.append(y[i][index * self.batch_size : (index+1) * self.batch_size])
        return rx, ry

    def __len__(self):
        return self.len

    def on_epoch_end(self):
        pass
