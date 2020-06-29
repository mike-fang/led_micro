import cv2

class ELP_Camera():
    def __init__(self, cv_chan):
        self.cap = cv2.VideoCapture(cv_chan)
        img = self.capture_img()
        self.img_shape = img.shape
    def camera_test(self):
        while True:
            ret, frame = self.cap.read()
            cv2.imshow('', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cam.release()
        cv2.destroyAllWindows()
    def capture_img(self):
        ret, frame = self.cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame
