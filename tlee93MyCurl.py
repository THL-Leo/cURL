import socket
import argparse
import sys
import re

HEADER_END_SIGNAL = b"\r\n\r"
BUFFER_SIZE = 1024
TIMEOUT = 10

url = None
path = None 
server_name = None 
server_IP = None 
server_port = None
client_IP = None
client_port = None
data = None

parser = argparse.ArgumentParser(description='Getting HTTP request')
parser.add_argument('input', type=str, help='User input', nargs='+')
cmd_input = parser.parse_args().input

url = cmd_input[0]

# parsed = re.search(r"(?P<http>https*)://?(?P<site>(\w+\.?)+):?(?P<port>\d*)?(?P<path>/.*)?", url)
parsed = re.search(r"((?P<http>https?):\/\/)?(?P<site>([a-zA-Z0-9]+\.?)+)(?<path>\/([a-zA-Z0-9.])*)?(:(?<port>[0-9]+))?", url)
# check if http field is not https
if (parsed.group('http') == 'https'):
    sys.exit("ERROR: HTTPS URLs are not supported.")

# get the server_name and server_IP if available
if len(cmd_input) == 2:
    server_name = cmd_input[1]
    server_IP = parsed.group('site')
else:
    server_name = parsed.group('site')

# get severPort if possible else defualt to 80
if parsed.group('port') == '443':
    sys.exit("ERROR: Destination port not available")
elif parsed.group('port') != '':
    server_port = int(parsed.group('port'))
else:
    server_port = 80

# get path if available
path = parsed.group('path')
if path == None:
    path = "\\"

# running the socket
sock =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # new socket

if server_IP == None:
    server_IP = socket.gethostbyname(server_name)

# connecting process
sock.connect((server_IP, server_port))
sock.settimeout(TIMEOUT)
client_IP, client_port = sock.getsockname()

# sending process
request = "GET {} HTTP/1.1\r\nHost:{}\r\n\r\n".format(path, server_name)
sock.send(request.encode())

data = ""
try: 
    while True:
        buffer = sock.recv(BUFFER_SIZE)
        if len(buffer) < BUFFER_SIZE:
            data += buffer.decode()
            break
        data += buffer.decode()
        
except Exception as e:
    sock.close()
    sys.exit("Error while receiving data.")

status = re.search(r"(HTTP/.*)?", data).group(1)
content = re.split(r"(.*)\r\n\r\n(.*)", data)[-1]

# Writing current HTTP data
f = open("HTTPoutput.html", "w")
f.write(content)
f.close()

# # Writing a log message in Log.csv
log_message = ""
print_message = ""

status_code = re.search(r"\w+ (\d*)? \w+", status).group(1)

if status_code == '200':
    get_gud = "Successful"
else:
    get_gud = "Unsucessful"

print("{} {} {}".format(get_gud, url, status))
if "chunked" in data:
    print("ERROR: Chunk encoding is not supported")

log_message += "{}, {}, {}, {}, {}, {}, {}, {}, {}\n".format( get_gud, status_code, 
                                                            url, server_name, 
                                                            client_IP, server_IP,
                                                            client_port, server_port,
                                                            status)

f = open("Log.csv", "a")
f.write(log_message)
f.close()