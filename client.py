import io
import socket
import struct
import time
import picamera
import json

client_socket = socket.socket()

client_socket.connect(('18.190.147.87', 8080))  # ADD IP HERE

BUFFER_SIZE = 1024

# Make a file-like object out of the connection
connection = client_socket.makefile('wb')
print("start sending...")
try:
    camera = picamera.PiCamera()
    #camera.vflip = True
    camera.resolution = (1024, 768)
    # Start a preview and let the camera warm up for 2 seconds
    camera.start_preview()
    time.sleep(2)
    

    # Note the start time and construct a stream to hold image data
    # temporarily (we could write it directly to connection but in this
    # case we want to find out the size of each capture first to keep
    # our protocol simple)
    start = time.time()
    stream = io.BytesIO()
    for foo in camera.capture_continuous(stream, 'jpeg'):
        # Write the length of the capture to the stream and flush to
        # ensure it actually gets sent
        connection.write(struct.pack('<L', stream.tell()))
        connection.flush()
        # Rewind the stream and send the image data over the wire
        stream.seek(0)
        connection.write(stream.read())
        # If we've been capturing for more than 30 seconds, quit
        #if time.time() - start > 60:
            #break
        # Reset the stream for the next capture
        stream.seek(0)
        stream.truncate()
        

        response = client_socket.recv(BUFFER_SIZE)
        response = response.decode("utf-8")
        print("Received data", response)
        if response != "none" and not response:
            data = json.loads(response)
            print(data['class'])
            print(data['x'])
            print(data['y'])
        
    # Write a length of zero to the stream to signal we're done
    connection.write(struct.pack('<L', 0))
    
finally:
    print("Sending Ended...")
    connection.close()
    client_socket.close()

