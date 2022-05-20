#!/usr/bin/env bash

# e-caste
# this script MUST be run after unzipping the archive, before or after copying the app to the /Applications folder

# this is because since I currently don't have an Apple Developer account I can't provide a developer signature to the
# app, and with macOS 12 Apple has removed the option to install an app "From Anywhere" (System Preferences ->
# Security & Privacy -> Allow apps downloaded from:)

# all this script does is removing Study Planner from Apple's quarantine so that you can run it
# all the code of the app, including the code used to compile it automatically, is public at https://github.com/e-caste/study-planner

function remove_from_quarantine() {
    xattr -d com.apple.quarantine "$1" &> /dev/null
    echo "Successfully removed $1 from quarantine."
}

if [[ -d Study\ Planner.app ]]; then
  remove_from_quarantine "Study\ Planner.app"
elif [[ -d /Applications/Study\ Planner.app ]]; then
  remove_from_quarantine "/Applications/Study\ Planner.app"
else
  echo "I can't find the Study Planner app. Please move it here or to the /Applications folder."
fi
