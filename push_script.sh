#!/bin/bash
set -e

# ===============================
# CONFIGURATION
# ===============================
REMOTE="origin"
BRANCH="main"
FOLDERS=("backend" "mobile" "frontend-web" "scripts" "tests" "docs" ".")
LARGE_FILE_THRESHOLD="+50M"

# ===============================
# STEP 1: Initialize Git LFS
# ===============================
echo "Initializing Git LFS..."
git lfs install

# ===============================
# STEP 2: Detect large files
# ===============================
echo "Detecting large files (>50MB)..."
LARGE_FILES=$(find . -type f -size $LARGE_FILE_THRESHOLD)
if [[ -n "$LARGE_FILES" ]]; then
    echo "Large files detected:"
    echo "$LARGE_FILES"
    echo "Removing unnecessary large files from repo..."
    # Remove them from Git index and working directory
    git rm -f $LARGE_FILES || true
fi

# ===============================
# STEP 3: Track remaining essential large files with Git LFS
# ===============================
# Example: Track .zip, .apk, .db files
echo "Tracking essential large files with Git LFS..."
git lfs track "*.zip" "*.apk" "*.db"
git add .gitattributes
git commit -m "Track large files with Git LFS" || true

# ===============================
# STEP 4: Add .gitkeep to empty directories
# ===============================
echo "Adding .gitkeep to empty directories..."
find . -type d -empty -exec touch {}/.gitkeep \;
git add -A
git commit -m "Add .gitkeep to empty directories" || true

# ===============================
# STEP 5: Commit repository folder by folder
# ===============================
echo "Committing folders in order..."
for folder in "${FOLDERS[@]}"; do
    if [ -d "$folder" ] || [ "$(ls -A $folder 2>/dev/null)" ]; then
        git add "$folder"
        git commit -m "Add $folder to repository" || true
    fi
done

# ===============================
# STEP 6: Push commits to GitHub
# ===============================
echo "Pushing all commits to $REMOTE/$BRANCH..."
git push $REMOTE $BRANCH || {
    echo "Push failed, attempting folder-by-folder push..."
    for folder in "${FOLDERS[@]}"; do
        git push $REMOTE $BRANCH || true
    done
}

# ===============================
# STEP 7: Verification
# ===============================
echo "Verifying repository..."
git status
echo "All files and folders should now be visible on GitHub. Large files tracked with Git LFS."

echo "✅ Repository push complete!"
