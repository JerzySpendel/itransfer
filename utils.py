def strip_binary(binary):
    return binary.decode('ascii').strip().encode('ascii')


def cli_valid(parsed, parser):
    if parsed.serve and (parsed.download_to or parsed.download_as):
        parser.error("You cannot specify file to serve, and in the same time directory to download")
    elif parsed.download_to and parsed.download_as:
        parser.error("You cannot specify --download-as and download-to in the same time")
    elif (parsed.download_to or parsed.download_as) and not parsed.ip:
        parser.error("Well, I would like to download that file for you but where should I search for it? Specify --ip")
