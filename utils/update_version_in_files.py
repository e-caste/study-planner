nv = (2, 2, 1)  # new version to set
nv_str = '.'.join(map(str, nv))

# update windows_version_file.py
contents = f"""# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
    ffi=FixedFileInfo(
        # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
        # Set not needed items to zero 0.
        filevers=({nv[0]}, {nv[1]}, {nv[2]}, 0),
        prodvers=({nv[0]}, {nv[1]}, {nv[2]}, 0),
        # Contains a bitmask that specifies the valid bits 'flags'r
        mask=0x3f,
        # Contains a bitmask that specifies the Boolean attributes of the file.
        flags=0x0,
        # The operating system for which this file was designed.
        # 0x4 - NT and there is no need to change it.
        OS=0x4,
        # The general type of file.
        # 0x1 - the file is an application.
        fileType=0x1,
        # The function of the file.
        # 0x0 - the function is not defined for this fileType
        subtype=0x0,
        # Creation date and time stamp.
        date=(0, 0)
    ),
    kids=[
        StringFileInfo(
            [
                StringTable(
                    u'040904B0',
                    [StringStruct(u'CompanyName', u'Enrico Castelli'),
                     StringStruct(u'FileDescription', u'Study Planner'),
                     StringStruct(u'FileVersion', u'{nv[0]}.{nv[1]}.{nv[2]}'),
                     StringStruct(u'InternalName', u'Study Planner'),
                     StringStruct(u'LegalCopyright', u'Copyright (c) Enrico Castelli'),
                     StringStruct(u'OriginalFilename', u'main.py'),
                     StringStruct(u'ProductName', u'Study Planner'),
                     StringStruct(u'ProductVersion', u'{nv[0]}.{nv[1]}.{nv[2]}')])
            ]),
        VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
    ]
)
"""
with open("windows_version_file.py", "w") as f:
    f.write(contents)

# update backend.py
with open("backend.py", 'r+') as f:
    lines = f.readlines()
    f.seek(0)
    for line in lines:
        if not line.startswith("CURRENT_RELEASE = "):
            f.write(line)
        else:
            f.write(f"""CURRENT_RELEASE = "{nv_str}"\n""")

# update utils/edit_mac_app_info.py
with open("utils/edit_mac_app_info.py", 'r+') as f:
    lines = f.readlines()
    f.seek(0)
    for line in lines:
        if line.startswith("contents['CFBundleVersion'] ="):
            f.write(f"contents['CFBundleVersion'] = '{nv_str}'\n")
        elif line.startswith("contents['CFBundleShortVersionString'] = "):
            f.write(f"contents['CFBundleShortVersionString'] = '{nv_str}'\n")
        else:
            f.write(line)
