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
        """ Initializes object

            Args:
                topic (String): Topic of component
        """
        self._topic = topic

    @property
    def topic(self):
        """ Returns topic component publishes/subscribes to

            Returns:
                String
        """
        return self._topic


class HiddenPublisher(HiddenComponent):
    """ Abstract base class for ZMQ/Nanomsg implementations of Publisher"""
    def publish(self, message):
        """ Publishes message
            
            Args:
                message (String): Message to publish
        """
        pass


class HiddenSubscriber(HiddenComponent):
    """ Abstract base class for ZMQ/Nanomsg implementations of Subscriber"""
    def receive(self):
        """ Receives a message
        """
        pass

if TECHNOLOGY == 'nanomsg':
    from nanomsgcomponents import NanomsgPublisher as Publisher
    from nanomsgcomponents import NanomsgSubscriber as Subscriber
elif TECHNOLOGY == 'zmq':
    from zeromqcomponents import ZmqPublisher as Publisher
    from zeromqcomponents import ZmqSubscriber as Subscriber
else:
    raise NotImplementedError('Technology {} not implemented'.format(TECHNOLOGY))

