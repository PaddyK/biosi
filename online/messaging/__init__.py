""" Makes Publisher/Subscriber components available and defines abstract
    parent classes.
"""

TECHNOLOGY = 'nanomsg'
#TECHNOLOGY = 'zmq'
""" Defines whether to use NanoMSG or ZMQ for publisher/subsciber functionality.
    Set ``TECHNOLOGY`` to:
        - nanomsg
        - zmq
    to get respective implementations
"""
class HiddenComponent(object):
    """ Abstract base class for ZMQ/Nanomsg implementations"""
    def __init__(self, topic):
        self._topic = topic

    @property
    def topic(self):
        return self._topic


class HiddenPublisher(HiddenComponent):
    """ Abstract base class for ZMQ/Nanomsg implementations of Publisher"""
    def publish(self, message):
        pass


class HiddenSubscriber(HiddenComponent):
    """ Abstract base class for ZMQ/Nanomsg implementations of Subscriber"""
    def receive(self):
        pass

if TECHNOLOGY == 'nanomsg':
    from nanomsgcomponents import NanomsgPublisher as Publisher
    from nanomsgcomponents import NanomsgSubscriber as Subscriber
elif TECHNOLOGY == 'zmq':
    from zeromqcomponents import ZmqPublisher as Publisher
    from zeromqcomponents import ZmqSubscriber as Subscriber
else:
    raise NotImplementedError('Technology {} not implemented'.format(TECHNOLOGY))

