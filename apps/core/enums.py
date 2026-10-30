from enum import Enum


class LabeledEnum(str, Enum):
    """A string enum where each member also carries a human label (pt-BR, for the UI).

    Pure Python on purpose: domain code can use it without importing Django.
    Django model fields take their choices from `choices()`.
    """

    label: str

    def __new__(cls, value, label):
        member = str.__new__(cls, value)
        member._value_ = value
        member.label = label
        return member

    @classmethod
    def choices(cls):
        return [(member.value, member.label) for member in cls]

    @classmethod
    def values(cls):
        return [member.value for member in cls]
