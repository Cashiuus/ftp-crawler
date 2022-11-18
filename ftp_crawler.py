#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
# File:         ftp_crawler.py
# Author:       Cashiuus
# Created:      13-Nov-2022     -     Revised:
#
# Depends:      n/a
# Compat:       3.7+
#
#-[ Usage ]---------------------------------------------------------------------
#
#
# - https://ftputil.sschwarzer.net/documentation
#       - file content is always transferred in binary mode for upload/downloads
#
# - Help: https://stackoverflow.com/questions/31828604/unable-to-download-files-using-ftputil
#
# ==============================================================================
__version__ = '1.0.0'
__author__ = 'Cashiuus'
__license__ = 'MIT'
__copyright__ = 'Copyright (C) 2022 Cashiuus'
## =======[ IMPORTS ]========= ##
import argparse
import logging
import os
import sys
from pathlib import Path
from random import randrange, uniform
from time import sleep, strftime

import ftplib
import ftputil

# Our local patterns config
from config import *


## =========[  TEXT COLORS  ]============= ##
class Colors(object):
    """ Access these via 'Colors.GREEN'   """
    GREEN = '\033[32;1m'    # Green
    YELLOW = '\033[01;33m'  # Warnings/Information
    RED = '\033[31m'        # Error or '\033[91m'
    ORANGE = '\033[33m'     # Debug
    BLUE = '\033[01;34m'    # Heading
    PURPLE = '\033[01;35m'  # Other
    GREY = '\e[90m'         # Subdued Text
    BOLD = '\033[01;01m'    # Highlight
    RESET = '\033[00m'      # Normal/White
    BACKBLUE = '\033[44m'   # Blue background
    BACKCYAN = '\033[46m'   # Cyan background
    BACKRED = '\033[41m'    # Red background
    BACKWHITE = '\033[47m'  # White background

## =======[ Constants & Settings ]========= ##
DEBUG = False
BASE_DIR = Path(__file__).resolve(strict=True).parent       # one parent means dir of this file
SAVE_DIR = BASE_DIR / "saved"
LOG_FILE = BASE_DIR / "ftp_crawler.log"


# Logging Cookbook: https://docs.python.org/3/howto/logging-cookbook.html
# This first line must be at top of the file, outside of any functions, so it's global
logger = logging.getLogger(__name__)


# ==========================[ HELPERS ]========================== #
def delay(max=10):
    """Generate random number for sleep function
            Usage: time.sleep(delay(max=30))
    """
    #return randrange(2, max, 1)
    return round(uniform(0, max), 2)     # Random float between 0 and max with '2' decimal precision (e.g. 1.24)


# ==========================[ BEGIN APPLICATION ]========================== #

class MyFTPSession(ftplib.FTP):
    """ A session factory object for working with target FTP across many use cases.
        NOTE: Don't use MySession itself, but pass it as session_factory argument like this:

        with ftputil.FTPHost(target, username, password, port=2121, session_factory=MyFTPSession) as ftp_host:
            # do normal stuff with the connection
    """
    def __init__(self, target, username, password, port=21):
        ftplib.FTP.__init__(self)
        self.connect(target, port)
        self.login(username, password)


def get_total_filecount(ftpobj):
    logger.debug('Started count function')
    cnt = 0
    # For some reason, this is only resulting in a total count of 15, which is not even close to correct
    #cnt = sum([len(files) for (dirname, subdirs, files) in ftpobj.walk('/')])
    for (dirname, subdirs, files) in ftpobj.walk('/'):
        cnt += len(files)
    logger.debug('Finished count function, with total at: {}'.format(cnt))
    return cnt


def download_remote_file_helper(ftpobj, download_file, output_dir):
    """ Use an existing FTP connection object and download a provided remote file. """
    dest_file = output_dir / Path(download_file).name
    logger.debug("var output_dir: {}".format(output_dir))
    logger.debug("var download_file: {}".format(download_file))
    logger.debug("var dest_file: {}".format(dest_file))
    if dest_file:
        ftpobj.download(download_file, dest_file)
        logger.info("File has been downloaded: {}".format(str(download_file)))
        print("[*] File has been downloaded: {}".format(str(download_file)))
        logger.debug("Finished ftpobj.download() operation")
    else:
        logger.debug("var dest_file is empty, something went wrong (e.g. dest_file was a dir not a file)")
    return


