#!/bin/bash

RUN_INFO=$(gh run list --workflow=build-apk.yml --limit 1 --json databaseId,status,conclusion)
ID=$(echo $RUN_INFO | jq -r '.[0].databaseId')
STATUS=$(echo $RUN_INFO | jq -r '.[0].status')
CONCLUSION=$(echo $RUN_INFO | jq -r '.[0].conclusion')

if [ "$STATUS" == "completed" ] && [ "$CONCLUSION" == "success" ]; then
  gh run download $ID --name Workforce-Debug-APK
  mv Workforce-Debug-APK/app-debug.apk /Users/mithunsuresh/Desktop/Workforce-App-Debug.apk
  echo "APK downloaded successfully."
else
  echo "Run not completed or failed. Status: $STATUS, Conclusion: $CONCLUSION"
fi
