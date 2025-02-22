#!/usr/bin/env python3

#based on https://gist.github.com/traut/5b2b5e21040bbac486c30081049d3b18
import os
import argparse
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler

# SECRET is set dynamically at runtime with -s
SECRET = None

# PART_SIZE is hardcoded; writes out larger files in chunks of this size to limit memory usage 
# This also significantly speeds up large transfers, but idk why
PART_SIZE = 256 * 1024 * 1024 #256MB

class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    
    # Ignore all GETs
    def do_GET(self):
        self.send_response(404)
        self.end_headers()
        print(f"Rejecting request because it's a GET: {self.path}")
        return

    def do_POST(self):
        # If a secret was specified, immediately ignore any requests that do not include it
        if SECRET:
            try:
                q = parse_qs(urlparse(self.path).query, keep_blank_values=True)
                if not q.get(SECRET):
                    raise Exception(f"Secret value '{SECRET}' not found in URL parameters of request: {self.path}") 
                    
            except Exception as e:
                # If there's any issue at all, minimal 404 response
                self.send_response(404)
                self.end_headers()
                print(f"Rejecting request: {self.path}")
                print(f"Reason: {e}")
                return
        
        # os.chdir was already used on args.directory in main(), so cwd is root
        root = Path(os.path.realpath("./")) 
        
        # Sane default filename
        filename = os.path.basename(urlparse(self.path).path)
        if filename == "" or filename == "/":
            filename = "savedFile"
        filePath = os.path.join(root, filename)
        
        file_length = int(self.headers['Content-Length'])
        
        # Avoid overwriting existing files
        i = 1
        while os.path.exists(filePath):
            if filePath[-2:] == f"_{i}":
                i += 1
                filePath = f"{filePath[:-2]}_{i}"
            else:
                filePath = f"{filePath}_{i}"
        
        # Write the request body to a file
        with open(filePath, 'wb') as output_file:
            print(f"Recieving file '{filename}' with size {file_length} from {self.client_address[0]}")
            
            numParts = file_length // PART_SIZE
            if file_length % PART_SIZE != 0:
                numParts += 1
                
            for i in range(numParts):
                print(f"Writing part {i+1} of {numParts}")
                remainingSize = file_length - (i * PART_SIZE)
                output_file.write(self.rfile.read(min(PART_SIZE, remainingSize)))
        
        self.send_response(201, 'Created')
        self.end_headers()
        
        print(f"File of size {file_length} bytes saved to {filePath}")
        print()
    
    # Treat PUT just like POST
    def do_PUT(self):
        self.do_POST()

def main(args):
    # Make sure we're saving to a valid directory
    serveDir = Path(os.path.realpath(args.directory))
    if not os.path.isdir(serveDir):
        print(f"Path {serveDir} does not exist or is not a directory, exiting")
        exit(1)
    os.chdir(serveDir)
    
    # Display important server parameters being used
    print(f"Listening on {args.ip}:{args.port}")
    print(f"Files will be saved to {serveDir}")
    if args.secret:
        global SECRET
        SECRET = args.secret
        print(f"Uploads must include the '{SECRET}' URL parameter")
        
        if not SECRET.isalnum():
            print("WARNING: secret contains non-alphanumeric characters; this server might not be able to recognize it in requests.")
    
    print()
    # Start the server
    httpd = HTTPServer((args.ip, args.port), CustomHTTPRequestHandler)
    httpd.serve_forever()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="HTTP server that accepts POST and PUT requests and saves the body content to a file. Best used with \"curl -T ./myFile.txt IP:PORT/myFile.txt\"")
    parser.add_argument("port", type=int, default=8123, nargs='?', help="Port to listen on; default is 8123")
    parser.add_argument("-d", "--directory", default="./", help="Directory to save files to")
    parser.add_argument("-i", "--ip", default="0.0.0.0", help="IP to listen on")
    parser.add_argument("-s", "--secret", default=None, help="If specified, this (case-sensitive, alphanumeric) value must be present as a URL parameter for the server to accept the file. E.g. http://1.2.3.4:8123/file?mySecretParam")
    
    args = parser.parse_args()
    main(args)
