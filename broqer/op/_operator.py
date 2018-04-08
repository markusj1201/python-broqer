import asyncio
from typing import Any, List

from broqer import Publisher, Subscriber, SubscriptionDisposable


class Operator(Publisher, Subscriber):
  def __init__(self, *publishers:List[Publisher]):
    super().__init__()
    self._publishers=publishers

  def subscribe(self, subscriber:'Subscriber') -> SubscriptionDisposable:
    disposable=Publisher.subscribe(self, subscriber)
    if not self._subscriptions:
      for _publisher in self._publishers:
        _publisher.subscribe(self)
    return disposable
  
  def unsubscribe(self, subscriber:'Subscriber') -> None:
    Publisher.unsubscribe(self, subscriber)
    if not self._subscriptions:
      for _publisher in self._publishers:
        _publisher.unsubscribe(self)
  
  def _emit(self, *args:Any) -> None:
    for subscriber in tuple(self._subscriptions):
      # TODO: critical place to think about handling exceptions
      subscriber.emit(*args, who=self)