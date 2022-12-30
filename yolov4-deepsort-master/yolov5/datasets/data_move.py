import os
import shutil


def get_files(data_path, data_file_list=[]):
    data_files = os.listdir(data_path)
    for data_file in data_files:
        data_file_path = os.path.join(data_path, data_file)
        if os.path.isdir(data_file_path):
            get_files(data_file_path, data_file_list)
        else:
            data_file_list.append(data_file_path)
    return data_file_list


def move_files(data_files, img_path, xml_path):
    for data_file_path in data_files:
        data_format = data_file_path.split('.')[-1]
        if data_format == 'xml':
            xml_file_path = data_file_path
            img_file_path = data_file_path.split('.')[0] + '.bmp'
            xml_save_path = os.path.join(xml_path, os.path.basename(xml_file_path))
            img_save_path = os.path.join(img_path, os.path.basename(img_file_path).split('.')[0] + '.jpg')
            shutil.copy(xml_file_path, xml_save_path)
            shutil.copy(img_file_path, img_save_path)


if __name__ == '__main__':
    data_dir = r'D:\pythonProject\project1\H11_1012'
    img_save_path = r'D:\pythonProject\project1\datasets\VOCdatasets\JPEGImages'
    xml_save_path = r'D:\pythonProject\project1\datasets\VOCdatasets\Annotations'
    # data_file_list = []
    data_file_list = get_files(data_dir)
    # print(data_file_list)
    # if not os.path.exists(img_save_path):
    #     os.makedirs(img_save_path)
    # if not os.path.exists(xml_save_path):
    #     os.makedirs(xml_save_path)
    # move_files(data_file_list, img_save_path, xml_save_path)
    print(data_file_list)

