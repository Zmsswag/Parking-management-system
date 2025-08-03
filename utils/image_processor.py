# utils/image_processor.py
import cv2
import os

def process_images_in_folder(input_folder, output_folder):
    """
    批量处理一个文件夹中的所有图像。
    功能：转为灰度图 -> 二值化阈值分割 -> 反相 -> 保存。
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    img_list = os.listdir(input_folder)
    print(f"找到 {len(img_list)} 张图片，开始处理...")
    
    for pic in img_list:
        img_path = os.path.join(input_folder, pic)
        output_path = os.path.join(output_folder, pic)
        
        image = cv2.imread(img_path)
        if image is not None:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(gray, 165, 255, cv2.THRESH_BINARY)
            mask_inv = cv2.bitwise_not(mask)
            cv2.imwrite(output_path, mask_inv)
            print(f"已处理并保存: {pic}")