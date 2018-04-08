import pytest
from broqer import Publisher
from broqer.subject import Subject

@pytest.mark.parametrize('cls', [Publisher])
def test_meta(cls):
  d={'a':1}

  # init without .meta dict
  publisher=cls()
  assert publisher.meta is None

  # .meta should not be able to set
  with pytest.raises(AttributeError):
    publisher.meta={'a':1}

  # init with .meta dict
  publisher=cls(meta=d)
  assert publisher.meta==d

  # .meta should not be able to set
  with pytest.raises(AttributeError):
    publisher.meta={'a':1}
  
  # .meta dict should be immutable
  with pytest.raises(TypeError):
    publisher.meta['a']=2
  
  with pytest.raises(TypeError):
    publisher.meta['b']=2

@pytest.mark.parametrize('cls', [Publisher])
def test_subscribe(cls):
  s1=Subject()
  s2=Subject()

  publisher=cls()
  assert len(publisher)==0

  # subscribe first subscriber
  d1=publisher.subscribe(s1)
  assert len(publisher)==1

  # re-subscribe should fail
  with pytest.raises(ValueError):
    publisher.subscribe(s1)
  
  # subscribe second subscriber
  d2=publisher.subscribe(s2)
  assert len(publisher)==2

  # unsubscribe both subscribers
  d1.dispose()
  assert len(publisher)==1
  publisher.unsubscribe(s2)
  assert len(publisher)==0

  # re-unsubscribing should fail
  with pytest.raises(ValueError):
    d1.dispose()
  
  with pytest.raises(ValueError):
    publisher.unsubscribe(s1)
  
  with pytest.raises(ValueError):
    d2.dispose()


  