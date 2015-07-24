""" Module containing subscriber classes for different data sources
"""
import online
from threading import Thread
from nanomsg import SUB
from nanomsg import SUB_SUBSCRIBE
from nanomsg import Socket
from nanomsg import NanoMsgAPIError
#from nanomsg import EBADF, ENOTSUP, EFSM, EAGAIN, EINTER, ETIMEDOUT, ETERM
from Queue import Queue
import json
import matplotlib.pyplot as plt

#error_codes = {
#        EBADF: 'The provided socket is invalid.',
#        ENOTSUP: 'The operation is not supported by this socket type.',
#        EFSM: 'The operation cannot be performed on this socket at the ' + \
#                'moment because socket is not in the appropriate state. ' + \
#                'This error may occur with socket types that switch ' + \
#                'between several states.',
#        EAGAIN: 'Non-blocking mode was requested and there is no message ' + \
#                'to receive at the moment.',
#        EINTER: 'The operation was interrupted by delivery of a signal ' + \
#                'before the message was received.',
#        ETIMEDOUT: 'Individual socket types may define their own specific ' + \
#                'timeouts. If such timeout is hit this error will be returned.',
#        ETERM: 'The library is terminating.'
#        }

class AbstractSubscriber(Thread):
    """ Abstract base class for concrete subscribers
    """

    def __init__(self, url, topic):
        """ Initiates object

            Args:
                url (String): URL to publisher socket
                topic (String): Topic to subscribe to
        """
        super(AbstractSubscriber, self).__init__()
        self._url = url
        self._topic = topic + '|' # Momentarily used as separator <topic>|<body>

    @property
    def url(self):
        """ Getter for attribute `url`

            Returns:
                String
        """
        return self._url

    @property
    def topic(self):
        """ Returns topic subscriber is listening to

            Returns:
                String
        """
        return self._topic

    def run(self):
        """ Starts Thread
        """
        set = []
        start = 0

        with Socket(SUB) as sub_socket:
            sub_socket.connect(self.url)
            sub_socket.set_string_option(SUB, SUB_SUBSCRIBE, self.topic)
            plt.ion()
            plt.show()
            while True:
                try:
                    message = sub_socket.recv()
                    msg = message.split('|')
                    data = json.loads(msg[1])

                    if len(set) > 8000:
                        set.pop()
                        start += 1
                    set.append(data)
                    x = range(start, start + len(set))

                    plt.clf()
                    plt.plot(x, set)
                    plt.draw()

                    print 'SUBSCRIBER: {}'.format(message)
                except NanoMsgAPIError as e:
                    print 'Error during receiving of data in AbstractSubscriber ' + \
                            'Error was : {}'.format(e.message)
                    break

class EmgSubscriber(AbstractSubscriber):
    """ Subscriber for EMG data
    """

    def __init__(self, url):
        """ Initiates object

            Args:
                url (String): Url of local ressource to bind to.

            Examples:
                >>> url = 'inproc://<identifier>'
                Used for within procss communication (within a single process).
                `<identifier>` may be an arbitrary sequence of characters

                >>> url = 'ipc://<rel-path>     # relative path POSIX
                >>> url = 'ipc:///<abs-path>    # absolute path POSIX
                >>> url = 'ipc://<identifier>  # Windows format
                Used for interprocess communication. On POSIX-compliant systems
                `<path>` is a relative (indicated by two preceeding slashes) or
                absolute (three preceeding slashes) path to a file.
                On windows named pipes are used. Here `<identifier>` can be any
                sequence of characters.
                Adress `ipc://test` would refer to pipe `\\.\pipe\test`

                >>> url = 'tcp://<interface>;<address>:<port>'
                When using `bind`, `<interface> **must** be ommitted. When
                using `connect`, `<interface>` **can** be specified (depending
                on OS, for UNIX e.g. `eth0`). If not specified OS will select
                it itself.
                `<address>` can be an IPv4, IPv6 address or DNS name, `<port>`
                is the numeric port.
        """
        super(EmgSubscriber, self).__init__(url, 'emg' )