def download_remote_file(target, username, password, download_file, output_dir):
    """ Download a remote file from FTP server to our local system as a fully standalone function for one-off's.

        download_file - full remote path of the file you wish to download
        output_dir    - the local destination directory in which to save the file

    """
    #with ftputil.FTPHost(target, username, password, session_factory=MyFTPSession) as ftp_host:
    with ftputil.FTPHost(target, username, password) as ftp:
        print("[*] Connected to FTP Server. Attempting to retrieve specified file for download")
        # May need to enable hidden for this to always work
        # Note, if download_file is a dir for some reason, then dest_file will be empty here
        dest_file = output_dir / Path(download_file).name
        logger.debug("var output_dir: {}".format(output_dir))
        logger.debug("var download_file: {}".format(download_file))
        logger.debug("var dest_file: {}".format(dest_file))
        if dest_file:
            ftp.download(download_file, dest_file)
            logger.debug("Finished ftp.download operation")
        else:
            logger.debug("var dest_file is empty, something went wrong (e.g. dest_file was a dir not a file)")
    return


def generate_listing_file(input_list, listing_file):
    """ Process and input list and write it to a file. """
    if not input_list:
        return
    print("[*] Generating the listing file for your review")
    logger.info("Generating the listing file for your review")
    with open(listing_file, 'w') as fl:
        for line in input_list:
            fl.write(str(line) + "\n")
    return


def crawl_ftpserver_with_report(target, username, password, output_dir, all_files=False, include_hidden=True):
    """ Crawl the FTP server's entire contents and output full list of files to a text file for review.

        all_files           - Toggle on listing ALL files in the saved list instead of just pattern matches, often useful
        include_hidden      - If FTP server supports it, enable view/access of hidden dirs/files (Default: True)
    """
    with ftputil.FTPHost(target, username, password) as ftp:
        logger.info("Connected to FTP server successfully and now have an ftp session object")
        print("[*] Connected to FTP Server")
        total = get_total_filecount(ftp)
        i = 1
        matches = []
        if include_hidden:
            # Try to enable showing hidden files/dirs also - only if FTP server supports it
            ftp.use_list_a_option = True
        for (dirname, subdirs, files) in ftp.walk("/"):
            logger.debug("walk vars: dirname: {} - subdirs: {} - files: {}".format(dirname, subdirs, files))
            i += 1
            #print("\r[*] Crawled {} of {} Files".format(i, total), end='')
            print("[*] Crawled {} Files".format(i), end='\r')
            if dirname in EXCLUDE_DIRS:
                continue
            if files:
                for f in files:
                    #logger.debug("f var: {}".format(f))
                    full_filename = Path(ftp.path.join(dirname, f))
                    if all_files:
                        # Instead of iter'ing all files, I really could just extend the files list right here
                        #matches.extend([os.path.join(dirname, x) for x in files])
                        matches.append(full_filename)
                    else:
                        # -- pattern matching --
                        suf = full_filename.suffixes
                        if len(suf) > 1:
                            # File is a multi-extension (e.g. ".tar.gz") and requires more code for an accurate match
                            real_suffix = '.'.join([x.lower() for x in suf])
                        elif len(suf) == 1:
                            real_suffix = full_filename.suffix.lower()
                        else:
                            logger.debug("File with no extension: {}".format(full_filename))
                        
                        # Approach: Add matches to list for all extensions as well as exact filenames, 
                        # but also download matched filenames
                        if real_suffix in INTERESTING_EXTENSIONS:
                            if f not in EXCLUDE_FILES and 'thumbcache_' not in f:
                                matches.append(full_filename)
                    # Regardless, of our reporting mode above, still check and download files of interest
                    if f in INTERESTING_FILENAMES:
                        if full_filename not in matches: matches.append(full_filename)
                        print("\n[*] Found a matching file of interest for download: {}".format(full_filename))
                        download_remote_file_helper(ftp, full_filename, output_dir)
                        sleep(delay(max=2))
        print()
        # -- end of loop
    return matches


