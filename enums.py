from enum import Enum


class Color(Enum):
    Blue = "blue"
    Green = "green"
    Orange = "orange"
    Red = "red"
    Violet = "violet"
    Grey = "grey"
    Rainbow = "rainbow"

    def __str__(self):
        return self.value


class State(Enum):
    New = "New"
    Edited = "Edited"
    Deleted = "Deleted"

    def __str__(self):
        return self.value
