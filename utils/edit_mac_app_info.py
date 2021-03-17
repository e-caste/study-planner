import plistlib

file_to_edit = "dist/Study Planner.app/Contents/Info.plist"

with open(file_to_edit, 'rb') as f:
    contents = plistlib.load(f)

print("Info.plist before editing:", contents)

contents['CFBundleIdentifier'] = 'dev.caste.study-planner'
contents['CFBundleVersion'] = '2.2.0'
contents['CFBundleShortVersionString'] = '2.2.0'
contents['NSRequiresAquaSystemAppearance'] = False  # enable auto dark mode

print("Info.plist after editing:", contents)

with open(file_to_edit, 'wb') as f:
    plistlib.dump(contents, f)
