# Python Upload Server

Relatively simple Python server that accepts POST requests and saves the body contents to a file. I mainly use it for transferring files from Windows to Linux. 

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
usage: upload-server.py [-h] [-d DIRECTORY] [-i IP] [-s SECRET] [port]

HTTP server that accepts POST requests and saves them to a file. Best used with "curl --data-binary '@myFile.txt' IP:PORT/myFile.txt"

positional arguments:
  port                  Port to listen on

options:
  -h, --help            show this help message and exit
  -d DIRECTORY, --directory DIRECTORY
                        Directory to save files to
  -i IP, --ip IP        IP to listen on
  -s SECRET, --secret SECRET
                        If specified, this (case-sensitive, alphanumeric) value must be present as a URL parameter for the server to
                        accept the file. E.g. http://1.2.3.4/file?mySecretParam
```

## Examples
Start the server with a secret parameter, listening on 8080, saving files to the current working dir:
```
python3 ./upload-server.py 8080 -s mySecretParam
```

Send a file in the current working dir to the server using PowerShell:
```PowerShell
Invoke-WebRequest -Uri http://1.2.3.4:8080/differentName.bin?mySecretParam -Method Post -InFile '.\myFile.bin'
```
- Also works with `Invoke-RestMethod` using the same parameters

Send a file in the current working dir to the server using curl:
```bash
curl --data-binary '@myFile.bin' http://1.2.3.4:8080/differentName.bin?mySecretParam
```
- Also works with `curl.exe` on recent versions of Windows

## Security
If you don't specify a `--secret` value, anyone who can connect to this server can upload files to your computer. You probably don't want that. 

Using the `--secret` option with a non-trivial secret value should be enough to ensure random scans and pokes won't be able to upload any files. Still, I wouldn't leave this exposed to the Internet or other hostile networks for any longer than you have to. 

Traffic is all unencrypted over HTTP, so anyone sniffing it is going to get your secret value and can then upload files to your computer. If this is a concern, run this behind a reverse proxy that adds SSL/TLS encryption with a legitimate certificate. 

Python's `urllib` library handles all the URL parsing, which eventually feeds into the filenames written to disk. I've verified that at least basic path-traversal exploit attempts do not work for writing files outside the specified directory, but the library documentation [specifically says that it does not perform URL validation](https://docs.python.org/3/library/urllib.parse.html), so more advanced attempts might work. Again, specify a secret and don't leave this running for longer than necessary to minimize your risk here. 
