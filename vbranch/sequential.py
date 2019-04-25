# Declare models sequentially

from . import layers as L
from . import vb_layers as VBL
from . import utils

import tensorflow as tf
import numpy as np

class Sequential(object):
    def __init__(self, input_tensor):
        """
        Args:
            - input_tensor: single Tensor"""

        self.input = input_tensor
        self.layers = []
        self.output = input_tensor

    def add(self, layer):
        self.layers.append(layer)
        self.output = layer(self.output)

    def summary(self):
        model_summary = utils.Summary('i', 'Layer name', 'Output shape',
            'Parameters', 'Num param')

        total_num_params = 0

        # Input spec
        model_summary.add('','Input',utils.get_shape_as_str(self.input),'','')

        for i, l in enumerate(self.layers):
            config = l.get_config()
            name = config['name']
            output_shape = utils.shape_to_str(config['output_shape'])

            num_params = 0
            param_shapes = ''
            if 'weights' in config.keys():
                for weight in config['weights']:
                    num_params += utils.get_num_params(weight)
                    param_shapes += utils.get_shape_as_str(weight) + ' '

            model_summary.add(i, name, output_shape, param_shapes, num_params)
            total_num_params += num_params

        model_summary.show()

        print('Total parameters: {:d}'.format(total_num_params))

class SequentialVB(object):
    def __init__(self, inputs):
        """
        Args:
            - inputs: single Tensor or list of Tensors"""

        self.input = inputs
        self.layers = []
        self.output = inputs

    def add(self, layer):
        self.layers.append(layer)
        self.output = layer(self.output)

    def summary(self):
        model_summary = utils.Summary('i', 'Layer name', 'Output shapes',
            'Num param')

        total_num_params = 0

        # Input spec
        if type(self.input) is list:
            for ip in self.input:
                model_summary.add('', 'Input', utils.get_shape_as_str(ip), '')
        else:
            model_summary.add('','Input',utils.get_shape_as_str(self.input),'')

        for i, l in enumerate(self.layers):
            config = l.get_config()
            name = config['name']

            num_params = 0
            if 'weights' in config.keys():
                for weight in config['weights']:
                    if weight != []:
                        num_params += utils.get_num_params(weight)
            total_num_params += num_params

            num_outputs = len(config['output_shapes'])
            for b in range(num_outputs):
                output_shape = ''
                for shape in config['output_shapes'][b]:
                    output_shape += utils.shape_to_str(shape) + ' '

                if b == 0:
                    model_summary.add(i, name, output_shape, num_params,
                        show_line=b==num_outputs-1)
                else:
                    model_summary.add('', '', output_shape, '',
                        show_line=b==num_outputs-1)

        model_summary.show()

        print('Total parameters: {:d}'.format(total_num_params))

def simple_fcn(input_tensor, *layers_spec):
    # NOTE: input_tensor is a single Tensor object

    model = Sequential(input_tensor)

    for i, units in enumerate(layers_spec):
        model.add(L.Dense(units, 'fc'+str(i + 1)))
        model.add(L.BatchNormalization('bn'+str(i + 1)))

        activation_name = 'relu'+str(i+1) if i<len(layers_spec)-1 else 'output'
        model.add(L.Activation('relu', activation_name))

    return model

def simple_cnn(input_tensor, num_classes, *layers_spec):
    # NOTE: input_tensor is a single Tensor object

    model = Sequential(input_tensor)

    for i, filters in enumerate(layers_spec):
        for l in range(2):
            model.add(L.Conv2D(filters, 3, 'conv2d_%d_%d' % (i+1, l+1)))
            model.add(L.BatchNormalization('bn_%d_%d' % (i + 1, l+1)))
            model.add(L.Activation('relu', 'relu_%d_%d' % (i+1, l+1)))

        if i < len(layers_spec) - 1:
            model.add(L.AveragePooling2D((2,2), 'avg_pool2d_'+str(i + 1)))
        else:
            model.add(L.GlobalAveragePooling2D('global_avg_pool2d'))

            # Embedding layers
            model.add(L.Dense(layers_spec[-1], 'fc1'))
            model.add(L.BatchNormalization('bn_fc1'))
            model.add(L.Activation('relu', 'relu_fc1'))
            model.add(L.Dense(num_classes, 'output'))

    return model

def vbranch_fcn(inputs, *layers_spec, branches=1):
    # NOTE: inputs can be single Tensor or list of Tensors
    model = SequentialVB(inputs)

    for i, (units_list, shared_units) in enumerate(layers_spec):
        model.add(VBL.Dense(units_list,branches,'fc'+str(i + 1), shared_units))
        model.add(VBL.BatchNormalization(branches, 'bn'+str(i + 1)))

        activation_name = 'relu'+str(i + 1) if (i < len(layers_spec) - 1 or \
            layers_spec[-1][-1] > 0) else 'output'
        model.add(VBL.Activation('relu', branches, activation_name))

    # If using shared params
    if layers_spec[-1][-1] > 0:
        model.add(VBL.MergeSharedUnique(branches, 'output'))

    return model

def vbranch_cnn(inputs, final_spec, *layers_spec, branches=1):
    """
    CNN model for classification and one-shot learning
    Args:
        - inputs: single Tensor or list of Tensors
        - final_spec: tuple of (num_classes, shared_units)
        - layers_spec: tuple(s) of (filters_list, shared_filters)
        - branches: number of branches
    """

    model = SequentialVB(inputs)

    for i, (filters_list, shared_filters) in enumerate(layers_spec):
        for l in range(2):
            model.add(VBL.Conv2D(filters_list,3,branches,
                'conv2d_%d_%d'%(i+1,l+1),shared_filters))
            model.add(VBL.BatchNormalization(branches,'bn_%d_%d' % (i+1, l+1)))
            model.add(VBL.Activation('relu',branches,'relu_%d_%d' % (i+1, l+1)))

        if i < len(layers_spec) - 1:
            model.add(VBL.AveragePooling2D((2,2),branches,'avg_pool2d_'+str(i+1)))
        else:
            model.add(VBL.GlobalAveragePooling2D(branches,'global_avg_pool2d'))

            # Embedding layers
            model.add(VBL.Dense(layers_spec[-1][0],branches,'fc1',layers_spec[-1][1]))
            model.add(VBL.BatchNormalization(branches, 'bn_fc1'))
            model.add(VBL.Activation('relu', branches, 'relu_fc1'))

            # If using shared params
            if final_spec[1] > 0:
                model.add(VBL.Dense([final_spec[0]]*branches,branches,'fc2',
                                    final_spec[1]))
                model.add(VBL.MergeSharedUnique(branches, 'output'))
            else:
                model.add(VBL.Dense([final_spec[0]]*branches,branches,'output',
                                    final_spec[1]))

    return model
