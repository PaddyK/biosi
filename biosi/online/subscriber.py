""" Module containing subscriber classes for different data sources
"""
import online
from threading import currentThread
from threading import Thread
from messaging import Subscriber
#from nanomsg import EBADF, ENOTSUP, EFSM, EAGAIN, EINTER, ETIMEDOUT, ETERM
from Queue import Queue
import json
import matplotlib.pyplot as plt
import logging
logging.basicConfig(level=logging.DEBUG)

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

def array_iterator(msgclass, subscriber):
    while True:
        message = subscriber.queue.get()
        parsed = msgclass.deserialize(message)
        subscriber.queue.task_done()
        yield parsed


class AbstractSubscriber(Thread):
    """ Abstract base class for concrete subscribers
    """

    def __init__(self, url, topic, name, abort=None):
        """ Initiates object

            Args:
                url (String): URL to publisher socket
                topic (String): Topic to subscribe to
                name (String): Name of Thread
                abort (threading.Event): Inidcates if Thread should abort
        """
        super(AbstractSubscriber, self).__init__(name=name)
        self._url = url
        self._topic = topic
        self._qeueu = Queue()
        self._abort = abort

    @property
    def url(self):
        """ Getter for attribute `url`

            Returns:
                String
        """
        return self._url

    @property
    def queue(self):
        """ Returns objects *queue* attribute.

            queue contains messages as they are received by subscriber.
            Messages are not preprocessed or deserialized.

            Return Queue.Queue
        """
        return self._qeueu

    @property
    def topic(self):
        """ Returns topic subscriber is listening to

            Returns:
                String
        """
        return self._topic

    def _cleanup(self):
        """ Cleans when Thread exits
        """
        pass

    def run(self):
        """ Starts Thread
        """
        with Subscriber(self._url, self._topic) as subscriber:
            while True:
                try:
                    message = subscriber.receive()
                    self.queue.put(message[len(self.topic):])
                except Exception as e:
                    logging.info('Error during receiving of data in ' + \
                            'AbstractSubscriber Error was : {}'.format(e.message))
                    self._cleanup()
                    if self._abort is not None:
                        self._abort.set()
                    break

                if self._abort is not None:
                    if self._abort.is_set():
                        logging.info('{} - Abort event is set. Exit...'.format(
                                currentThread().getName()
                                ))
                        self._cleanup()
                        break


class EmgSubscriber(AbstractSubscriber):
    """ Subscriber for EMG data
    """

    def __init__(self, url, name='EmgSubscriber', abort=None):
        """ Initiates object

            Args:
                url (String): Url of local ressource to bind to.
                name (String): Name of thread
                abort (threading.Event): Signals Thread to stop exection

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
        super(EmgSubscriber, self).__init__(url, 'emg', name, abort=abort)


class KinSubscriber(AbstractSubscriber):
    """ Subscriber for Kinematic data
    """

    def __init__(self, url, name='KinSubscriber', abort=None):
        """ Initiates object

            Args:
                url (String): Url of local ressource to bind to.
                name (String): Name of thread
                abort (threading.Event): Signals Thread to stop exection

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
        super(KinSubscriber, self).__init__(url, 'kin', name, abort=abort)
