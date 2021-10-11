import cv2
import numpy as np


def exibir_img(text, img):
    cv2.imshow(text, cv2.resize(img, (int(img.shape[1] * 0.5), int(img.shape[0] * 0.5))))


def processar_imagem(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, None, fx=1.2, fy=1.2, interpolation=cv2.INTER_CUBIC)
    img = remover_sombras(img)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.GaussianBlur(img, (5, 5), 0)
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 255, 10)
    # img = cv2.morphologyEx(img, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    img = cv2.GaussianBlur(img, (5, 5), 0)
    return img


def remover_sombras(img):
    rgb_planes = cv2.split(img)
    result_planes = []
    result_norm_planes = []
    for plane in rgb_planes:
        dilated_img = cv2.dilate(plane, np.ones((7, 7), np.uint8))
        bg_img = cv2.medianBlur(dilated_img, 21)
        diff_img = 255 - cv2.absdiff(plane, bg_img)
        norm_img = cv2.normalize(diff_img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
        result_planes.append(diff_img)
        result_norm_planes.append(norm_img)
    result_norm = cv2.merge(result_norm_planes)
    return result_norm


def remover_linhas_horizontais(img):
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (70, 1))
    temp = 255 - cv2.morphologyEx(img, cv2.MORPH_CLOSE, horizontal_kernel)
    return cv2.add(temp, img)
