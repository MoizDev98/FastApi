import argparse

def create_parser():
    parser = argparse.ArgumentParser(description="Markdown Server command line options")
    parser.add_argument("notepath", nargs="?", default="./", help="Path to notes. Default is relative path of './'")
    parser.add_argument("--host", default='localhost', help="Host you would like to run on. Default is 'localhost'")
    parser.add_argument("--port", default=3000, help="Port to run application on. Default port is '3000'")
    parser.add_argument("--daemonize", default=False, action="store_true", help="Run server as background process")
    parser.add_argument("-d", "--debug", default=False, action="store_true", help="Enabled Debug Mode")
    return parser

parser = create_parser()
args = parser.parse_args()
