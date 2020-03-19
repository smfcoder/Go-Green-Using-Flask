from PIL import Image, ImageFilter, ImageEnhance
import cv2
import numpy as np

image = Image.open(jalgaoncenter.jpg)
image.show()
width, height= image.size
a=0
green=0
for x in range(width):
    for y in range(height):
        r,g,b=image.getpixel((x,y))
        if(r>0 and b>0):
            if(r<g and b<g):
                zz=g-r
                xx=g-b
                if(zz > 10 and xx >10):
                    green=green+1
                    image.putpixel((x,y),(255,255,255))
                else:
                    image.putpixel((x, y), (0, 0, 0))
            else:
                image.putpixel((x, y), (0,0,0))
        else:
            image.putpixel((x, y), (0, 0, 0))

        a=a+1
image.show()
image.save("mask.jpg")
print("Total Pixel %d"%a)
print("Total Green Pixel  %d"%green)
print(width)
print(height)

img = Image.open("mask.jpg")
img.filter(ImageFilter.FIND_EDGES).save("edge.jpg")

im = Image.open("edge.jpg")
im.show()

img = cv2.pyrDown(cv2.imread('mask.jpg', cv2.IMREAD_UNCHANGED))

ret, threshed_img = cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY),127, 255, cv2.THRESH_BINARY)

contours, hier = cv2.findContours(threshed_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
coo=0
for c in contours:
    x, y, w, h = cv2.boundingRect(c)
    aa=(w)*(h)
    print(aa)
    if aa > 70:
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        coo=coo+1
    else:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), -1)

   # rect = cv2.minAreaRect(c)
    # box = cv2.boxPoints(rect)
    # box = np.int0(box)
    # cv2.drawContours(img, [box], 0, (0, 0, 255))

    # (x, y), radius = cv2.minEnclosingCircle(c)
    # center = (int(x), int(y))
    # radius = int(radius)
    # img = cv2.circle(img, center, radius, (255, 0, 0), 2)

print("Total Counter of box :-  ")
print(len(contours))

print(" Approx No of tree : ")
print(coo)
cv2.imshow("contours", img)
while True:
    key = cv2.waitKey(1)
    if key == 27:
        break

cv2.destroyAllWindows()
