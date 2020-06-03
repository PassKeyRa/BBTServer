#!/usr/bin/env python3
import socket
import sys
import threading
import subprocess

def usage():
    print('''Usage:
python3 BBTServer.py <port>

<port> - 1-65535, 8081 by default''')

def recvall(soqet):
    BUFF_SIZE = 4096
    data = b''
    while True:
        part = soqet.recv(BUFF_SIZE)
        data += part
        if len(part) < BUFF_SIZE:
            break
    return data 

def howard_gives_file(head):
    filename = head[5:head.index(' HTTP', 4)]
    print('Reading file', filename)
    
    try:
        lfile = open(filename, 'rb').read()
    except Exception:
        response = ('''HTTP/1.0 404 Not Found''').encode()
        return response

    response = ('''HTTP/1.0 200 OK
Content-type: text/plain
Content-length: ''' + str(len(lfile)) + '''

''').encode()
    response += lfile
    return response

def bernadette_takes_file(data, content_length):
    tmpdata = data.decode()
    boundary = tmpdata[:tmpdata.index('\r\n')]
    filename = tmpdata[tmpdata.index('filename')+10:tmpdata.index('"', tmpdata.index('filename')+10)]
    if '/' in filename:
        filename.split('/')
    start = data.index(b'\r\n\r\n') + 4
    stop = data.index(boundary.encode(), start)-2
    file_data = data[start:stop]
    with open(filename, 'wb') as f:
        f.write(file_data)
    response = ('''HTTP/1.0 200 OK''').encode()
    return response

def leonard_got_connection(leonard):
    req = recvall(leonard).decode()
    print(req)
    data = b''
    http_type = 0
    if 'POST' in req.split('\n')[0]:
        data = recvall(leonard)
        http_type = 1

    response = b''
    try:
        if http_type == 0:
            response = howard_gives_file(req.split('\n')[0])
        else:
            content_length = int(req[req.index('Content-Length: ') + 16:req.index('\n', req.index('Content-Length: ') + 16)])
            response = bernadette_takes_file(data, content_length)
    except Exception:
        print('Error! Something went wrong')
        leonard.close()
        return

    print(response.decode()+'\n')
    leonard.send(response)
    leonard.send('\n\n'.encode())
    leonard.close()


def main():
    bip = '0.0.0.0'
    bport = 8081
    
    if '--help' in sys.argv or '-h' in sys.argv:
        usage()
        exit(0)

    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
            if port < 1 or port > 65535:
                raise WrongPort()
            else:
                bport = port
        except Exception:
            print("Port", sys.argv[1], "is wrong! Port 8081 selected")

    sheldon = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sheldon.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sheldon.bind((bip, bport))
    sheldon.listen(5)
    print('[STATUS] Sheldon is listening for connections on port', bport, '(' + subprocess.check_output(['hostname', '-I']).decode().strip().replace(' ', ', ') + ')')

    while True:
        leonard, i = sheldon.accept()
        print('[STATUS] Incoming connection from %s:%d -> Leonard' % (i[0], i[1]))

        penny = threading.Thread(target=leonard_got_connection,args=(leonard,))
        penny.start()


if __name__ == '__main__':
    main()
