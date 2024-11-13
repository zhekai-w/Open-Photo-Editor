from PyQt5 import QtWidgets,QtGui
from main_ui import Ui_MainWindow  # Import your UI class
import sys
from Alpha_spilt import alpha_split
import cv2

class Main(QtWidgets.QMainWindow,Ui_MainWindow):
    def __init__(self):
        super().__init__()
        
        self.setupUi(self)  # Set up the UI
        self.select_back_button.clicked.connect(self.open_back_file)
        self.select_front_button.clicked.connect(self.open_front_file)
        self.blend_Button.clicked.connect(self.blending)
        
        self.size_edit.textChanged.connect(self.size_edit_change)
        self.x_edit.textChanged.connect(self.x_edit_change)
        self.y_edit.textChanged.connect(self.y_edit_change)
        self.rotate_edit.textChanged.connect(self.rotate_edit_change)
        # self.timer.timeout.connect(self.update_image)

        
        
        self.scene_front = QtWidgets.QGraphicsScene(self)  # 確保正確初始化
        self.front_img_show.setScene(self.scene_front)
        self.scene_back = QtWidgets.QGraphicsScene(self)  # 確保正確初始化
        self.back_im_show.setScene(self.scene_back)
        self.scene_out = QtWidgets.QGraphicsScene(self)  # 確保正確初始化
        self.out_im_show.setScene(self.scene_out)
        
        
        
        self.size_slide.valueChanged.connect(self.size_change)
        self.size_slide.sliderReleased.connect(self.size_changed)
        
        self.x_slide.valueChanged.connect(self.x_change)
        self.x_slide.sliderReleased.connect(self.x_changed)
        
        self.y_slide.valueChanged.connect(self.y_change)
        self.y_slide.sliderReleased.connect(self.y_changed)
        
        self.rotate_slide.valueChanged.connect(self.rotate_change)
        self.rotate_slide.sliderReleased.connect(self.rotate_changed)
        
        self.scale=int(self.size_edit.text())
        self.position_x=self.x_slide.value()
        self.position_y=self.y_slide.value()
        
        
    def size_edit_change(self):
        scale=int(self.size_edit.text())
        self.size_slide.setValue(int(self.size_edit.text()))
        if scale>=0:
            self.load_image(self.bg_img.blending(self.fg_img.copyMakeBorder(self.fg_img.img,200*scale,200*scale,200*scale,200*scale)),self.scene_out,self.out_im_show)
        else :
            scale=scale*(-1)
            print(scale)
            self.load_image(self.bg_img.blending(self.fg_img.removeBorder(self.fg_img.img,20*scale,20*scale,20*scale,20*scale)),self.scene_out,self.out_im_show)
    
    def x_edit_change(self):
        self.position_x=int(self.x_edit.text())
        self.x_slide.setValue(int(self.x_edit.text()))
        print("x_change")
        self.changed_img=self.fg_img.shift_pos(self.changed_img,20*self.position_x,20*self.position_y)
        self.load_image(self.bg_img.blending(self.changed_img),self.scene_out,self.out_im_show)

        print("x_changed=",self.position_x)
        
    def y_edit_change(self):
        self.position_y=int(self.y_edit.text())
        self.y_slide.setValue(int(self.y_edit.text()))
        print("y_change")
        self.changed_img=self.fg_img.shift_pos(self.changed_img,20*self.position_x,20*self.position_y)
        self.load_image(self.bg_img.blending(self.changed_img),self.scene_out,self.out_im_show)
        print("x_changed=",self.position_y)
        
        
        
    def rotate_edit_change(self):
        self.rotate_value=int(self.rotate_edit.text())
        self.rotate_slide.setValue(int(self.rotate_edit.text()))
        print("rotate_change")
        self.changed_img=self.fg_img.rotate(self.changed_img,self.rotate_value)
        self.load_image(self.bg_img.blending(self.changed_img),self.scene_out,self.out_im_show)
        print("rotate_changed=",self.rotate_value)
    
    
    
    
    
    def size_change(self):
        self.scale=self.size_slide.value()
        self.size_edit.setText(str(self.scale))
        
    def size_changed(self):
        self.scale=self.size_slide.value()
        print("size_change")
        if self.scale>=0:
            self.changed_img=self.fg_img.copyMakeBorder(self.fg_img.img,200*self.scale,200*self.scale,200*self.scale,200*self.scale)
            self.load_image(self.bg_img.blending(self.changed_img),self.scene_out,self.out_im_show)
        else :
            self.scale=self.scale*(-1)
            print(self.scale)
            self.changed_img=self.fg_img.removeBorder(self.fg_img.img,20*self.scale,20*self.scale,20*self.scale,20*self.scale)
            self.load_image(self.bg_img.blending(),self.scene_out,self.out_im_show)
        print("size_changed")
            
        
        
        
    def x_change(self):
        self.x_edit.setText(str(self.x_slide.value()))
        
    def x_changed(self):
        self.position_x=self.x_slide.value()
        print("x_change")
        self.changed_img=self.fg_img.shift_pos(self.changed_img,20*self.position_x,20*self.position_y)
        self.load_image(self.bg_img.blending(self.changed_img),self.scene_out,self.out_im_show)

        print("x_changed=",self.position_x)
        
        
    def y_change(self):
        self.y_edit.setText(str(self.y_slide.value()))
        
    def y_changed(self):
        self.position_y=self.y_slide.value()
        print("y_change")
        self.changed_img=self.fg_img.shift_pos(self.changed_img,20*self.position_x,20*self.position_y)
        self.load_image(self.bg_img.blending(self.changed_img),self.scene_out,self.out_im_show)
        print("x_changed=",self.position_y)
    
    
    def rotate_change(self):
        self.rotate_edit.setText(str(self.rotate_slide.value()))
        
    def rotate_changed(self):
        self.rotate_value=self.rotate_slide.value()
        print("rotate_change")
        self.changed_img=self.fg_img.rotate(self.changed_img,self.rotate_value)
        self.load_image(self.bg_img.blending(self.changed_img),self.scene_out,self.out_im_show)
        print("rotate_changed=",self.rotate_value)
        
        
    def open_front_file(self):
        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "選擇檔案", "", "所有檔案 (*);;文本檔 (*.txt)", options=options)
        self.fg_img=alpha_split(file_name,"./111.png","front")
        self.load_image(self.fg_img.img,self.scene_front,self.front_img_show)
        # self.fg_img.Imshow(self.fg_img.img,"aa")
    def open_back_file(self):
        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "選擇檔案", "", "所有檔案 (*);;文本檔 (*.txt)", options=options)
        self.bg_img=alpha_split(file_name,"./222.png","back")
        # self.bg_img.Imshow(self.bg_img.img,"sss")
        self.load_image(self.bg_img.img,self.scene_back,self.back_im_show)
        
        
    
        
        
        
    def load_image(self,img,scene,GraphicsView):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        height, width, channel = img.shape
        bytes_per_line = channel * width
        q_image = QtGui.QImage(img.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
        # 將 QImage 添加到場景中
        pixmap = QtGui.QPixmap.fromImage(q_image)
        scene.addPixmap(pixmap)
        self.fit_image_to_view(pixmap,GraphicsView)

    def fit_image_to_view(self, pixmap,GraphicsView):
        # 獲取 QGraphicsView 的大小
        view_size = self.front_img_show.size()
        pixmap_size = pixmap.size()
        # 計算縮放比例
        scale_x = view_size.width() / pixmap_size.width()
        scale_y = view_size.height() / pixmap_size.height()
        scale = min(scale_x, scale_y)  # 使用最小縮放比例以保持比例
        # 應用縮放
        GraphicsView.setTransform(QtGui.QTransform().scale(scale, scale))
        
        
        
        
    def blending(self):
        self.changed_img=self.fg_img.copyMakeBorder(self.fg_img.img,0,0,0,0)
        self.changed_img=self.bg_img.blending(self.changed_img)
        
        self.load_image(self.changed_img,self.scene_out,self.out_im_show)
        self.size_changed()
        pass
        
        
        
        
        
        
        
        
if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())