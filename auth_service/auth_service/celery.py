# Ensures compatibility with older Python/Celery import behaviors
# Makes sure Celery understands absolute imports inside Django's folder structure.
from __future__ import absolute_import, unicode_literals

# Standard library import for environment variables
import os

# Celery main class — the core of the task queue system.
from celery import Celery


# -----------------------------------------------
# 1. SET DEFAULT DJANGO SETTINGS FOR CELERY
# -----------------------------------------------

# Celery runs OUTSIDE the main Django process.
# It is a separate worker process.
# Because of this, Celery must explicitly be told:
# “Use Django settings from auth_service.settings”
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auth_service.settings")


# -----------------------------------------------
# 2. CREATE CELERY APPLICATION INSTANCE
# -----------------------------------------------

# This initializes the Celery app for the whole project.
# "auth_service" is the name of your microservice/project.
# This name shows up in logs, monitoring tools, and workers.
app = Celery("auth_service")


# -----------------------------------------------
# 3. CELERY BROKER + RESULT BACKEND CONFIG
# -----------------------------------------------

# Celery needs 2 things:
#  - BROKER (queue system where tasks are sent)
#  - BACKEND (where task results/status are stored)

# Using Redis is the production standard:
#   Redis is extremely fast
#   Supports pub/sub
#   Supports TTL for expiring results
#   Works well inside microservice ecosystems
#
# broker_url = where Celery RECEIVES tasks (queue)
# result_backend = optional (where results are stored)
#
# os.getenv allows overriding via environment variables in production,
# otherwise defaults to Redis running locally.
app.conf.broker_url = os.getenv("CELERY_BROKER", "redis://localhost:6379/1")
app.conf.result_backend = os.getenv("CELERY_BACKEND", "redis://localhost:6379/2")


# -----------------------------------------------
# 4. AUTO-DISCOVER TASKS INSIDE EACH APP
# -----------------------------------------------

# Celery will scan every installed Django app.
# If it finds a `tasks.py` file inside an app (like accounts/tasks.py),
# it automatically loads the task definitions.
#
# This removes the need to manually import task modules.
app.autodiscover_tasks()


# -----------------------------------------------
# 5. CELERY CONFIGURATION SETTINGS
# -----------------------------------------------

# These settings control how Celery serializes data,
# handles timezone, and what formats it accepts.
app.conf.update(

    # Celery sends tasks as serialized JSON (recommended).
    # Safer and more compatible than pickle.
    task_serializer="json",

    # Task results (if stored) also serialized as JSON.
    result_serializer="json",

    # Accept only JSON into Celery (security: avoids pickle attacks).
    accept_content=["json"],

    # Use UTC across your microservice.
    # Essential for distributed systems, consistency, and auditing.
    timezone="UTC",
    enable_utc=True,
)
