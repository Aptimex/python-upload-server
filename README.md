# Python Upload Server

Pretty simple Python server that accepts POST requests and saves the body contents to a file. Very useful for transferring files from Windows to Linux. 

Features:
- Specify a directory to save files to (default `./`)
- Specify the IP to listen on (default `0.0.0.0`)
- Specify the port to listen on (default `8123`)
- Specify an optional secret value that must be included in the `secret` URL parameter or else the request will be rejected

If a path is specified in the request, the part after the final `/` (minus any URL parameters or such) will be treated as the filename that it should be saved to. For example:
```
POST http://192.168.1.2:8123/myFile.txt?hello=garbage
```
will cause the file to be saved to `myFile.txt`. 

## Usage
```
usage: upload-server.py [-h] [-i IP] [-s SECRET] [port] [directory]

HTTP server that accepts POST requests and saves them to a file. Best used with "curl --data-binary '@myFile.txt'
IP:PORT/myFile.txt"

positional arguments:
  port                  Port to listen on
  directory             Directory to save files to

options:
  -h, --help            show this help message and exit
  -i IP, --ip IP        IP to listen on
  -s SECRET, --secret SECRET
                        If specified, this value must be present as a URL 'secret' (case-sensitive) parameter for the server to
                        accept the file. E.g. 1.2.3.4/file?secret=mySuperSecret
```
