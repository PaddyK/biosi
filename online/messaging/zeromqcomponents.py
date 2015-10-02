""" This module contains publisher/subscriber components based on the
    ZeroMQ.
"""
from zmq import Context
from zmq import PUB
from zmq import SUB
from zmq import SUBSCRIBE
from messaging import HiddenComponent
from messaging import HiddenPublisher
from messaging import HiddenSubscriber

class ZmqPublisher(HiddenPublisher):
    """ Publisher class publishing messages to a certain topic to an url

        Attributes:
            context (zmq.Context):
            socket (Socket): Socket object of ZMQ context
            topic (String): Topic publisher publishs to
    """
    def __init__(self, url, topic):
        """ Initializes object

            Args:
                url (String): url to publish messages to
                topic (String): Topic to publish messages under
        """
        super(ZmqPublisher, self).__init__(topic)
        self._context = Context()
        self._socket = self._context.socket(PUB)
        self._socket.bind(url)

    def publish(self, message):
        """ Publishes message

            Args:
                message (String): Message to publish
        """
        self._socket.send_multipart([self.topic, message])


class ZmqSubscriber(HiddenSubscriber):
    """ Subscriber class subscribing to a certain topic

        Attributes:
           context (zmq.Context):
           socket (Socket): Socket object of ZMQ context
           topic (String): Topic subscriber subscribes to
    """
    def __init__(self, url, topic):
        """ Initializes object

            Args:
                url (String): url to publish messages to
                topic (String): Topic to publish messages under
        """
        super(ZmqSubscriber, self).__init__(url)
        self._context = Context()
        self._socket = self._context.socket(SUB)
        self._socket.connect(url)
        self._socket.setsockopt(SUBSCRIBE, self._topic)

    def receive(self):
        """ Receives a message

            Returns:
                String
        """
        topic, message = self._socket.recv_multipart()
        return message

