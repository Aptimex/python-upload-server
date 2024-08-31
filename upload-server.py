#!/usr/bin/env python3

#based on https://gist.github.com/traut/5b2b5e21040bbac486c30081049d3b18
import os
import argparse
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler

SECRET = None

class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    
    # Ignore all GETs
    def do_GET(self):
        self.send_response(404)
        self.end_headers()
        print(f"Rejecting request because it's a GET: {self.path}")
        return

    def do_POST(self):
        # Only accept requests that know the secret (if one was specified)
        if SECRET:
            try:
                q = parse_qs(urlparse(self.path).query)
                secret = q.get("secret")[0]
                #print(f"Got secret: {secret}")
                
                if secret != SECRET:
                    raise Exception("Secret doesn't match") 
                    
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
        
        # Write the request body 
        with open(filePath, 'wb') as output_file:
            output_file.write(self.rfile.read(file_length))
        self.send_response(201, 'Created')
        self.end_headers()
        #reply_body = 'Saved "{}"\n'.format(filename)
        #self.wfile.write(reply_body.encode('utf-8'))
        
        print(f"File of size {file_length} saved to {filePath}")

def main(args):
    serveDir = Path(os.path.realpath(args.directory))
    os.chdir(serveDir)
    print(f"Listening on {args.ip}:{args.port}")
    print(f"Files will be save to {serveDir}")
    
    if args.secret:
        global SECRET
        SECRET = args.secret
        print(f"Uploads must include the 'secret={SECRET}' URL parameter")
    
    httpd = HTTPServer((args.ip, args.port), CustomHTTPRequestHandler)
    httpd.serve_forever()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="HTTP server that accepts POST requests and saves them to a file. Best used with \"curl --data-binary '@myFile.txt' IP:PORT/myFile.txt\"")
    parser.add_argument("port", type=int, default=8123, nargs='?', help="Port to listen on")
    parser.add_argument("directory", default="./", nargs='?', help="Directory to save files to")
    parser.add_argument("-i", "--ip", default="0.0.0.0", help="IP to listen on")
    parser.add_argument("-s", "--secret", default=None, help="If specified, this value must be present as a URL 'secret' (case-sensitive) parameter for the server to accept the file. E.g. 1.2.3.4/file?secret=mySuperSecret")
    
    args = parser.parse_args()
    main(args)
