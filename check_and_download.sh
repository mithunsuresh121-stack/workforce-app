#!/bin/bash

while true; do
  RUN_INFO=$(gh run list --workflow=build-apk.yml --limit 1 --json databaseId,status,conclusion)
  ID=$(echo $RUN_INFO | jq -r '.[0].databaseId')
  STATUS=$(echo $RUN_INFO | jq -r '.[0].status')
  CONCLUSION=$(echo $RUN_INFO | jq -r '.[0].conclusion')
  if [ "$STATUS" == "completed" ]; then
    if [ "$CONCLUSION" == "success" ]; then
      # Download artifact
      gh run download $ID --name Workforce-Debug-APK
      # Move to Desktop
      mv Workforce-Debug-APK/app-debug.apk /Users/mithunsuresh/Desktop/Workforce-App-Debug.apk
      echo "APK downloaded successfully."
      break
    else
      echo "Run failed. Conclusion: $CONCLUSION"
      break
    fi
  fi
  echo "Waiting for run to complete..."
  sleep 30
done
