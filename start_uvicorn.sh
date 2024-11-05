#!/bin/bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# run:  pm2 start start_uvicorn.sh --name my-uvicorn-app
