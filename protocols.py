import asyncio
from constants import *
import hashlib
from utils import *
import os


class ServerProtocol(asyncio.Protocol):
    def __init__(self, file_path, *args, **kwargs):
        super(ServerProtocol, self).__init__(*args, **kwargs)
        self.file = open(file_path, 'rb')
        self.file_name = os.path.split(file_path)[1]

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        return self.dispatch(data)

    def dispatch(self, data):
        if strip_binary(data) == HASH_QUERY:
            self.transport.write(self.sha1().encode('ascii'))
        if strip_binary(data) == DATA_QUERY:
            for chunk in self.file_iterator():
                self.transport.write(chunk)
        if strip_binary(data) == SIZE_QUERY:
            self.transport.write(self.size())
        if strip_binary(data) == NAME_QUERY:
            self.transport.write(self.file_name.encode('ascii'))

    def sha1(self):
        s = hashlib.sha1()
        for chunk in self.file_iterator():
            s.update(chunk)
        self.file.seek(0)
        return s.hexdigest()

    def size(self):
        s = 0
        for chunk in self.file_iterator():
            s += len(chunk)
        return str(s).encode('ascii')

    def file_iterator(self):
        chunk = self.file.read(CHUNK_SIZE)
        while chunk:
            yield chunk
            chunk = self.file.read(CHUNK_SIZE)
        self.file.seek(0)

    def connection_lost(self, exc):
        print('I ni ma go')


class ClientProtocol(asyncio.Protocol):
    state = 'created'

    def __init__(self, parsed):
        print('asdf')
        self.loop = asyncio.get_event_loop()
        self.parsed = parsed
        self.hash = None
        self.size = None
        self.name = None
        self.file = None
        self.transferred = 0

    def connection_made(self, transport):
        self.transport = transport
        self.transport.write(HASH_QUERY)
        self.state = 'hash'

    def data_received(self, data):
        if self.state == 'hash':
            self.hash = data.decode('ascii')
            self.state = 'name'
            self.transport.write(NAME_QUERY)
        elif self.state == 'name':
            self.name = data.decode('ascii')
            self.state = 'size'
            self.file = self.give_me_file()
            self.transport.write(SIZE_QUERY)
        elif self.state == 'size':
            self.size = int(data)
            self.state = 'data'
            self.transport.write(DATA_QUERY)
        elif self.state == 'data':
            if self.transferred < self.size:
                print('len - {}'.format(len(data)))
                self.file.write(data)
                self.transferred += len(data)
                if self.transferred == self.size:
                    print('Done!')
                    self.file.flush()
                    self.state = 'done'
                    self.loop.stop()
            self.file.flush()

    def give_me_file(self):
        if self.parsed.download_to:
            if not os.path.exists(self.parsed.download_to):
                try:
                    os.makedirs(self.parsed.download_to)
                except FileExistsError:
                    pass
                except Exception:
                    print('Could not make directory {}'.format(self.parsed.download_to))
                    self.loop.stop()
            return open(os.path.join(self.parsed.download_to, self.name), 'wb')
        elif self.parsed.download_as:
            if not os.path.exists(os.path.split(self.parsed.download_as)):
                try:
                    os.makedirs(os.path.split(self.parsed.download_as)[0])
                except FileExistsError:
                    pass
                except Exception:
                    print('Could not make directory for file {}'.format(self.parsed.download_as))
            return open(self.parsed.download_as, 'wb')

