import re


class Version:
    def __init__(self, version: str):
        self.major, self.minor, *self.patch = tuple([int(x) for x in Version.transform(version).split('.')])

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if self.major > other.major:
            return True
        elif self.major == other.major:
            if self.minor > other.minor:
                return True
            elif self.minor == other.minor:
                if self.patch[0] == other.patch[0]:
                    if len(self.patch) == 1 and len(other.patch) > 1:
                        return True
                    elif len(other.patch) == 1 and len(self.patch) > 1:
                        return False
                    elif len(other.patch) == 1 and len(self.patch) == 1:
                        return False
                min, max = (self.patch, other.patch) if len(self.patch) < len(other.patch) else (
                    other.patch, self.patch)
                while len(min) < len(max):
                    min.append(0)
                return self.patch > other.patch
        return False

    def __lt__(self, other):
        return not self.__gt__(other) and not self.__eq__(other)

    @staticmethod
    def transform(patch: str):
        patch = patch.replace("alpha", "0")
        patch = patch.replace("beta", "1")
        patch = patch.replace("rc", "2")
        patch = patch.replace("-", ".")
        result = re.search(r'[0-9]+([a-z]{1})$', patch)
        if result:
            patch = patch.replace(result.group(0), result.group(0)[:-1] + f'.{(ord(result.group(0)[-1]) - 96)}')
        return patch


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
