from functools import total_ordering
from itertools import zip_longest


@total_ordering
class Version:
    def __init__(self, version: str):
        self.version = self.transform(version)

    def __eq__(self, other) -> bool:
        return self.__dict__ == other.__dict__

    def __gt__(self, other) -> bool:
        items = zip_longest(self.version, other.version)
        for index, item in enumerate(items, 0):
            if None in item and item[0] is None and index > 2:
                return True
            elif (None not in item and item[0] < item[1]) or (
                    None in item and (item[0] is None or item[0] is not None and index > 2)):
                return False
            elif None not in item and item[0] > item[1]:
                return True
        return True

    def transform(self, patch: str) -> list:
        patch = patch.replace("alpha", "0")
        patch = patch.replace("beta", "1")
        patch = patch.replace("rc", "2")
        patch = patch.replace("-", ".")
        items = patch.split('.')
        for index, item in enumerate(items, 0):
            if not item.isdigit():
                text_num = self.text_num_split(item)
                text_num[1] = str(self.letter_to_num(text_num[1]))
                items = self.insert(items, text_num, index)
        while len(items) < 3:
            items.append('0')
        return items

    def letter_to_num(self, letter) -> int:
        """convert alphabet letter to his index"""
        return ord(letter) - 97

    def text_num_split(self, item: str) -> list:
        """split text to number and letter"""
        for index, letter in enumerate(item, 0):
            if not letter.isdigit():
                return [item[:index], item[index:]]

    def insert(self, items: list, text_num: list, index) -> list:
        """insert number and letter"""
        return items[:index] + text_num


def main():
    to_test = [
        ("1.0.0", "2.0.0"),
        ("1.0.0", "1.42.0"),
        ("1.2.0", "1.2.42"),
        ("1.1.0-alpha", "1.2.0-alpha.1"),
        ("1.0.1b", "1.0.10-alpha.beta"),
        ("1.0.0-rc.1", "1.0.0"),
    ]

    for version_1, version_2 in to_test:
        assert Version(version_1) < Version(version_2), "le failed"
        assert Version(version_2) > Version(version_1), "ge failed"
        assert Version(version_2) != Version(version_1), "neq failed"


if __name__ == "__main__":
    main()
