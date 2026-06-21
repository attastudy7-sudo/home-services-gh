#!/bin/bash
flask db upgrade
exec gunicorn 'app:create_app()'
