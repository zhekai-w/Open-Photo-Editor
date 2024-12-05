import cv2
import numpy as np
import  enum
class ColorType(enum.IntEnum):
    USE_RGB = 1
    USE_RGBA =2
    USE_HSV = 3
    USE_YUV = 4
class resize_flag(enum.IntEnum):
    relative=1
    Absolute=2
class BaseIP:
    def __init__(self):
        self.pos_x=0
        self.pos_y=0
        self.angle=0
    @staticmethod
    def ImRead(path,code=cv2.IMREAD_UNCHANGED):
        #cv2.IMREAD_COLOR,cv2.IMREAD_GRAYSCALE,cv2.IMREAD_UNCHANGED
        return cv2.imread   (path,code)
    
    @staticmethod
    def ImWrite(output_path,img):
        cv2.imwrite(output_path,img)
        print("saved image {}" % output_path)

    @staticmethod     
    def Imshow(img,windowname):
        cv2.namedWindow(windowname,cv2.WINDOW_NORMAL)
        cv2.imshow(windowname,img)
        cv2.waitKey(0)
    @staticmethod    
    def resize(img, dst_img, flag=resize_flag.relative, scale=None):
        print("start resize") 
        if flag==1:
            width = int(dst_img.shape[1])
            height = int(dst_img.shape[0])
            print("end resize")
            return cv2.resize(img, (width, height))
        elif flag==2:
            width = int(dst_img.shape[1]*scale)
            height = int(dst_img.shape[0]*scale)
            print("end resize")
            return cv2.resize(img, (width, height))
        
        
    @staticmethod    
    def copyMakeBorder(img, top, bottom, left, right, value=[255, 255, 255]):
        return cv2.copyMakeBorder(img, top, bottom, left, right, borderType=cv2.BORDER_CONSTANT, value=value)
    @staticmethod
    def removeBorder(img, top, bottom, left, right):
        height, width = img.shape[:2]
        return img[top:height-bottom, left:width-right]
    
    @staticmethod
    def Split(img):  
        if img.shape[2]==3:
            b,g,r = cv2.split(img) 
            return b,g,r
        elif img.shape[2]==4:
            b,g,r,a = cv2.split( img) 
            return b,g,r,a
    @staticmethod  
    def merge(b,g,r,a=None,flag=ColorType.USE_RGB):
        if flag==1:
            return cv2.merge([b,g,r])
        elif flag==2:
            return cv2.merge([b,g,r,a])

    
    @staticmethod
    def shift_pos(img,pos_x,pos_y):
        rows,cols,ch=img.shape
        M = np.float32([[1, 0, pos_x], [0, 1, pos_y]])
        new_cols = cols + abs(pos_x)  
        new_rows = rows + abs(pos_y)  
        dst=cv2.warpAffine(img,M,(new_cols, new_rows),borderMode=cv2.BORDER_WRAP, borderValue=(255, 255, 255))
        return dst
    
    @staticmethod
    def rotate(img,angle):
        rows,cols,ch=img.shape
        M=cv2.getRotationMatrix2D((cols/2,rows/2),angle,1)
        dst=cv2.warpAffine(img,M,(cols,rows))
        return dst
    
    

if __name__=="__main__":            
    # img1=BaseIP("./a.jpg","./a_changed.png","a")
    img2=BaseIP("./fg_img.png","./b_changed.png","b")
    # img1.Imshow()
    # img2.Imshow()
    # img2.img=img2.copyMakeBorder(img2.img,1000,1000,0,2000)
    # img2.img=img2.removeBorder(img2.img,1000,1000,1000,1000)
    img2.Imshow(img2.shift_pos(img2.img,200,200),"aa")
    