def crawl_ftpserver(target, username, password, output_dir, include_hidden=True):
    """ This function is defunct and replaced by the function above it. """
    with ftputil.FTPHost(target, username, password) as ftp:
        print("[*] Connected to FTP Server. Now crawling, please wait...")
        i = 1
        matches = []
        if include_hidden:
            # Try to enable showing hidden files/dirs also - only if FTP server supports it
            ftp.use_list_a_option = True
        for (dirname, subdirs, files) in ftp.walk("/"):
            #d = ftp.getcwd()
            if DEBUG:print("[DBG] dirname var: {}".format(dirname))
            logger.debug("dirname var: {}".format(dirname))
            ftp.chdir(dirname)
            if subdirs:
                if DEBUG:print("[DBG] subdirs var: {}".format(subdirs))
                logger.debug("subdirs var: {}".format(subdirs))
                for sub in subdirs:
                    try:
                        if DEBUG:print("[DBG] Attempting to cd into subdir 'sub': {}".format(sub))
                        logger.debug("Attempting to cd into subdir 'sub': {}".format(sub))
                        ftp.chdir(sub)
                    except ftputil.error.PermanentError as e:
                        # This is typically a 550 permission denied error, just skip this dir
                        continue
                    print("\n[*] Current Dir: {}".format(ftp.getcwd()))
                    logger.info("[*] Current Dir: {}".format(ftp.getcwd()))
                    print("---------------")
                    names = ftp.listdir(ftp.curdir)
                    if names:
                        print("Contents: {}".format(', '.join([x for x in names])))
                        logger.info("Contents: {}".format(', '.join([x for x in names])))
                    else:
                        print()
                    if DEBUG:print("[DBG] files var: {}".format(files))
                    logger.debug("files var: {}".format(files))
                    for f in files:
                        #if f.startswith(SEARCH_FILE):
                        if DEBUG:print("[DBG] f var: {}".format(f))
                        logger.debug("f var: {}".format(f))
                        (directory, fname) = os.path.split(f)
                        if fname in INTERESTING_FILES:
                            print("[*] Downloading matching file: {}".format(fname))
                            logger.info("[*] Downloading matching file: {}".format(fname))
                            fname.download(f, f"{i}-{f}")
                            i += 1
                        # Match against a list of file extensions we care about
                        # NOTE: Another way for single pattern would be:
                        #   for f in fnmatch.filter(files, '*.txt'):
                        if fname.endswith(('.ctb', 'txt', 'db', 'exe')):
                            print("[*] Possibly interesting file: {}".format(f))
                            logger.info("[*] Possibly interesting file: {}".format(f))
                            #matches.append(os.path.join(dirname, f)
                            matches.append(f)
                    print("------------------------------\n\n")
                    #ftp.chdir(ftp.pardir)
                    ftp.chdir("..")
                    if DEBUG:print("[DBG] CD'ed up, CWD: {}".format(ftp.getcwd()))
                    logger.debug("CD'ed up, CWD: {}".format(ftp.getcwd()))
                    sleep(delay(max=2))
            else:
                # No subdirs, so just enumerate files in this main 'dirname' directory
                # TODO: refactor this
                print("\n[*] Current Dir: {}".format(ftp.getcwd()))
                logger.info("[*] Current Dir: {}".format(ftp.getcwd()))
                print("---------------")
                for f in files:
                    if DEBUG:print("[DBG] f var: {}".format(f))
                    logger.debug("f var: {}".format(f))
                    #(directory, fname) = os.path.split(f)
                    full_filename = ftp.path.join(dirname, f)
                    if f in INTERESTING_FILES:
                        print("[*] Downloading matching file: {}".format(f))
                        logger.info("[*] Downloading matching file: {}".format(f))
                        ftp.download(f, f"{i}-{f}")     # TODO: Refactor this
                        if full_filename not in matches:
                            matches.append(full_filename)
                        i += 1
                    # Match against a list of file extensions we care about
                    # NOTE: Another way for single pattern would be:
                    #   for f in fnmatch.filter(files, '*.txt'):
                    if f.endswith(('.ctb', 'txt', 'db', 'exe')):
                        print("[*] Possibly interesting file: {}".format(f))
                        logger.info("[*] Possibly interesting file: {}".format(f))
                        #matches.append(os.path.join(dirname, f)
                        matches.append(full_filename)
            print("------------------------------\n\n")
            if DEBUG:print("[DBG] CWD is: {}".format(ftp.getcwd()))
            logger.debug("CWD is: {}".format(ftp.getcwd()))
            sleep(delay(max=2))
        ftp.chdir("..")
        sleep(delay(max=2))
    print("[*] List of matching/interesting files:")
    logger.info("[*] List of matching/interesting files:")
    if matches:
        print("{0}".format([x for x in matches]))
        logger.info("{0}".format([x for x in matches]))
    else:
        print(" -- None --")
        logger.info(" -- None --")
    return


