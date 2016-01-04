def strip_binary(binary):
    return binary.decode('ascii').strip().encode('ascii')


def cli_valid(parsed, parser):
    if parsed.serve and (parsed.download_to or parsed.download_as):
        parser.error("You cannot specify file to serve, and in the same time directory to download")
    elif parsed.download_to and parsed.download_as:
        parser.error("You cannot specify --download-as and download-to in the same time")
