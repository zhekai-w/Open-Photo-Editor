import cv2
import numpy as np
# import  enum
class BaseIP:
    def __init__(self,path,output_path,windowname) -> None:
        self.path=path
        self.outputpath=output_path
        self.img=cv2.imread(self.path,cv2.IMREAD_UNCHANGED)
        self.windowname=windowname
        self.pos_x=0
        self.pos_y=0
        self.angle=0

    def ImRead(self,path):
        self.img=cv2.imread(path,cv2.IMREAD_UNCHANGED)


    def ImWrite(self,output_path,img):
        cv2.imwrite(output_path,img)
        print("saved image {}" % output_path)


    def Imshow(self,img,windowname):
        cv2.namedWindow(windowname,cv2.WINDOW_NORMAL)
        cv2.imshow(windowname,img)
        cv2.waitKey(0)

    def resize(self, img, scale):
        print("start resize")
        width = int(img.shape[1] * scale)
        height = int(img.shape[0] * scale)
        print("end resize")
        return cv2.resize(img, (width, height))



    def copyMakeBorder(self, img, top, bottom, left, right, value=[255, 255, 255]):
        return cv2.copyMakeBorder(img, top, bottom, left, right, borderType=cv2.BORDER_CONSTANT, value=value)

    def removeBorder(self, img, top, bottom, left, right):
        height, width = img.shape[:2]
        return img[top:height-bottom, left:width-right]

    def shift_pos(self,img,pos_x,pos_y):
        rows,cols,ch=img.shape
        # if self.pos_x!=pos_x:
        #     M=np.float32([[1,0,pos_x],[0,1,0]])
        # if self.pos_y!=pos_y:
        #     M=np.float32([[1,0,0],[0,1,pos_y]])
        M = np.float32([[1, 0, pos_x - self.pos_x], [0, 1, pos_y - self.pos_y]])
        self.pos_x=pos_x
        self.pos_y=pos_y
        new_cols = cols + abs(pos_x - self.pos_x)
        new_rows = rows + abs(pos_y - self.pos_y)
            # M=np.float32([[1,0,pos_x],[0,1,pos_y]])
        dst=cv2.warpAffine(img,M,(new_cols, new_rows),borderMode=cv2.BORDER_WRAP, borderValue=(255, 255, 255))
        return dst

    def rotate(self,img,angle):
        rows,cols,ch=img.shape
        M=cv2.getRotationMatrix2D((cols/2,rows/2),angle-self.angle,1)
        self.angle=angle
        dst=cv2.warpAffine(img,M,(cols,rows))
        return dst

        # pass

if __name__=="__main__":
    # img1=BaseIP("./a.jpg","./a_changed.png","a")
    img2=BaseIP("./fg_img.png","./b_changed.png","b")
    # img1.Imshow()
    # img2.Imshow()
    # img2.img=img2.copyMakeBorder(img2.img,1000,1000,0,2000)
    # img2.img=img2.removeBorder(img2.img,1000,1000,1000,1000)
    img2.Imshow(img2.shift_pos(img2.img,200,200),"aa")