def main():
    print("[*] FTP Crawler is now launching...")
    if DEBUG:
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        # FileHandler accepts string or Path object for filename; mode 'w' truncates log, 'a' appends
        fh = logging.FileHandler(LOG_FILE, mode='a')
        # Or you can use a rotating file handler: https://docs.python.org/3/howto/logging-cookbook.html#cookbook-rotator-namer
        #fh = handlers.RotatingFileHandler(LOG_FILE, max_bytes=104857600, backupCount=4)
        ch.setLevel(logging.ERROR)
        fh.setLevel(logging.DEBUG)
        # Message Format - See here: https://docs.python.org/3/library/logging.html#logrecord-attributes
        formatter = logging.Formatter('%(funcName)s : %(levelname)-8s %(message)s')
        ch.setFormatter(formatter)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s: %(message)s')
        fh.setFormatter(formatter)
        # Add the handlers to the logger
        logger.addHandler(fh)
        logger.addHandler(ch)
    logger.debug('Logger initialized')

    parser = argparse.ArgumentParser(description="FTP crawler for files of interest to review or download")
    parser.add_argument('-t', "--target", dest='target', help='IP/URL of FTP server target')
    parser.add_argument("-u", "--user", dest='user', default="anonymous", help="Auth username (default: anonymous)")
    parser.add_argument("-p", "--pass", dest='password', default="anonymous", help="Auth password (default: anonymous)")

    parser.add_argument('-a', '--all-files', dest='all_files', action='store_true',
                        help='Toggle listing all files instead of only matched patterns')
    parser.add_argument("-f", "--download-file", dest='dl_file', help="Specify a single remote file to download (full path) and skip full crawl")
    parser.add_argument("-o", "--output-dir", dest='output',
                        help="Specify output directory for saving downloaded files")

    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Display error information")
    args = parser.parse_args()

    if not args.target:
        parser.print_help()
        sys.exit(1)
    
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = SAVE_DIR
    logger.debug("var output_dir: {}".format(output_dir))

    ftp_target = args.target
    logger.debug("var ftp_target: {}".format(ftp_target))

    if not output_dir.is_dir():
        print("[*] Output directory doesn't exist, so creating it first")
        logger.debug("Output dir does not exist, calling makedirs")
        os.makedirs(output_dir)
    else:
        logger.debug("Output dir already exists")
    # Sanity check
    if not output_dir.is_dir():
        print("[ERR] Failed to create save directory, fix and try again")
        sys.exit(1)
    
    LISTING_FILE_NAME = "FTP_Files_listing_" + ftp_target + "_" + strftime('%Y%m%d') + ".txt"
    LISTING_FILE = output_dir / LISTING_FILE_NAME

    u = args.user if args.user else "anonymous"
    p = args.password if args.password else "anonymous"

    if args.dl_file:
        download_remote_file(ftp_target, u, p, args.dl_file, output_dir)
    else:
        if args.all_files:
            results = crawl_ftpserver_with_report(ftp_target, u, p, output_dir, all_files=True)
        else:
            results = crawl_ftpserver_with_report(ftp_target, u, p, output_dir)
        print("[*] Finished crawling FTP server")
        generate_listing_file(results, LISTING_FILE)
        # This assumes that we ran crawl_ftpserver_with_report() and saved file list
        print("[*] List of all files on FTP server are in saved file for review: {}".format(output_dir / LISTING_FILE))
    logger.debug('Program end')
    return


if __name__ == '__main__':
    #crawl_ftpserver()
    main()
