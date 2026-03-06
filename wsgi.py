"""
The Oracle 2026 - WSGI Configuration
For PythonAnywhere Deployment
"""

import os
import sys

# Add project directory to path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.insert(0, path)

# Set timezone to WITA
os.environ['TZ'] = 'Asia/Makassar'

def application(environ, start_response):
    """WSGI application for PythonAnywhere"""
    from telegram_notifier import send_next_day_report
    
    # Run the telegram notifier
    try:
        send_next_day_report()
        status = '200 OK'
        body = 'Telegram notification sent successfully'
    except Exception as e:
        status = '500 Internal Server Error'
        body = f'Error: {str(e)}'
    
    response_headers = [
        ('Content-Type', 'text/plain'),
        ('Content-Length', str(len(body)))
    ]
    start_response(status, response_headers)
    return [body.encode('utf-8')]
