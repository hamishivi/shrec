#!/usr/bin/env python
from argparse import ArgumentParser
from app import app
import cProfile

parser = ArgumentParser()
parser.add_argument("-p", "--profiling", action="store_true",
                    help="Enable cProfile. Disables debug reloader.")
parser.add_argument("--port", default=5000,
                    help="Port to start server on")
parser.add_argument("--host", default="127.0.0.1",
                    help="Port to start server on")
parser.add_argument("-d", "--debug", action="store_true",
                    help="Enable debug mode")
args = parser.parse_args()

if __name__ == "__main__":
   appargs = {"port": args.port, "host": args.host, "debug": args.debug}
   if args.profiling:
      appargs["use_reloader"] = False
      cProfile.run(f'app.run(**{appargs})')
   else:
      app.run(**appargs)
