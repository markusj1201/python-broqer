"""
>>> from broqer import Subject, op
>>> s = Subject()

>>> def moving_average(state, value):
...     state=state[1:]+[value]
...     return state, sum(state)/len(state)

>>> lowpass = s | op.accumulate(moving_average, init=[0]*3)
>>> lowpass | op.sink(print)
<...>
>>> s.emit(3)
1.0
>>> s.emit(3)
2.0
>>> s.emit(3)
3.0
>>> s.emit(3)
3.0

Resetting (or just setting) the state is also possible:

>>> lowpass.reset([1, 1, 1])
>>> s.emit(4)
2.0

"""
from typing import Any, Callable, Tuple

from broqer import Publisher

from ._operator import Operator, build_operator


class Accumulate(Operator):
    """ On each emit of source publisher a function gets called with state and
    received value as arguments and is returning new state and value to emit.

    :param publisher: source publisher
    :param func:
        Function taking two arguments: current state and new value. The return
        value is a tuple with (new state, result) where new state will be used
        for the next call and result will be emitted to subscribers.
    :param init: initialization for state
    """
    def __init__(self, publisher: Publisher,
                 func: Callable[[Any, Any], Tuple[Any, Any]], init) -> None:
        Operator.__init__(self, publisher)
        self._acc_func = func
        self._state = init

    def reset(self, state:Any) -> None:
        """ Reseting (or setting) the internal state.

        :param state: new state to be set
        """
        self._state = state

    def emit(self, *args: Any, who: Publisher) -> None:
        assert len(args) == 1, \
            'accumulate is only possible for emits with single argument'
        assert who == self._publisher, 'emit from non assigned publisher'
        self._state, result = self._acc_func(self._state, args[0])
        self.notify(result)


accumulate = build_operator(Accumulate)
