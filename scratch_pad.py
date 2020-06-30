import cv2

cap = cv2.VideoCapture(0)
print(cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1))
print(cap.set(cv2.CAP_PROP_EXPOSURE, 2000))
print(cap.get(cv2.CAP_PROP_EXPOSURE))
while True:
	ret, frame = cap.read()
	cv2.imshow('', frame)
	print(cap.get(cv2.CAP_PROP_EXPOSURE))
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
cam.release()
cv2.destroyAllWindows()
assert False
