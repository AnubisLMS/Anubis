import difflib
import string
import random
from typing import Callable, Iterable, TypeVar

T = TypeVar("T")

def rand_swap(collection: Iterable[T], swap_probability: float, generator_func: Callable[[T], T]) -> Iterable[T]:
    return [generator_func(item) if random.random() < swap_probability else item for item in collection]

rand_text = lambda: "".join(random.choices(string.ascii_letters, k=random.randint(10, 50)))
rand_lines = lambda n: [rand_text() for _ in range(n)]
swap_text = lambda text: "".join(rand_swap(text, 0.1, lambda _: random.choice(string.ascii_letters)))
swap_lines = lambda lines: rand_swap(lines, 0.1, swap_text)

diffs = []

for i in range(10):
    expected_output = rand_lines(i * 100) 
    actual_output = swap_lines(expected_output) + rand_lines(5)
    diffs.append("\n".join(difflib.unified_diff(expected_output, actual_output, lineterm="")))

rand_diff = lambda: random.choice(diffs)
