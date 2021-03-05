# this would be a job for sed, but BSD sed is quite complex, and Python is so much simpler
key_value_pair = "\t<key>NSRequiresAquaSystemAppearance</key>\n\t<false/>\n"
insert_before = "</dict>\n"
file_to_edit = "Study Planner.app/Contents/Info.plist"

with open(file_to_edit, 'r+') as f:
    lines = f.readlines()
    insert_index = lines.index(insert_before)
    lines.insert(insert_index, key_value_pair)
    f.seek(0)
    for line in lines:
        f.write(line)
