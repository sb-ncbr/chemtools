#!/usr/bin/env bash

celery -A worker worker --loglevel=info --concurrency=8

