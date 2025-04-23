#!/usr/bin/env bash
gcloud run deploy sheet-search-api \
  --source=./cloud-run-api \
  --region=us-central1 \
  --set-secrets=OPENAI_API_KEY=openai-key:latest$( [[ -z "$SERPAPI_KEY" ]] || echo ,SERPAPI_KEY=serpapi-key:latest ) \
  --allow-unauthenticated
