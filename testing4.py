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

<head>
    
    <link
        href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Oswald:wght@600&family=Teko&display=swap"
        rel="stylesheet">
    <style>
    body {{
  background-image: url("https://raw.githubusercontent.com/4vinn/Akvin/master/static/iitd.jpg");
  background-size: cover;
  background-position: center center;
  background-repeat: no-repeat;
  margin: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  position: relative;
}}
body::before {{
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(204, 204, 204, 0.2);
  z-index: -1;
}}

.bigbox {{
  background-color: rgb(216, 208, 208, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 2rem;
  padding: 2rem;
}}


.box {{
  display: flex;
  flex-direction: row;
  padding: 1rem;
  font-family: "Oswald", sans-serif;
}}

.heading {{
  padding: 0.5rem;
  text-align: center;
  font-family: "Montserrat", sans-serif;
}}

.data {{
  padding-bottom: 2rem;
  width: 100%;
}}

.info-container {{
  font-size: 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;

}}
.butt {{
  width: 8rem;
  height: 3rem;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 4rem;
  border: none;
}}


.a {{
  cursor: pointer;
  background-color: rgba(239, 239, 239, 0.205);
}}
.a:hover {{
  color: white;
  background: rgba(80, 255, 32, 0.847);
}}

.b {{
  cursor: pointer;
  background-color: rgba(239, 239, 239, 0.205);
}}
.b:hover {{
  cursor: pointer;
  color: white;
  background: rgb(255, 23, 23);
}}

.c {{
  cursor: pointer;
  background-color: rgba(239, 239, 239, 0.205);
}}
.c:hover {{
  cursor: pointer;
  color: white;
  background: rgb(10, 10, 10);
}}

.image-container {{
  padding-left: 5rem;
}}

.image-container img {{
  border-radius: 2rem;
}}

button.ON {{
  height: 1.1rem;
  width: 1.1rem;
  background-color: rgb(94, 255, 94);
  border-radius: 0.2rem;
  border: none;
}}

button.OFF {{
  border: none;
  height: 1.1rem;
  width: 1.1rem;
  background-color: rgb(255, 19, 19);
  border-radius: 0.2rem;
}}

    </style>   
    
</head>

<body>
    <div class="bigbox">
    <div class="heading">
        <h1>Welcome to Standalone Automated Dimension Measurement System</h1>
    </div>

    <div class="box">
        <div class="info-container">
            <div class="data">
                 <p>Status : <button class="{self.temp}"></button> {self.temp} </p>
                <p>Measured Breadth : {self.x} cm</p>
                <p>Measured Length : {self.y} cm</p>
            </div>
            <div class="buttons">
                <form action="/do_POST" method="POST">
                    <input class="a butt" type="submit" name="submit" value="Start">
                    <input class="b butt" type="submit" name="submit" value="Stop">
                    <input class="c butt" type="submit" name="submit" value="Next">
                </form>
            </div>
        </div>
        <div class=" image-container">
                    <img src="data:image/jpeg;base64,{self.captured_image}" alt="Captured Image">
            </div>
        </div>

        </div>
        
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
        if post_data == 'Start':
            MyServer.temp = "ON"  # Modify the class variable
            print("Button clicked: ON")
            MyServer.cap = cv2.VideoCapture(0)
            # Capture an image in a separate thread
        elif post_data == 'Stop':
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