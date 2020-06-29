import cv2

cap = cv2.VideoCapture(0)
cap.set(3, 640*2)
cap.set(4, 480*2)
for n in range(100):
    print(n, cap.get(n))
cap.set(8, -20)
while True:
    ret, frame = cap.read()
    print(frame)
    cv2.imshow('', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cam.release()
cv2.destroyAllWindows()
assert False
