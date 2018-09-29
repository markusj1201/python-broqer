""" This module enables the operator overloading of publishers """
import asyncio
import operator
import math
from typing import Any

from broqer import Publisher
from broqer.op.operator import Operator


class _MapConstant(Operator):
    def __init__(self, publisher: Publisher, value, operation) -> None:
        Operator.__init__(self)
        self._value = value
        self._operation = operation
        self._publisher = publisher

    def get(self):
        return self._operation(self._publisher.get(), self._value)

    def emit(self, value: Any, who: Publisher) -> asyncio.Future:
        assert who is self._publisher, 'emit from non assigned publisher'

        result = self._operation(value, self._value)

        return self.notify(result)


class _MapConstantReverse(Operator):
    def __init__(self, publisher: Publisher, value, operation) -> None:
        Operator.__init__(self)
        self._value = value
        self._operation = operation
        self._publisher = publisher

    def get(self):
        return self._operation(self._value, self._publisher.get())

    def emit(self, value: Any, who: Publisher) -> asyncio.Future:
        assert who is self._publisher, 'emit from non assigned publisher'

        result = self._operation(self._value, value)

        return self.notify(result)


class _MapUnary(Operator):
    def __init__(self, publisher: Publisher, operation) -> None:
        Operator.__init__(self)
        self._operation = operation
        self._publisher = publisher

    def get(self):
        return self._operation(self._publisher.get())

    def emit(self, value: Any, who: Publisher) -> asyncio.Future:
        assert who is self._publisher, 'emit from non assigned publisher'

        result = self._operation(value)

        return self.notify(result)


def apply_operator_overloading():
    """ Function to apply operator overloading to Publisher class """
    # operator overloading is (unfortunately) not working for the following
    # cases:
    # int, float, str - should return appropriate type instead of a Publisher
    # len - should return an integer
    # "x in y" - is using __bool__ which is not working with Publisher
    for method in (
            '__lt__', '__le__', '__eq__', '__ne__', '__ge__', '__gt__',
            '__add__', '__and__', '__lshift__', '__mod__', '__mul__',
            '__pow__', '__rshift__', '__sub__', '__xor__', '__concat__',
            '__getitem__', '__floordiv__', '__truediv__'):
        def _op(operand_left, operand_right, operation=method):
            from broqer.op import CombineLatest

            if isinstance(operand_right, Publisher):
                return CombineLatest(operand_left, operand_right,
                                     map_=getattr(operator, operation))
            return _MapConstant(operand_left, operand_right,
                                getattr(operator, operation))

        setattr(Publisher, method, _op)

    for method, _method in (
            ('__radd__', '__add__'), ('__rand__', '__and__'),
            ('__rlshift__', '__lshift__'), ('__rmod__', '__mod__'),
            ('__rmul__', '__mul__'), ('__rpow__', '__pow__'),
            ('__rrshift__', '__rshift__'), ('__rsub__', '__sub__'),
            ('__rxor__', '__xor__'), ('__rfloordiv__', '__floordiv__'),
            ('__rtruediv__', '__truediv__')):
        def _op(operand_left, operand_right, operation=_method):
            return _MapConstantReverse(operand_left, operand_right,
                                       getattr(operator, operation))

        setattr(Publisher, method, _op)

    for method, _method in (
            ('__neg__', operator.neg), ('__pos__', operator.pos),
            ('__abs__', operator.abs), ('__invert__', operator.invert),
            ('__round__', round), ('__trunc__', math.trunc),
            ('__floor__', math.floor), ('__ceil__', math.ceil)):
        def _op_unary(operand, operation=_method):
            return _MapUnary(operand, operation)

        setattr(Publisher, method, _op_unary)


class Str(_MapUnary):
    def __init__(self, publisher: Publisher):
        _MapUnary.__init__(self, publisher, str)


class Bool(_MapUnary):
    def __init__(self, publisher: Publisher):
        _MapUnary.__init__(self, publisher, bool)


class Int(_MapUnary):
    def __init__(self, publisher: Publisher):
        _MapUnary.__init__(self, publisher, int)


class Float(_MapUnary):
    def __init__(self, publisher: Publisher):
        _MapUnary.__init__(self, publisher, float)


class Repr(_MapUnary):
    def __init__(self, publisher: Publisher):
        _MapUnary.__init__(self, publisher, repr)


class Len(_MapUnary):
    def __init__(self, publisher: Publisher):
        _MapUnary.__init__(self, publisher, len)
