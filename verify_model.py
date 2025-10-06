import os
import csv
import argparse
import Levenshtein
from funasr import AutoModel

"""
 验证微调后的模型，与原模型对比

 conda activate asr_new
 python verify_model.py -m /data/model/iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch -f /data/FunASR/examples/industrial_data_pretraining/paraformer/outputs -c /data/nn/nn_testsets.csv
"""


def inference(model, wav_file):
    res = model.generate(input = wav_file)

    text = ""
    for result in res:
        text = text + result["text"]
        
    return text    
    
    
# 获取2个字符串比较的结果，用于计算字正确率
# S: 替换错误字数
# D: 删除错误字数
# I: 插入错误字数
def get_edit(label_txt, asr_txt):
    result_dict={'S':0,'D':0,'I':0,'N':0,'ser':0}
    label_txt=label_txt.replace('NAN','')
    asr_txt=asr_txt.replace('NAN','')
    result=Levenshtein.editops(label_txt,asr_txt)
    for row in result:
        if 'replace' in row:
            result_dict['S']+=1
        if 'delete' in row:
            result_dict['D']+=1
        if 'insert' in row:
            result_dict['I']+=1
    result_dict['N']=len(label_txt)
    return result_dict    


def loop_all_csv(old_model, finetune_model, csv_file):
    # 以UTF-8编码打开CSV文件
    with open(csv_file, mode='r', encoding='utf-8', newline='') as csvfile:
        # 创建csv.reader对象
        reader = csv.reader(csvfile)
        # 读取标题行
        headers = next(reader)
        print(headers)
        
        # 读取每一行
        count = 0       # 微调后的模型，推理不一致的行数
        old_count = 0   # 原模型，推理不一致的行数
        index = 0
        old_accuracy_N = 0
        old_accuracy_error = 0
        new_accuracy_N = 0
        new_accuracy_error = 0
        
        word_count = 0  # 标签文本的字数量
        all_labels = ""
        with open('verify_model.txt', 'w', encoding='utf-8') as file:
            for row in reader:
                index += 1
                
                audio_file = row[0]
                # 文本中间可以有空格，对于英文必须是空格隔开
                text = row[1].replace(" ","")
                all_labels = all_labels + text
                
                word_count = word_count + len(text)
                
                old_text = ""
                # 分别用原模型和微调后的模型进行推理
                if old_model is not None:
                    old_text = inference(old_model, audio_file)
                    accuracy_result = get_edit(text, old_text)
                    old_accuracy_N = old_accuracy_N + accuracy_result['N']
                    old_accuracy_error = old_accuracy_error + (accuracy_result['I'] + accuracy_result['D'] + accuracy_result['S'])
                    
                new_text = ""    
                if finetune_model is not None:    
                    new_text = inference(finetune_model, audio_file)
                    accuracy_result = get_edit(text, new_text)
                    new_accuracy_N = new_accuracy_N + accuracy_result['N']
                    new_accuracy_error = new_accuracy_error + (accuracy_result['I'] + accuracy_result['D'] + accuracy_result['S'])
                
                # 比较微调后的输出是否与真实文本一致
                result = "相同"
                if text != new_text:
                    result = "不一致"
                    count = count + 1
                    
                if text != old_text:
                    old_count = old_count + 1    
                                
                msg = f"行号:{index}\n文本: {text}\n原:{old_text}\n新:{new_text}\n结果:{result}\n==================================================\n\n"
                
                file.write(msg)
                
                print(msg)
                
            msg = f"总行数:{index}\n原模型推理有问题的数量：{old_count}\n微调模型推理有问题的数量：{count}\n"    
            file.write(msg)    
            print(msg)     
            old_acc = round((index - old_count)*100/index, 2)
            new_acc = round((index - count)*100/index, 2)
            msg = f"原模型的句子正确率：{old_acc}%\n微调模型的句子正确率：{new_acc}%\n提升百分比:{round(new_acc - old_acc,2) }%\n"
            file.write(msg)    
            file.write("==================================================\n\n") 
            print(msg)      
            
            # 计算不同汉字的个数
            unique_chars = set(all_labels)
            unique_count = len(unique_chars)
                        
            msg = f"标签总字数：{word_count}\n其中不同汉字个数：{unique_count}\n"
            file.write(msg)   
            print(msg)              
            
            # 字准确率(Word Accuracy)
            # W.Corr = ( N - D - S ) / N 
            # 正确文本字数为 N, 删除错误字数 D,插入错误字数 I, 替换错误字数 S
            old_acc = round((old_accuracy_N - old_accuracy_error) * 100/old_accuracy_N, 2)
            new_acc = round((new_accuracy_N - new_accuracy_error) * 100/new_accuracy_N, 2)
            msg = f"原模型的字正确率：{old_acc}%\n微调模型的字正确率：{new_acc}%\n提升百分比:{new_acc - old_acc }%\n"
            file.write(msg)    
            
            file.write("==================================================\n\n") 
            print(msg)  
            
            unique_chars = "".join(unique_chars)
            msg = f"不同的汉字：=================\n{unique_chars}\n"
            file.write(msg) 
            print(msg)
            
            
            
if __name__ == "__main__":
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='验证微调后的模型', formatter_class=argparse.RawTextHelpFormatter)
    
    # 添加命令行参数
    parser.add_argument(
        '-m', '--model', 
        required=False,
        default='',
        help='原ASR模型路径'
    )
    
    # 微调后模型路径
    parser.add_argument(
        '-f', '--finetune', 
        required=False,
        default='',
        help='微调后的ASR模型路径'
    )
    
    parser.add_argument(
        '-c', '--csv', 
        required=False,
        default='merged.csv',
        help='csv文件路径，例如：/data/nn_testsets.csv'
    )
    
    # 解析命令行参数
    args = parser.parse_args()  
    
    old_model = None
    finetune_model = None

    # 需要configuration.json config.yaml model.pt，也可以将其它轮次的保存模型文件(比如：model.pt.ep20)重命名为model.pt
    if args.model is not None:
        old_model = AutoModel(model=args.model,
                         disable_update=True,
                         disable_pbar=True,
                         disable_log=True,
                         check_latest=False)
                   
    if args.finetune is not None:                   
        finetune_model = AutoModel(model=args.finetune,
                         disable_update=True,
                         disable_pbar=True,
                         disable_log=True,
                         check_latest=False)
                     
    loop_all_csv(old_model, finetune_model, args.csv)