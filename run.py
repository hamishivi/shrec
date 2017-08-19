#!/usr/bin/env python
from app import app
import cProfile

if __name__ == "__main__":
   cProfile.run('app.run(debug=True)')
