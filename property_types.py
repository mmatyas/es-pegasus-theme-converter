import os
import re
from errors import print_error
from static import PropType
from typing import Optional, Union


class NormPair():
    def __init__(self, prop_str):
        fields = prop_str.split(maxsplit=1)
        if len(fields) != 2:
            raise ValueError(f"Invalid normalized pair: `{prop_str}`")

        try:
            self.a, self.b = map(float, fields)
        except ValueError:
            raise ValueError(f"Invalid normalized pair values: `{prop_str}`")

    def __repr__(self):
        return f"{self.__class__.__name__} {{ {self.a}, {self.b} }}"


class NormRect():
    def __init__(self, prop_str):
        fields = prop_str.split(maxsplit=3)
        if len(fields) != 2 or len(fields) != 4:
            raise ValueError(f"Invalid normalized rectangle: `{prop_str}`")

        try:
            if len(fields) == 2:
                self.a, self.b = map(float, fields)
                self.c, self.d = self.a, self.b
            else:
                self.a, self.b, self.c, self.d = map(float, fields)
        except ValueError:
            raise ValueError(f"Invalid normalized rect values: `{prop_str}`")

    def __repr__(self):
        return f"{self.__class__.__name__} {{ {self.a}, {self.b}, {self.c}, {self.d} }}"


class Color():
    def __init__(self, prop_str):
        res = re.match(r'^([0-9a-fA-F]{6})([0-9a-fA-F]{2})?$', prop_str)
        if not res:
            raise ValueError(f"Invalid color value: `{prop_str}`")

        self.hex = prop_str
        self.color = res.group(1)
        if res.group(2):
            self.opacity = int(res.group(2), 16) / 255
        else:
            self.opacity = 1.0

    def __repr__(self):
        return f"#{self.hex}"


Property = Union[NormPair, NormRect, Color, str, float, bool]


def parse_param(basedir: str, prop_type: PropType, prop_str: str) -> Optional[Property]:
    assert(basedir)
    assert(prop_str)
    try:
        if prop_type == PropType.NORMALIZED_PAIR:
            return NormPair(prop_str)
        if prop_type == PropType.NORMALIZED_RECT:
            return NormRect(prop_str)
        if prop_type == PropType.STRING:
            return prop_str
        if prop_type == PropType.PATH:
            return os.path.join(basedir, prop_str)
        if prop_type == PropType.COLOR:
            return Color(prop_str)
        if prop_type == PropType.FLOAT:
            return float(prop_str)
        if prop_type == PropType.BOOLEAN:
            return prop_str.lower()[0] in ['1', 't', 'y']
    except ValueError as err:
        print_error(err)
    return None
