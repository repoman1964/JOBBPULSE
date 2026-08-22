#!/bin/sh
set -eu
exec celery -A app.tasks.celery_app.celery_app worker -l info
