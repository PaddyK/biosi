""" This module contains publisher/subscriber components based on NanoMSG.
"""
from nanomsg import PUB
from nanomsg import Socket
from nanomsg import SUB
from nanomsg import SUB_SUBSCRIBE
from nanomsg import Socket
from nanomsg import NanoMsgAPIError
from messaging import HiddenComponent
from messaging import HiddenPublisher
from messaging import HiddenSubscriber


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
        self._socket.bind(url)

    def publish(self, message):
        """ Publishes message

            Args:
                message (String): Message to publish
        """
        self._socket.send('{}|{}').format(self._topic, message)


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
        self._socket.connect(url)
        self._socket.set_string_option(SUB, SUB_SUBSCRIBE, topic)

    def receive(self):
        """ Receives a message

            Returns:
                String
        """
        message = self._socket.recv()
        return message
