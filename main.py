import asyncio
from protocols import ServerProtocol, ClientProtocol
from utils import cli_valid
import argparse

parser = argparse.ArgumentParser(description='Simple file transferring')
parser.add_argument('--serve-file', dest='serve', help='path to file to serve')
parser.add_argument('--download-to', dest='download_to', help='directory where file will be downloaded')
parser.add_argument('--download-as', dest='download_as', help='Specify path file should be saved as')
parser.add_argument('--ip', dest='ip', help='IP address to download from')
parser.add_argument('--port', dest='port', help='Port to connect to or serve from, default 8888')
args = parser.parse_args()
cli_valid(args, parser)


loop = asyncio.get_event_loop()
port = 8888 if not args.port else args.port
if args.serve:
    print('ok, tu')
    path = args.serve
    coro = loop.create_server(lambda *args, **kwargs: ServerProtocol(path, *args, **kwargs), '0.0.0.0', port)
    server = loop.run_until_complete(coro)
    try:
        loop.run_forever()
    except Exception:
        print('Eksepszyn')
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
elif args.download_to or args.download_as:
    print('Downloading...')
    loop = asyncio.get_event_loop()
    coro = loop.create_connection(lambda: ClientProtocol(args), args.ip, port)
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()
