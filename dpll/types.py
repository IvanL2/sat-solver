from dataclasses import dataclass
from strenum import StrEnum


@dataclass
class Variable:
    name: str

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


@dataclass
class Tautology:
    name: str = "⊤"

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


@dataclass
class Contradiction:
    name: str = "⊥"

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


Atom = Variable | Tautology | Contradiction


class Operator(StrEnum):
    NEGATION = "¬"
    CONJUNCTION = "&"
    DISJUNCTION = "|"
    IMPLICATION = ">"
    EQUIVALENCE = "="
