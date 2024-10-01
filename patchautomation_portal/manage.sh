#!/bin/sh
/usr/bin/python3.11 -m uvicorn --host=0.0.0.0 --port=61007 patchautomation_portal.asgi:application
