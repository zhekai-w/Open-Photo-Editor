
from BaseIP import BaseIP,ColorType,resize_flag
import matplotlib.pyplot as plt
import numpy as np
import cv2

class HistIP(BaseIP):
    def __init__(self) -> None:
        super().__init__()
        pass

    def CalcGrayHist(self,src_gray,mask=None):
        hist=cv2.calcHist([src_gray], [0], mask, [256], [0, 256])
        return hist


    def CalcColorHist(self,SrcColor,mask=None):
        histb=cv2.calcHist([SrcColor], [0], mask, [256], [0, 256])
        histg=cv2.calcHist([SrcColor], [1], mask, [256], [0, 256])
        histr=cv2.calcHist([SrcColor], [2], mask, [256], [0, 256])
        return histb,histg,histr

    def ShowGrayHist(self,winname,value=None):
        plt.plot(value, color='k')
        plt.title(winname)
        plt.xlabel('Pixel Value')
        plt.ylabel('Frequency')
        plt.show()

    def ShowColorHist(self, winname, b_value=None,g_value=None,r_value=None):
        plt.plot(b_value, color='b')
        plt.plot(g_value, color='g')
        plt.plot(r_value, color='r')
        plt.title(winname)
        plt.xlabel('Pixel Value')
        plt.ylabel('Frequency')
        plt.show()

    def MonoEqualize_gray(self,SrcGray):
        return cv2.equalizeHist(SrcGray)

    def MonoEqualize_rgb(self, src):
        b,g,r=self.Split(src)
        b_c=cv2.equalizeHist(b)
        g_c=cv2.equalizeHist(g)
        r_c=cv2.equalizeHist(r)
        return self.merge(b_c,g_c,r_c)

    def calc_cdf(self,hist_1,hist_2,hist_3,CType):
        if CType==1:
            sum_hist_b = cv2.calcHist([hist_1], [0], None, [256], [0, 256]).cumsum()
            sum_hist_g = cv2.calcHist([hist_2], [0], None, [256], [0, 256]).cumsum()
            sum_hist_r = cv2.calcHist([hist_3], [0], None, [256], [0, 256]).cumsum()

            normalized_hist_b = sum_hist_b / sum_hist_b[-1]
            normalized_hist_g = sum_hist_g / sum_hist_g[-1]
            normalized_hist_r = sum_hist_r / sum_hist_r[-1]
            return normalized_hist_b,normalized_hist_g,normalized_hist_r
        elif CType==3:
            sum_hist_v = cv2.calcHist([hist_3], [0], None, [256], [0, 256]).cumsum()
            normalized_hist_v = sum_hist_v / sum_hist_v[-1]
            return normalized_hist_v
        elif CType==4:
            sum_hist_y = cv2.calcHist([hist_1], [0], None, [256], [0, 256]).cumsum()
            normalized_hist_y = sum_hist_y / sum_hist_y[-1]
            return normalized_hist_y

    def interpolate_histogram(self,src_hist, ref_hist, intensity):
            # Create intermediate target histogram by interpolating between source and reference histograms
            target_hist = src_hist + intensity * (ref_hist - src_hist)
            return target_hist


    def HistMatching(self, SrcImg, RefImg, CType=ColorType.USE_RGB, intensity=1.0):
        # Convert copies to avoid modifying original images
        src_converted = SrcImg.copy()
        ref_converted = RefImg.copy()


        if CType == ColorType.USE_RGB:
            # Calculate histograms for each channel
            src_b, src_g, src_r = cv2.split(src_converted)
            ref_b, ref_g, ref_r = cv2.split(ref_converted)

            # Calculate cumulative histograms for each channel
            src_hist_b,src_hist_g,src_hist_r=self.calc_cdf(src_b,src_g,src_r,CType)
            ref_hist_b,ref_hist_g,ref_hist_r=self.calc_cdf(ref_b,ref_g,ref_r,CType)

            # Interpolate target histograms
            target_hist_b = self.interpolate_histogram(src_hist_b, ref_hist_b, intensity)
            target_hist_g = self.interpolate_histogram(src_hist_g, ref_hist_g, intensity)
            target_hist_r = self.interpolate_histogram(src_hist_r, ref_hist_r, intensity)

            # Create lookup tables
            lut_b = np.interp(src_hist_b, target_hist_b, np.arange(256))
            lut_g = np.interp(src_hist_g, target_hist_g, np.arange(256))
            lut_r = np.interp(src_hist_r, target_hist_r, np.arange(256))

            # Apply lookup tables
            b = cv2.LUT(src_b, lut_b.astype(np.uint8))
            g = cv2.LUT(src_g, lut_g.astype(np.uint8))
            r = cv2.LUT(src_r, lut_r.astype(np.uint8))

            return cv2.merge([b, g, r])

        elif CType == ColorType.USE_HSV:
            src_hsv = cv2.cvtColor(src_converted, cv2.COLOR_BGR2HSV)
            ref_hsv = cv2.cvtColor(ref_converted, cv2.COLOR_BGR2HSV)

            # Only match V channel, preserve H and S
            h, s, v = cv2.split(src_hsv)
            _, _, ref_v = cv2.split(ref_hsv)

            # Calculate and interpolate V channel histogram
            src_hist_v=self.calc_cdf(h,s,v,CType)
            ref_hist_v=self.calc_cdf(_,_,ref_v,CType)


            target_hist_v = self.interpolate_histogram(src_hist_v, ref_hist_v, intensity)
            lut_v = np.interp(src_hist_v, target_hist_v, np.arange(256))

            v_matched = cv2.LUT(v, lut_v.astype(np.uint8))
            hsv_matched = cv2.merge([h, s, v_matched])

            return cv2.cvtColor(hsv_matched, cv2.COLOR_HSV2BGR)

        elif CType == ColorType.USE_YUV:
            src_yuv = cv2.cvtColor(src_converted, cv2.COLOR_BGR2YUV)
            ref_yuv = cv2.cvtColor(ref_converted, cv2.COLOR_BGR2YUV)

            # Only match Y channel, preserve U and V
            y, u, v = cv2.split(src_yuv)
            ref_y, _, _ = cv2.split(ref_yuv)

            # Calculate and interpolate Y channel histogram
            src_hist_y=self.calc_cdf(y,u,v,CType)
            ref_hist_y=self.calc_cdf(ref_y,_,_,CType)

            target_hist_y = self.interpolate_histogram(src_hist_y, ref_hist_y, intensity)
            lut_y = np.interp(src_hist_y, target_hist_y, np.arange(256))

            y_matched = cv2.LUT(y, lut_y.astype(np.uint8))
            yuv_matched = cv2.merge([y_matched, u, v])

            return cv2.cvtColor(yuv_matched, cv2.COLOR_YUV2BGR)


