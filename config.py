

# NOTE: Ensure when you do matching that you compare the .lower() of the remote file to these
INTERESTING_EXTENSIONS = (
    '.bak', '.cftp', '.conf', '.csv', '.db', '.ini', '.jar',
    '.kdb', '.kdbx',
    '.ovpn', '.pem', '.ps1',
    '.sh', '.sql', '.sqlite', '.tar', '.tar.gz', '.tar.bzip',
    '.xls', '.xlsx', '.xlsm', '.zip'
)


INTERESTING_FILENAMES = (
    'backup.zip',
    'config.php',
    'ConsoleHost_history.txt',
    'db.php',
    'flag.txt',
    'id_rsa',
    'MicrosoftEdgeCookiesBackup.dat',
    'ntuser.dat',
    'SAM',
    'SYSTEM',
    'web.config',
    'WinSCP.ini', 
    'ws_ftp.ini',
)


EXCLUDE_FILES = ('IconCache.db',
    'desktop.ini',
)


EXCLUDE_DIRS = (
    '/AppData/Local/Microsoft/local',
)


## --
# Here and below are not used at this time, possible future uses
EXCLUDE_PATTERNS = (
    "iconcache_*",
    "thumbcache_*",
)


APPDATA = (
    'AppData/Roaming/Microsoft/Protect',                # DPAPI master keys
    'AppData/Roaming/Microsoft/Windows/Recent',         # Recent files user has accessed
    '/AppData/Roaming/Microsoft/Windows/PowerShell/PSReadLine/ConsoleHost_history.txt',
)


# Are these interesting?
#/AppData/Roaming/Code/User/globalStorage/state.vscdb
#/AppData/Roaming/Code/User/globalStorage/state.vscdb.backup
#/AppData/Roaming/Code/User/workspaceStorage/1602468096409/state.vscdb
#/AppData/Roaming/Code/User/workspaceStorage/1602468096409/state.vscdb.backup


# NOTE: Can often find python executables on windows here:
#/AppData/Local/Microsoft/WindowsApps/python.exe
#/AppData/Local/Microsoft/WindowsApps/python3.exe
#/AppData/Local/Programs/Python/Python39/python.exe
#/AppData/Local/Programs/Python/Python39/pythonw.exe
