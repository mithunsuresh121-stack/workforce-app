#!/bin/bash

# Delete unused workflow files
rm .github/workflows/backend-tests.yml
rm .github/workflows/frontend-tests.yml
rm .github/workflows/mobile-tests.yml

# Commit and push changes
git add -A
git commit -m "Remove unused workflow files"
git push

# Delete all runs for removed workflows
for workflow in backend-tests frontend-tests mobile-tests; do
  run_ids=$(gh run list --workflow "$workflow" --json id | jq -r '.[] .id')
  for id in $run_ids; do
    gh run delete "$id"
  done
done

# For build-apk.yml, delete failed/cancelled/skipped runs
for status in failure cancelled skipped; do
  run_ids=$(gh run list --workflow build-apk.yml --status "$status" --json id | jq -r '.[] .id')
  for id in $run_ids; do
    gh run delete "$id"
  done
done

# Keep only the last 3 successful runs for build-apk.yml
successful_runs=$(gh run list --workflow build-apk.yml --status success --json id,createdAt | jq -r 'sort_by(.createdAt) | reverse | .[3:] | .[] .id')
for id in $successful_runs; do
  gh run delete "$id"
done

# Trigger a final clean run
gh workflow run build-apk.yml
