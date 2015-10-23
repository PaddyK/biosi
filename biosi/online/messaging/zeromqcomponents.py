""" This module contains publisher/subscriber components based on the
    ZeroMQ.
"""
from zmq import Context
from zmq import PUB
from zmq import SUB
from zmq import SUBSCRIBE
from zmq import RCVTIMEO
from zmq import SNDTIMEO
from . import HiddenComponent
from . import HiddenPublisher
from . import HiddenSubscriber
import logging
logging.basicConfig(level=logging.DEBUG)


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
        self._logger = logging.getLogger('ZeromqPublisher')

    def publish(self, message):
        """ Publishes message

            Args:
                message (String): Message to publish
        """
        self._socket.send_multipart([self.topic, message])

    def __enter__(self):
        """ Statement used for the `` with ... as ...:`` returns
            the object to use in the ``with`` block

            Returns:
                ZmqPublisher
        """
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        """ Executed when leaving ``with`` block, regardless whether
            because of an exception or normal program flow
        """
        self._socket.close()
        self._context.term()


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
        self._socket.setsockopt(SUBSCRIBE, topic)
        self._socket.setsockopt(RCVTIMEO, 500) # Wait 500ms for message to arrive
        self._socket.connect(url)
        self._logger = logging.getLogger('ZeromqSubscriber')

    def receive(self):
        """ Receives a message

            Returns:
                String
        """
        topic, message = self._socket.recv_multipart()
        return message

    def __enter__(self):
        """ Statement used for the `` with ... as ...:`` returns
            the object to use in the ``with`` block

            Returns:
                ZmqSubscriber
        """
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        """ Executed when leaving ``with`` block, regardless whether
            because of an exception or normal program flow
        """
        self._socket.close()
        self._context.term()

