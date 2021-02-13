from framework.training.method import training_method_creator as creator
from framework.algorithm import loss_function 
import numpy as np
import gc
import os
from framework.utili import get_table_value

class training_on_batch:
    name = 'training_on_batch'
    def __init__(self, config, context):
        self.config = config
        self.context = context
        log_file = get_table_value(self.config, 'debug_file', None)
        if log_file and os.path.exists(log_file):
              os.remove(log_file)

    def train(self):
        print('=======================train===============================')
        model_manager = self.context['model_manager']
        data_manager = self.context['data_manager']
        model = model_manager.get_model()
        x, y = data_manager.get_training_data()
        batch_size = self.config['batch_size']
        epochs = self.config['epochs']
        period_of_sort = self.config['period_of_sort']
        recomputation_freq_per_epoch = self.config['recomputation_freq_per_epoch']
        ratio_of_recomputation = self.config['ratio_of_recomputation']
        sel = self.config['sel']
        data_len = len(x)
        batch_length = int(np.floor(data_len / batch_size))

        def calculate_prob(loss):
            data_len = len(loss)
            indices = np.argsort(-loss)
            reverse_indices = np.argsort(indices)
            loss_sorted = loss[indices]
            a = []
            epoch_index
            probability = (1 / np.exp(np.log(loss_sorted) / data_len)) ** [x for x in range(1, data_len + 1)]  
            probability = probability / np.sum(probability)
            a.append(probability[0])

            for i in range(1, len(probability)):
                a.append(a[i-1] + probability[i])
            return a, probability, indices, reverse_indices

        step_index = 0

        print('batch_length:',batch_length)
        print('epochs:', epochs)
        for epoch_index in range(epochs):
            print('==============epoch:=======================', epoch_index)
            predicted = model.predict(x)[3]
            loss = loss_function.binary_entropy(y[3], predicted)
            a, probability, indices, reverse_indices = calculate_prob(loss)

            for batch_index in range(batch_length): 
                if step_index % period_of_sort == 0:
                    indices = np.argsort(loss)
                    reverse_indices = np.argsort(indices)

                if step_index % recomputation_freq_per_epoch == 0: 
                    ids = indices[:int(data_len * ratio_of_recomputation)]
                    r_x = x[ids]
                    r_y = y[3][ids]
                    r_predicted = predicted[ids]
                    r_loss = loss_function.binary_entropy(r_y, r_predicted)
                    loss[ids] = r_loss
                    indices = np.argsort(loss)
                    reverse_indices = np.argsort(indices)

                def select(batch_size, reverse_indices, a):
                    res = []
                    al = len(a)
                    for _ in range(batch_size):
                        r = np.random.random_sample()

                        begin = 0
                        end = al
                        mid = (begin + end) // 2
                        while begin < end:
                            if r <= a[mid]:
                                end = mid
                            else:
                                begin = mid + 1
                            mid = (begin + end) // 2
                        if mid == al:
                            mid -= 1 #to handle suspecious float point problem

                        res.append(reverse_indices[mid])
                    return res

                res = select(batch_size, reverse_indices, a)

                y_ = []

                for i in range(4):
                    y_.append(y[i][res])

                z = x[res]
                model.train_on_batch(z, y_)
                log_file = get_table_value(self.config, 'debug_file', None)
                log_colums = get_table_value(self.config, 'log_colums', None)

                if log_file:
                    training_set, _ = data_manager.get_training_and_test_set()
                    training_set.iloc[res][log_colums].to_csv(log_file, mode='a', sep='\t')

                step_index += 1
            #gc.collect()

def create(config, context):
    return training_on_batch(config, context)

creator.instance.register(training_on_batch.name, create)
