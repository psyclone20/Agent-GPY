import cv2
import numpy as np
import PIL
from PIL import Image
from PIL import ImageGrab
import time

person_cascade = cv2.CascadeClassifier("person-cascade.xml")


def recognize(img, current_team):
	person = person_cascade.detectMultiScale3(
		img,
		minNeighbors = 750,
		minSize = (64, 64),
		outputRejectLevels = True
	)
	rects = person[0]
	neighbours = person[1]
	weights = person[2]
	
	myVar = -1
	for (x, y, w, h) in rects:
		myVar += 1
		if weights[myVar] > 3.3:
			if not(x < 600 and (x+w) > 600 and y < 480 and (y+h) > 480): # avoid own weapon
				image = PIL.Image.fromarray(img).crop(box=(int(x+0.4*w), int(y+0.2*h), int(x+0.6*w), int(y+0.4*h)))
				result = image.convert('P', palette=Image.ADAPTIVE, colors=1)
				result.putalpha(0)
				colors_upper = result.getcolors()
				
				gray = 0.2126*colors_upper[0][1][0] + 0.7152*colors_upper[0][1][1] + 0.0722*colors_upper[0][1][2]
					
				new_y = y - 15 if y - 15 > 15 else y + 15
				cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)
				if gray > 70:
					cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
					cv2.putText(img, "T: " + str(gray), (x, new_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
					# coords.append(x)
					# coords.append(y)

					# cv2.imshow("Output", img)
					# if cv2.waitKey(1) & 0xFF == ord('q'):
					# 	cv2.destroyAllWindows()

					if current_team == "CT":
						return (x, y, x+w, y+h)
					else:
						return (-1, -1, -1, -1)
				else:
					cv2.rectangle(img, (x, y), (x+w, y+h), (255, 255, 0), 2)
					cv2.putText(img, "CT: " + str(gray), (x, new_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

					# cv2.imshow("Output", img)
					# if cv2.waitKey(1) & 0xFF == ord('q'):
					# 	cv2.destroyAllWindows()

					if current_team == "T":
						return (x, y, x+w, y+h)
					else:
						return (-1, -1, -1, -1)

	# cv2.imshow("Output", img)
	# if cv2.waitKey(1) & 0xFF == ord('q'):
	# 	cv2.destroyAllWindows()
	return (-1, -1, -1, -1)
		
	# cv2.imshow("Output", cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
	# if cv2.waitKey(1) & 0xFF == ord('q'):
	# 	cv2.destroyAllWindows()
	# 	break