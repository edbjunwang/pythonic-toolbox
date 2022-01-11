def test_dict_until():
    from pythonic_toolbox.utils.dict_utils import dict_until
    data = {'full_name': 'Albert Lee', 'pen_name': None}
    assert dict_until(data, keys=['name', 'full_name']) == 'Albert Lee'
    assert dict_until(data, keys=['full_name', 'name']) == 'Albert Lee'
    assert dict_until(data, keys=['name', 'english_name']) is None
    assert dict_until(data, keys=['name', 'english_name'], default='anonymous') == 'anonymous'
    # test when pen_name is set None on purpose
    assert dict_until(data, keys=['pen_name'], default='anonymous') is None
    # test when value with None value is not acceptable
    assert dict_until(data, keys=['pen_name'], terminate=lambda x: x is not None, default='anonymous') == 'anonymous'


def test_collect_leaves():
    from pythonic_toolbox.utils.dict_utils import collect_leaves
    # a nested dict-like struct
    my_dict = {
        'node_1': {
            'node_1_1': {
                'node_1_1_1': 'A',
            },
            'node_1_2': {
                'node_1_2_1': 'B',
                'node_1_2_2': 'C',
                'node_1_2_3': None,
            },
            'node_1_3': [  # dict list
                {
                    'node_1_3_1_1': 'D',
                    'node_1_3_1_2': 'E',
                },
                {
                    'node_1_3_2_1': 'FF',
                    'node_1_3_2_2': 'GG',
                }
            ]
        }}

    expected = ['A', 'B', 'C', None, 'D', 'E', 'FF', 'GG']
    assert collect_leaves(my_dict) == expected

    expected = ['A', 'B', 'C', 'D', 'E', 'FF', 'GG']
    assert collect_leaves(my_dict, leaf_pred=lambda lf: lf) == expected

    assert collect_leaves(my_dict, keypath_pred=lambda kp: len(kp) == 1) == []

    expected = ['B', 'C']
    assert collect_leaves(my_dict, keypath_pred=lambda kp: kp[-1] in {'node_1_2_1', 'node_1_2_2'}) == expected

    expected = ['C']
    assert collect_leaves(my_dict, leaf_pred=lambda lf: lf == 'C') == expected
    assert collect_leaves(my_dict,
                          keypath_pred=lambda kp: kp[-1] == 'node_1_2_2',
                          leaf_pred=lambda lf: lf == 'C') == expected

    assert collect_leaves(my_dict,
                          keypath_pred=lambda kp: kp[-1] == 'node_1_1_1',
                          leaf_pred=lambda lf: lf == 'C') == []

    expected = ['D', 'E', 'FF', 'GG']
    assert collect_leaves(my_dict,
                          keypath_pred=lambda kp: len(kp) >= 2 and kp[-2] == 'node_1_3') == expected

    expected = ['FF', 'GG']
    assert collect_leaves(my_dict,
                          keypath_pred=lambda kp: len(kp) >= 2 and kp[-2] == 'node_1_3',
                          leaf_pred=lambda lf: isinstance(lf, str) and len(lf) == 2) == expected