if __name__=="__main__":
    a=HistIP()
    # img=a.ImRead("test.png")
    # print(img.shape)
    # v=a.CalcGrayHist(img)
    # v_c=cv2.normalize(v,None,0,1,cv2.NORM_MINMAX)
    # a.ShowGrayHist("aa",v_c)


    #等化 gray
    # img=a.ImRead("test.png")
    # a.Imshow(img,"ssd")
    # img1= a.MonoEqualize(img)
    # a.Imshow(img1,"sd")
    # v1=a.CalcGrayHist(img)
    # v2=a.CalcGrayHist(img1)
    # a.ShowGrayHist("aa1",v1)
    # a.ShowGrayHist("aa2",v2)
    #等化RGB
    # img=a.ImRead("v1.jpeg")
    # a.Imshow(img,"aa")
    # img1=a.MonoEqualize_rgb(img)
    # a.Imshow(img1,"ss")
    # b1,g1,r1=a.CalcColorHist(img)
    # a.ShowColorHist("aa",b1,g1,r1)
    # b2,g2,r2=a.CalcColorHist(img1)
    # a.ShowColorHist("ss",b2,g2,r2)

    # 匹配RGB
    img=a.ImRead("v1.jpeg")
    img1=a.ImRead("v2.jpg")
    a.Imshow(img,"11")
    # b_value,g_value,r_value=a.CalcColorHist(img)
    # a.ShowColorHist("11",b_value,g_value,r_value)

    a.Imshow(img1,"22")
    # b_value,g_value,r_value=a.CalcColorHist(img1)
    # a.ShowColorHist("22",b_value,g_value,r_value)

    # final_img=match_histograms(img1,img,multichannel=True)
    final_img=a.HistMatching(img,img1,CType=ColorType.USE_RGB, intensity=0.5)
    final_img1=a.HistMatching(img,img1,CType=ColorType.USE_RGB, intensity=1.0)
    # print(final_img.shape[0])
    # print(final_img.shape[1])
    # print(final_img.shape[2])
    a.Imshow(final_img,"33")
    a.Imshow(final_img1,"44")
    # b_value,g_value,r_value=a.CalcColorHist(final_img)
    # a.ShowColorHist("33",b_value,g_value,r_value)


    # img=a.ImRead("bg_img.jpg")
    # mask = np.zeros(img.shape[:2], np.uint8)
    # mask[300:780, 300:1000] = 255
    # # if len(mask.shape) == 3:  # 如果掩膜是三通道（比如 RGB）
    # #         mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    # b_value,g_value,r_value=a.CalcColorHist(img,mask)
    # a.ShowColorHist("aa",b_value,g_value,r_value)
