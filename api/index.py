"""Vercel entry point.

Vercel's Python runtime looks for a WSGI callable named `app` in this file.
All requests are routed here by vercel.json.
"""

from config.wsgi import application as app  # noqa: F401
