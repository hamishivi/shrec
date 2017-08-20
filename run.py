#!/usr/bin/env python
from argparse import ArgumentParser
from app import app
import cProfile

parser = ArgumentParser()
parser.add_argument("-p", "--profiling", action="store_true",
                    help="Enable cProfile")
parser.add_argument("-d", "--debug", action="store_true",
                    help="Enable debug mode")
args = parser.parse_args()

if __name__ == "__main__":
   if args.profiling:
      params = "debug=True, use_reloader=False" if args.debug else ''
      cProfile.run(f'app.run({params})')
   else:
      app.run()
