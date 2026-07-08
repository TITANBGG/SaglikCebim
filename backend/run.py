#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Start uvicorn
import uvicorn
uvicorn.run("app.main:app", host="127.0.0.1", port=8001, reload=False)
