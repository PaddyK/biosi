""" Module contains publisher classes for different data sources
"""
import online
import sources
from threading import Thread
from nanomsg import PUB
from nanomsg import Socket
from Queue import Queue


class AbstractPublisher(Thread):
    """ Abstract base class for concrete publisher classes
    """

    def __init__(self, source, url):
        """ Initializes object
        """
        self._factory = sources.SourceFactory()
        self._source = self._factory.produce(source)
        self._url = url

    @property
    def url(self):
        """ Returns url of local endpoint of publisher.

            Publisher always bind/connect to local endpoint

            Returns:
                String
        """
        return self._url

    @property
    def source(self):
        """ Returns data source of publisher

            Returns:
                online.sources.AbstractSource
        """
        return self._source

    def run(self):
        """ Starts Thread

            Runs as long as new data is available. If no new data for 5 Seconds
            received socket will be shut down
        """
        with Socket(PUB) as pub_socket:
            pub_socket.bind(self.url)

            while True:
                try:
                    sample = self.source.queue.get(timeout=1)
                    message = '{:s}|{:s}'.format(source, sample)
                    pub_socket.send(message)
                except Empty as e:
                    print 'No new data available - terminating publisher'
                    break


class EmgPublisher(AbstractPublisher):
    """ Publisher for EMG data
    """

    def __init__(self, url):
        """ Initializes Object

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
        super(EmgPublisher, self).__init__('emg', url)
