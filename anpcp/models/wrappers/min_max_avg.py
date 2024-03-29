from dataclasses import dataclass


@dataclass
class MinMaxAvg:
    """
    Just wraps these 3 stastical attributes.
    """

    minimum: float
    maximum: float
    average: float

    def to_tuple(self):
        return (self.minimum, self.maximum, self.average)
