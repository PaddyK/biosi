""" This module contains publisher/subscriber components based on NanoMSG.
"""
from nanomsg import PUB
from nanomsg import Socket
from nanomsg import SUB
from nanomsg import SUB_SUBSCRIBE
from nanomsg import Socket
from nanomsg import NanoMsgAPIError
from . import HiddenComponent
from . import HiddenPublisher
from . import HiddenSubscriber
import logging
logging.basicConfig(level=logging.DEBUG)


class NanomsgPublisher(HiddenPublisher):
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
        super(NanomsgPublisher, self).__init__(topic)
        self._socket = Socket(PUB)
        self._socket.send_timeout = 1 # Wait 1ms for sending
        self._socket.bind(url)
        self._logger = logging.getLogger('NanomsgPublisher')

    def publish(self, message):
        """ Publishes message

            Args:
                message (String): Message to publish
        """
        self._socket.send('{}|{}'.format(self._topic, message))

    def __enter__(self):
        """ Statement used for the `` with ... as ...:`` returns
            the object to use in the ``with`` block

            Returns:
                NanomsgPublisher
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ Executed when leaving ``with`` block, regardless whether
            because of an exception or normal program flow
        """
        self._socket.close()


class NanomsgSubscriber(HiddenSubscriber):
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
        super(NanomsgSubscriber, self).__init__(topic)
        self._socket = Socket(SUB)
        self._socket.recv_timeout = 500 # Wait 500ms for receiving msgs
        self._socket.connect(url)
        self._socket.set_string_option(SUB, SUB_SUBSCRIBE, topic + '|')
        self._logger = logging.getLogger('NanomsgSubscriber')

    def receive(self):
        """ Receives a message

            Returns:
                String
        """
        message = self._socket.recv()
        return message[len(self.topic) + 1:]

    def __enter__(self):
        """ Statement used for the `` with ... as ...:`` returns
            the object to use in the ``with`` block

            Returns:
                NanomsgSubscriber
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ Executed when leaving ``with`` block, regardless whether
            because of an exception or normal program flow
        """
        self._socket.close()

