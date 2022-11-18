FTP Crawler
============



This is a rudimentary tool to crawl and scrape files of interest from a target FTP server.

Known to Work on:
- FTP servers running with anonymous access


Features:
- Authenticate to FTP server, as anonymous by default if you don't pass creds as args
- Traverse the entire accessible file system based on your permissions to search for files by defined patterns
- If supported by FTP server, includes files & dirs marked as Hidden


## Installing


```
git clone https://github.com/Cashiuus/ftp-crawler
cd ftp-crawler
# Optionally, create a virtualenv (only 1 dependency at this time, so not really necessary)
python3 -m venv .venv
python3 -m pip install -r requirements.txt
```




## Usage

```bash
ftp_crawler.py [-t TARGET] [-u USER] [-p PASSWORD] [-f DL_FILE] [-o OUTPUT] [--version] [-d] [-h]

options:
  -h, --help                            Show this help message and exit
  -t TARGET, --target TARGET            IP/URL of FTP server target
  -u USER, --user USER                  Auth username (Default: anonymous)
  -p PASSWORD, --pass PASSWORD          Auth password (Default: anonymous)

  -a, --all-files                       Toggle to list all files instead of only matched patterns (Default: False)
  -f DL_FILE, --download-file DL_FILE   Specify a remote file to download (full path); NOTE: Skips reporting routine
  -o OUTPUT, --output-dir OUTPUT        Specify output directory for saving downloaded files (Default: ./saved/)

  --version                             Show program's version number and exit
  -d, --debug                           Display error information
```


## Examples

Enumerate an open FTP server to determine what's on it, by default looking only for interesting file extensions
or save an output list of all files on the server with `-a, --all-files`:
```bash
ftp_crawler.py -t 10.10.1.20

ftp_Crawler.py -t 10.10.1.20 --all-files
```

Enumerate an FTP server where user and pass is known
```bash
ftp_crawler.py -t 10.10.1.20 -u joe -p SecretPassword
```

After reviewing the saved file list, you want to download a file you saw that may be interesting
```bash
ftp_crawler.py -t 10.10.1.20 -f /full/path/to/file.txt
```


