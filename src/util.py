import time
from typing import Any, Callable, List, TypeVar

T = TypeVar('T')

def get_time_ms() -> int:
    return time.time_ns() // 1_000_000 

def get_elements_except(all_elements: List[T], elements_to_exclude: List[T]) -> List[T]:
    return [x for x in all_elements if not x in elements_to_exclude]

def get_min_element(elements: List[T], element_to_value: Callable[[T], float]) -> T:
    if not elements:
        return None # type: ignore

    min_element = elements[0]
    min_element_value = element_to_value(min_element)
    for element in elements:
        element_value = element_to_value(element)
        if (element_value < min_element_value):
            min_element = element
            min_element_value = element_value
    return min_element

def get_max_element(elements: List[T], element_to_value: Callable[[T], float]) -> T:
    if not elements:
        return None # type: ignore

    max_element = elements[0]
    max_element_value = element_to_value(max_element)
    for element in elements:
        element_value = element_to_value(element)
        if (element_value > max_element_value):
            max_element = element
            max_element_value = element_value
    return max_element

def all_increasing(elements: List[T], element_to_value: Callable[[T], float]) -> bool:
    if not elements:
        return True
    
    previous_element_value = element_to_value(elements[0])
    for i in range(1, len(elements)):
        element_value = element_to_value(elements[i])
        if previous_element_value > element_value: 
            return False
        previous_element_value = element_value

    return True

def all_decreasing(elements: List[T], element_to_value: Callable[[T], float]) -> bool:
    if not elements:
        return True
    
    previous_element_value = element_to_value(elements[0])
    for i in range(1, len(elements)):
        element_value = element_to_value(elements[i])
        if previous_element_value < element_value: 
            return False
        previous_element_value = element_value
        
    return True