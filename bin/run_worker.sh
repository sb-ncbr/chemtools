#!/usr/bin/env bash

celery -A worker worker --loglevel=debug --concurrency=8

