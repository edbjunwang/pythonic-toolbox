import json
from collections import defaultdict
from typing import List, Iterable, Union, Optional, Callable, TypeVar, Any, Tuple, DefaultDict, Hashable

from funcy import first, identity

T = TypeVar("T")
D = TypeVar("D")  # type for default value


def sort_with_custom_orders(values: List[T],
                            prefix_orders: Optional[List[T]] = None,
                            suffix_orders: Optional[List[T]] = None,
                            key: Optional[Callable[[T], Any]] = None,
                            hash_fun: Optional[Callable] = None,
                            reverse: bool = False) -> List[T]:
    class Empty:
        pass

    UNSIGNED = Empty()

    if prefix_orders is None:
        prefix_orders = []

    if suffix_orders is None:
        suffix_orders = []

    if not isinstance(prefix_orders, list):
        raise ValueError('prefix_orders should be a list if provided')

    if not isinstance(suffix_orders, list):
        raise ValueError('suffix_orders should be a list if provided')

    default_hash_fun = json.dumps

    if key is None:
        key = identity

    value_types = set(map(type, values))
    value_types.update(set(map(type, prefix_orders)))
    value_types.update(set(map(type, suffix_orders)))
    if len(value_types) > 1:
        raise ValueError('multi types provided in values, prefix_orders, suffix_orders')

    samples = filter(lambda x: x is not UNSIGNED, [first(values)] + [first(prefix_orders)] + [first(suffix_orders)])
    sample = first(samples)

    if sample is UNSIGNED:
        # nothing provided in values, prefix_orders, suffix_orders
        return []

    is_value_type_hashable = True
    try:
        # judge if value type is hashable on runtime
        {sample: None}
    except TypeError:
        is_value_type_hashable = False

    if is_value_type_hashable:
        _hash_fun = hash_fun or identity
    else:
        if hash_fun is not None:
            _hash_fun = hash_fun
        else:
            _hash_fun = default_hash_fun
    hash_fun = _hash_fun

    prefix_orders = list(prefix_orders)
    prefix_orders_set = set(map(hash_fun, prefix_orders))

    if len(prefix_orders) != len(prefix_orders_set):
        raise ValueError('prefix_orders contains duplicated values')

    suffix_orders = list(suffix_orders)
    suffix_orders_set = set(map(hash_fun, suffix_orders))

    if len(suffix_orders) != len(suffix_orders_set):
        raise ValueError('suffix_orders contains duplicated values')

    if prefix_orders_set.intersection(suffix_orders_set):
        raise ValueError('prefix and suffix contains same value')

    order_map: DefaultDict[Hashable, int] = defaultdict(lambda: 1)
    for idx, item in enumerate(prefix_orders):
        order_map[_hash_fun(item)] = idx - len(prefix_orders)

    for idx, item in enumerate(suffix_orders, start=2):
        order_map[_hash_fun(item)] = idx

    def key_func(x: T) -> Tuple[int, Any]:
        return order_map[hash_fun(x)], key(x)

    sorted_values = sorted(values, key=key_func, reverse=reverse)

    return sorted_values


def until(values: Optional[Union[List[T], Iterable]],
          terminate: Optional[Callable[[T], bool]] = None,
          default: Optional[D] = None) -> Optional[Union[T, D]]:
    class Empty:
        pass

    UNSIGNED = Empty()

    def default_terminate(v: Any) -> bool:
        return v is not UNSIGNED

    if values is None:
        return default

    if terminate is None:
        terminate = default_terminate

    if isinstance(values, (list, Iterable)):
        for value in values:
            if terminate(value):
                return value
        else:
            pass
        return default
    else:
        raise ValueError('values type should be list, Iterable')


def unpack_list(source: List[Any], target_num: int, default: Optional[Any] = None) -> List[Any]:
    return [*source, *([default] * (target_num - len(source)))] if len(source) < target_num else source[:target_num]
