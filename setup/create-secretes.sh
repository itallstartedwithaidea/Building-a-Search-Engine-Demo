#!/usr/bin/env bash
# one-time secret creation (OpenAI key mandatory, SerpAPI optional)

OPENAI="sk-..."
SERP="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"   # leave blank if none

echo -n "$OPENAI" | gcloud secrets create openai-key --data-file=- 2>/dev/null \
      || gcloud secrets versions add openai-key --data-file=-

if [[ -n "$SERP" ]]; then
  echo -n "$SERP"  | gcloud secrets create serpapi-key --data-file=- 2>/dev/null \
        || gcloud secrets versions add serpapi-key --data-file=-
fi

PROJECT_NUM=$(gcloud projects describe $(gcloud config get-value project) \
               --format='value(projectNumber)')
for secret in openai-key serpapi-key; do
  gcloud secrets add-iam-policy-binding "$secret" \
    --member="serviceAccount:${PROJECT_NUM}-compute@developer.gserviceaccount.com" \
    --role='roles/secretmanager.secretAccessor' 2>/dev/null || true
done
