import os
import csv
import sys
import shutil   # 拷贝文件

# type:    要处理的数据集类型，可以是train,val,test,分别代表训练、验证、测试集
# max_num: 最大数据条数,如果为0则无限制
# csv_file: csv的文件路径名
# src_wav_parent_path wav: 文件所在的目录
# output_path: .scp和text及wav文件输出目录
# dest_wav_parent_path: wav文件最终的输出父目录，比如最终微调的时候放到/home/data/目录下
# copy_wav_file: 拷贝wav文件在输出目录
def process_data(type, max_num, csv_file, src_wav_parent_path, output_path, dest_wav_parent_path='',copy_wav_file= True):
    if type != "train" and type != "val" and type != "test":
        print("type is invalid,train or val or test is valid data")
        return

    # 根据csv文件获取wav文件所在的目录
    data_path = os.path.dirname(csv_file)

    # 如果.scp和text及wav文件输出目录不存在，则创建目录
    if not os.path.exists(output_path):
        os.makedirs(output_path)
                
    #写train_wav.scp
    wav_path = os.path.join(output_path,f"{type}_wav.scp")
    wav_file = open(wav_path, 'w', encoding='utf-8')

    #写train_text.txt
    text_path = os.path.join(output_path,f"{type}_text.txt")
    text_file = open(text_path, 'w', encoding='utf-8')

    # 以UTF-8编码打开CSV文件
    with open(csv_file, mode='r', encoding='utf-8', newline='') as csvfile:
        # 创建csv.reader对象
        reader = csv.reader(csvfile)
        # 读取标题行
        headers = next(reader)
        print(headers)

        # 读取每一行
        index = 0
        for row in reader:
            print(row)
            index += 1

            audio_file = row[0]
            # 文本中间可以有空格，对于英文必须是空格隔开
            #text = row[1].replace(" ","")
            text = row[1]

            file_name_with_extension = os.path.basename(audio_file)
            file_name_without_extension, _ = os.path.splitext(file_name_with_extension)

            directory = os.path.dirname(audio_file)
            """
            wav_output_dir = os.path.join(output_path, directory)
            # 如果目录不存在，则创建目录
            if not os.path.exists(wav_output_dir):
                os.makedirs(wav_output_dir)
            """    

            #将wav文件拷贝到输出目录
            if copy_wav_file:
                src_path = os.path.join(src_wav_parent_path, audio_file)
                dest_path = os.path.join(dest_wav_parent_path,audio_file)
                print(f"src_path:{src_path},dest_path:{dest_path}")
                directory = os.path.dirname(dest_path)
                # 检查目录是否存在
                if not os.path.exists(directory):
                    os.makedirs(directory)
                    
                shutil.copyfile(src_path, dest_path)

            # 将wav的实际保存路径格式化为linux格式，因为最终微调都是在linux系统下
            if audio_file.startswith('/'):
                # 音频文件的路径已经是绝对路径了，则无需处理
                pass
            else:    
                if dest_wav_parent_path.endswith("/"):
                    audio_file = f"{dest_wav_parent_path}{audio_file}"
                else:
                    audio_file = f"{dest_wav_parent_path}/{audio_file}"

            wav_file.write(f"{file_name_without_extension} {audio_file}\n")
            text_file.write(f"{file_name_without_extension} {text}\n")
            if max_num>0 and index >= max_num:
                break

    wav_file.close()
    text_file.close()


# 根据csv文件生成train_wav.scp,train_text.txt和val_wav.scp 和 val_text.txt到指定的目录下面
# .scp 和 .txt是微调脚本需要的数据集格式文件
#                        类型 最大数据量 输入的csv文件 输出目录 微调时wav文件的父目录
# python data_process.py "val" 10000 "./data/speech_asr_aishell_devsets.csv" "./data/list/" '/home/data/'
if __name__ == "__main__":
    process_data("train", 0, "/data/nn/nn_trainsets.csv", "/data/", "/data/FunASR/data/list", '/data/', False)
    process_data("val", 0, "/data/nn/nn_valsets.csv", "/data/", "/data/FunASR/data/list", '/data/', False)
   

