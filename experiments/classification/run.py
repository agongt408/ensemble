import os

# Toy dataset

# for num_classes in [200]:
#     for samples_per_class in [400]:
#         cmd = 'python experiments/classification/baseline.py ' + \
#             '--architecture fcn ' + \
#             '--dataset toy --epochs 15 --trials 8 ' + \
#             '--num_classes ' + str(num_classes) + ' ' + \
#             '--samples_per_class ' + str(samples_per_class)
#         os.system(cmd)
#
#         for num_branches in range(6, 7):
#             model_id_list = ''
#             for i in range(num_branches):
#                 model_id_list += '%d ' % (i+1)
#
#             cmd = 'python experiments/classification/baseline.py ' + \
#                 '--architecture fcn ' + \
#                 '--dataset toy --trials 8 ' + \
#                 '--num_classes ' + str(num_classes) + ' ' + \
#                 '--samples_per_class ' + str(samples_per_class) + ' ' + \
#                 '--test --model_id ' + model_id_list
#             os.system(cmd)
#
#             for shared_frac in [0., 0.25, 0.5, 0.75, 1.]:
#                 cmd = 'python experiments/classification/vbranch.py ' + \
#                     '--architecture fcn ' + \
#                     '--dataset toy --epochs 15 --trials 4 ' + \
#                     '--num_classes ' + str(num_classes) + ' ' + \
#                     '--samples_per_class ' + str(samples_per_class) + ' ' + \
#                     '--num_branches ' + str(num_branches) + ' ' + \
#                     '--shared_frac ' + str(shared_frac)
#                 os.system(cmd)

# # MNIST
#
# cmd = 'python experiments/classification/baseline.py ' + \
#     '--architecture fcn --dataset mnist --epochs 15 --trials 8'
# os.system(cmd)
#
# for num_branches in range(2, 7):
#     model_id_list = ''
#     for i in range(num_branches):
#         model_id_list += '%d ' % (i+1)
#
#     cmd = 'python experiments/classification/baseline.py ' + \
#         '--architecture fcn --dataset mnist ' + \
#         '--test --trials 8 --model_id ' + model_id_list
#     os.system(cmd)
#
#     for shared_frac in [0, 0.25, 0.5, 0.75, 1]:
#         cmd = 'python experiments/classification/vbranch.py ' + \
#             '--architecture fcn2 ' + \
#             '--dataset mnist --epochs 15 --trials 8 ' + \
#             '--num_branches ' + str(num_branches) + ' ' + \
#             '--shared_frac ' + str(shared_frac)
#         os.system(cmd)

# for train_frac in [0.05, 0.1, 0.2]:
#     for batch_size in [8, 16, 32, 64, 128]:
#         baseline_path = os.path.join('data_exp-2/mnist-fcn',
#             'F{:.2f}'.format(train_frac), 'Ba{}'.format(batch_size))
#
#         cmd = 'python experiments/classification/baseline.py ' + \
#             '--architecture fcn --dataset mnist --epochs 10 --trials 8 ' + \
#             '--train_frac {} --batch_size {} '.format(train_frac, batch_size) + \
#             '--path ' + baseline_path
#         os.system(cmd)
#
#         for num_branches in range(2, 7):
#             model_id_list = ''
#             for i in range(num_branches):
#                 model_id_list += '%d ' % (i+1)
#
#             cmd = 'python experiments/classification/baseline.py ' + \
#                 '--architecture fcn --dataset mnist --test --trials 8 ' + \
#                 '--path ' + baseline_path + ' --model_id ' + model_id_list
#             os.system(cmd)
#
#             vb_path = os.path.join('data_exp-2/vb-mnist-fcn',
#                 'F{:.2f}'.format(train_frac), 'Ba{}'.format(batch_size))
#
#             for shared_frac in [0., 0.25, 0.5, 0.75, 1.]:
#                 cmd = 'python experiments/classification/vbranch.py ' + \
#                     '--architecture fcn --dataset mnist --epochs 10 --trials 8 ' + \
#                     '--train_frac {} --batch_size {} '.format(train_frac, batch_size) + \
#                     '--num_branches ' + str(num_branches) + ' ' + \
#                     '--shared_frac ' + str(shared_frac) + ' ' + \
#                     '--path ' + vb_path
#                 os.system(cmd)

ARCHITECTURE = 'fcn'

for bagging in [0.4, 0.6, 0.8, 1.0]:
    for batch_size in [32, 64, 96, 128, 160]:
        baseline_path = f'bagging-3/mnist-{ARCHITECTURE}/Bg{bagging}/Ba{batch_size}'

        cmd = f'python experiments/classification/baseline.py ' \
            f'--architecture {ARCHITECTURE} --dataset mnist --trials 8 ' \
            f'--path {baseline_path} --batch_size {batch_size} --epochs 50'
        os.system(cmd)

        for num_branches in range(2, 5):
            model_id_list = ''
            for i in range(num_branches):
                model_id_list += '%d ' % (i+1)

            cmd = f'python experiments/classification/baseline.py ' \
                f'--architecture fcn --dataset mnist --test --trials 8 ' \
                f'--path {baseline_path} --model_id {model_id_list}'
            os.system(cmd)

            vb_path = f'bagging-3/vb-mnist-{ARCHITECTURE}/Bg{bagging}/Ba{batch_size}'

            for shared_frac in [0., 0.25, 0.5, 0.75, 1.]:
                cmd = f'python experiments/classification/vbranch.py ' \
                    f'--architecture fcn --dataset mnist --trials 8 ' \
                    f'--num_branches {num_branches} --shared_frac {shared_frac} ' \
                    f'--bagging {bagging} --path {vb_path} --bootstrap ' \
                    f'--batch_size {batch_size} --epochs 50'
                os.system(cmd)
