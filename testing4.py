import http.server
import socketserver
import base64
import cv2
from object_detector import*
import numpy as np




class MyServer(http.server.SimpleHTTPRequestHandler):
    temp = "ON"  # Declare temp as a class variable
    captured_image = None
    detector = HomogeneousBgDetector()
    cap = cv2.VideoCapture(0)
    (x,y) = (0,0)
    img = None


    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _redirect(self, path):
        self.send_response(303)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', path)
        self.end_headers()

    def do_GET(self):

        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = f'''
                <html>
                <body 
                    style="width:960px; margin: 20px auto;">
                    <h1>Welcome to Standalone Automated Dimension Measurement System</h1>
                    <p style="font-size: 20px;">Current status of the system is : {self.temp}</p>
                    <p style="font-size: 20px;">The Breadth of measured Object is (in cm) : {self.x}</p>
                    <p style="font-size: 20px;">The Length of measured Object is (in cm) : {self.y}</p>
                    <form action="/do_POST" method="POST">
                        Buttons :
                        <input type="submit" name="submit" value="On" style="width: 200px; height: 60px; font-size: 24px;">
                        <input type="submit" name="submit" value="Off" style="width: 200px; height: 60px; font-size: 24px;">
                        <input type="submit" name="submit" value="Next" style="width: 200px; height: 60px; font-size: 24px;">
                    </form>
                    <h2>Captured Image</h2>
                    f'<img src="data:image/jpeg;base64,{self.captured_image}" alt="Captured Image">'
                    
                </body>
                </html>
            '''
            self.wfile.write(html.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

    def do_POST(self):
        global captured_image
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode("utf-8")
        post_data = post_data.split("=")[1]

        if post_data == 'On':
            MyServer.temp = "ON"  # Modify the class variable
            print("Button clicked: ON")
            MyServer.cap = cv2.VideoCapture(0)
            # Capture an image in a separate thread

        elif post_data == 'Off':
            MyServer.temp = "OFF"  # Modify the class variable
            print("Button clicked: OFF")
            MyServer.cap.release()
        else:
            for i in range(5):
                _, MyServer.img = MyServer.cap.read()


            print("image captured")
            contours = MyServer.detector.detect_objects(MyServer.img)
            for cnt in contours:
                (MyServer.x, MyServer.y), (w, h), angle = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(cv2.minAreaRect(cnt))
                box = np.int0(box)
                cv2.polylines(MyServer.img, [box], True, (255, 0, 0), 2)

                MyServer.x = round(w/27.71, 2)
                MyServer.y = round(h/27.55,2)
            _, img_base64 = cv2.imencode('.jpg', MyServer.img)
            img_data = base64.b64encode(img_base64).decode('utf-8')
            MyServer.captured_image = img_data

        print("Current temp value (after POST request):", MyServer.temp)
        self._redirect('/')  # Redirect back to the root URL

if __name__ == '__main__':
    host_name = '0.0.0.0'  # Use '0.0.0.0' to allow access from other devices
    host_port = 8080
    httpd = socketserver.TCPServer((host_name, host_port), MyServer)
    print(f"Serving at http://{host_name}:{host_port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
