import functools

# Метод, который говорит о том, чтобы разбить анализ данных на несколько процессов,
# а потом результаты этих процессов сложить

def map_frequency(text: str) -> dict[str, int]:
    words = text.split(" ")
    frequencies = {}
    for word in words:
        frequencies[word] = frequencies.get(word, 0) + 1

    return frequencies


def merge_dictionaries(first: dict[str, int], second: dict[str, int]) -> dict[str, int]:
    merged = first

    for key in second:
        merged[key] = merged.get(key, 0) + second.get(key, 0)

    return merged


lines = [
    "I know what I know",
    "I know what I know",
    "I don't know much",
    "They don't know much",
]


mapped_results = [map_frequency(line) for line in lines]
# print(mapped_results)

# for result in mapped_results:
#     print(result)

print(functools.reduce(merge_dictionaries, mapped_results))
