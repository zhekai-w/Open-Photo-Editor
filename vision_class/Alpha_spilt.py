from BaseIP import BaseIP 
import numpy as np
import cv2



class alpha_split(BaseIP):
    def __init__(self, path, output_path, windowname) -> None:
        super().__init__(path, output_path, windowname)
        self.pos_x=0
        self.pox_y=0
    def check_alpha(self):
        if self.img.shape[2] == 4:
            alpha_channel = self.img[:, :, 3]
            print("Alpha channel min:", np.min(alpha_channel))
            print("Alpha channel max:", np.max(alpha_channel))

            if np.any(alpha_channel < 255):
                print("圖像包含透明區域")
                mask = alpha_channel > 0
                print("Mask sum:", np.sum(mask))

                cut_image = np.zeros_like(self.img)
                cut_image[mask] = self.img[mask]
                cut_image[mask, 3] = 255  # 設置 alpha 通道為 255

                cv2.imshow('Cut Image', cut_image)
                # cv2.imwrite('cut_image.png', cut_image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            else:
                print("圖像不包含透明區域")
        else:
            print("圖像不包含 alpha 通道")
            
    def Split(self,img):
        # cv2.imshow('Original_Image', img) 
  
        # Using cv2.split() to split channels of coloured image  
        try :
            b,g,r,a = cv2.split( img) 
            bgr_img=cv2.merge([b,g,r])
            return bgr_img,cv2.merge([a])
        except:
            b,g,r = cv2.split( img) 
            bgr_img=cv2.merge([b,g,r])
            return bgr_img,0

        # cv2.imshow("Model Blue Image", b) 
        # cv2.imshow("Model Green Image", g) 
        # cv2.imshow("Model Red Image", r) 
        # cv2.imshow("Model alpha Image", a) 
        # cv2.waitKey(0)
        
        
        
        
        
    def blending(self,fg_img):

        front_img,front_alpha = self.Split(fg_img) 
        back_img,back_alpha = self.Split(self.img)  
        
        if front_img.shape != back_img.shape:
            front_img = cv2.resize(front_img, (back_img.shape[1], back_img.shape[0]))
        if front_alpha.shape != back_img.shape[:2]:
            front_alpha = cv2.resize(front_alpha, (back_img.shape[1], back_img.shape[0]))
        # if front_img.shape != back_img.shape:
        #     back_img = cv2.resize(back_img, (front_img.shape[1], front_img.shape[0]))
            
        # if (fg_img.shape[1] > image2.shape[1] or fg_img.shape[0] > image2.shape[0]):
        #     raise ValueError("Resized foreground exceeds background dimensions.")

        print(front_img.dtype)
        print(back_img.dtype)
        print(front_alpha.dtype)
        
        front_img = front_img.astype(np.float32) / 255.0
        back_img = back_img.astype(np.float32) / 255.0
        front_alpha = front_alpha.astype(np.float32) / 255.0
        
        front_alpha = front_alpha[:, :, np.newaxis]
        
        # print("alpha",front_alpha)
        
        final_img= front_img*front_alpha+back_img*(1-front_alpha)
        final_img = np.clip(final_img, 0, 1)  # 确保数值在 [0, 1] 范围内
        final_img = (final_img * 255).astype(np.uint8)  # 转换为 uint8 类型
        # Displaying Merged RGB image 
        # self.Imshow(final_img,"final_img")
  
        # Waits for user to press any key 
        # cv2.waitKey(0)
        return final_img
        
        
        
   
        
        
        
    

if __name__=="__main__":
    img1=alpha_split("./bg_img.jpg","./bg_img_changed.png","bg_img")
    img2=alpha_split("./fg_img.png","./fg_img_changed.png","fg_img")\
        
        
        
    
    img2.img=img2.copyMakeBorder(img2.img, 1000,1000,0,2000)
    img2.blending(img1.img) 
    img2.img=img2.copyMakeBorder(img2.img, 1000,1000,1000,1000)
    img2.blending(img1.img) 
