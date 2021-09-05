from typing import Any, Callable, List, TypeVar, Type, Optional
import time
import jsonpickle # type: ignore

#############################################
# Type Variables for Generics
T = TypeVar('T')

#############################################
# Time Utils
def get_time_ms() -> int:
    return time.time_ns() // 1_000_000 

#############################################
# Number Utils
def limit_int(current_value: int, min_value: Optional[int], max_value: Optional[int]) -> int:
    if (min_value is not None and current_value < min_value):
        return min_value
    if (max_value is not None and current_value > max_value):
        return max_value
    return current_value

def limit_float(current_value: float, min_value: Optional[float], max_value: Optional[float]) -> float:
    if (min_value is not None and current_value < min_value):
        return min_value
    if (max_value is not None and current_value > max_value):
        return max_value
    return current_value

#############################################
# JSON Utils
def to_json(obj: Any, pretty_print: bool = False) -> str:
    indent = 4 if pretty_print else None
    return jsonpickle.encode(obj, indent=indent) # type: ignore
    
def from_json(json_string: str, _: Type[T]) -> T:
    return jsonpickle.decode(json_string) # type: ignore

#############################################
# List Utils
def get_elements_except(all_elements: List[T], elements_to_exclude: List[T]) -> List[T]:
    return [x for x in all_elements if x not in elements_to_exclude]

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

#############################################
# List Predicates
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