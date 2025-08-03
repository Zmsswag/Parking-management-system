# core/plate_recognizer.py
import cv2
import easyocr
import re
import numpy as np

class PlateRecognizer:
    """处理来自视频流的车牌识别任务"""
    def __init__(self):
        """初始化车牌识别器"""
        # 修复某些easyocr版本可能出现的警告
        if not hasattr(easyocr.easyocr, 'corrupt_msg'):
            easyocr.easyocr.corrupt_msg = "图像文件损坏，无法打开。"
            
        self.reader = easyocr.Reader(['en'])  # 仅识别英文字符和数字
        self.cap = None
        self.recent_results = []  # 用于存储最近的识别结果，以提高稳定性

    def start_camera(self):
        """启动默认摄像头"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise IOError("无法打开摄像头")
        self.recent_results.clear() # 每次启动时清空历史记录

    def stop_camera(self):
        """释放并关闭摄像头"""
        if self.cap:
            self.cap.release()
            self.cap = None

    def is_valid_plate(self, text: str) -> bool:
        """验证识别出的文本是否符合车牌格式（此处简化为6位字母/数字）"""
        if len(text) != 6:
            return False
        # 正则表达式，匹配6位由A-F和0-9组成的字符串
        pattern = r'^[A-F0-9]{6}$'
        return bool(re.match(pattern, text))

    def get_most_common_result(self) -> str:
        """从最近的识别结果中找出出现次数最多的那个"""
        if not self.recent_results:
            return None
        return max(set(self.recent_results), key=self.recent_results.count)

    def process_frame(self):
        """
        捕获一帧图像，进行处理，并尝试识别车牌。
        返回处理后的图像帧和稳定识别出的车牌号。
        """
        if not self.cap or not self.cap.isOpened():
            return None, None

        ret, frame = self.cap.read()
        if not ret:
            return None, None

        # 将BGR格式的帧转换为RGB，以便在PyQt中正确显示
        display_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 在原始帧上进行OCR识别
        results = self.reader.readtext(frame)

        for (bbox, text, prob) in results:
            cleaned_text = text.replace(' ', '').upper()
            if self.is_valid_plate(cleaned_text) and prob > 0.5:
                # 将有效结果添加到历史记录中
                self.recent_results.append(cleaned_text)
                if len(self.recent_results) > 10:  # 只保留最近10次结果
                    self.recent_results.pop(0)

                most_common = self.get_most_common_result()

                # 如果一个结果是最多见的，并且在近期出现了至少3次，我们认为它是稳定的
                if most_common == cleaned_text and self.recent_results.count(cleaned_text) >= 3:
                    # 在显示的帧上绘制边界框和文本
                    pts = np.array(bbox, np.int32).reshape((-1, 1, 2))
                    cv2.polylines(display_frame, [pts], True, (0, 255, 0), 2)
                    cv2.putText(display_frame, cleaned_text, (int(bbox[0][0]), int(bbox[0][1]) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    return display_frame, cleaned_text

        # 如果没有稳定的结果，只返回处理后的帧
        return display_frame, None