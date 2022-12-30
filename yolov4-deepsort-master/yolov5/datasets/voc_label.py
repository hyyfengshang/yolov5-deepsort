# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os
from os import getcwd

sets = ['train', 'val', 'test']
classes = ["1"]  # 改成自己的类别

def convert(size, box):
    dw = 1. / (size[0])
    dh = 1. / (size[1])
    x = (box[0] + box[1]) / 2.0 - 1
    y = (box[2] + box[3]) / 2.0 - 1
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return x, y, w, h


def convert_annotation(image_id):
    in_file = open(f'{xml_path}/{image_id}.xml', encoding='UTF-8')
    out_file = open(f'{label_path}/{image_id}.txt', 'w')
    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)
    for obj in root.iter('object'):
        # difficult = obj.find('difficult').text
        # difficult = obj.find('Difficult').text
        cls = obj.find('name').text
        if cls not in classes:
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text),
             float(xmlbox.find('ymax').text))
        b1, b2, b3, b4 = b
        # 标注越界修正
        if b2 > w:
            b2 = w
        if b4 > h:
            b4 = h
        b = (b1, b2, b3, b4)
        bb = convert((w, h), b)
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')


label_path = r'D:\pythonProject\project1\datasets\VOCdatasets\labels'
txt_path = r'D:\pythonProject\project1\datasets\VOCdatasets\ImageSets\Main'
img_path = r'D:\pythonProject\project1\datasets\VOCdatasets\JPEGImages'
xml_path = r'D:\pythonProject\project1\datasets\VOCdatasets\Annotations'
wd = getcwd()
for image_set in sets:
    if not os.path.exists(label_path):
        os.makedirs(label_path)
    image_ids = open(
        f'{txt_path}/{image_set}.txt')
    list_file = open(f'{label_path}/{image_set}.txt' , 'w')
    for image_id in image_ids:
        image_id = image_id.split('\n')[0]
        list_file.write( f'{img_path}/{image_id}.jpg\n')
        convert_annotation(image_id)
    list_file.close()
