import os
import csv
import wave
from collections import Counter

"""
 获取数据集的信息

 conda activate asr_new
 python data_info.py
"""


# 获取wav文件的时长,单位毫秒
def get_wav_duration(wav_file):
    try:
        with wave.open(wav_file, 'r') as wav:
            frames = wav.getnframes()
            rate = wav.getframerate()
            return (frames / rate) * 1000  # 直接返回毫秒
    except Exception as e:
        print(f"获取文件时长时出错: {e}")
        return 0


def format_milliseconds_with_hours(ms):
    """
    将毫秒数转换为"时:分:秒"格式的字符串，总是显示小时部分
    
    参数:
        ms: 毫秒数
        
    返回:
        "时:分:秒"格式的字符串
    """
    # 确保输入是整数
    ms = int(ms)
    
    # 转换为秒
    total_seconds = ms // 1000
    
    # 计算小时、分钟和秒
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    # 格式化为字符串
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"



# 统计CSV文件第2列中每个汉字出现的次数
def count_chinese_characters(csv_file_path):
    """
    统计CSV文件第2列中每个汉字出现的次数
    
    Args:
        csv_file_path (str): CSV文件路径
    
    Returns:
        Counter: 汉字出现次数的统计结果
    """
    character_counter = Counter()
    total_duration = 0

    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            
            for row_num, row in enumerate(csv_reader, 1):
                # 跳过第一行的标题
                if row_num == 1:
                    continue
                    
                # 确保行有足够的列
                if len(row) < 2:
                    print(f"警告: 第{row_num}行数据不完整，已跳过")
                    continue

                duration = get_wav_duration(row[0])
                total_duration = total_duration + duration

                # 获取第2列内容（索引为1）
                text = row[1].replace(" ","")
                
                # 统计每个汉字
                for char in text:
                    # 可选：只统计汉字字符（Unicode范围）
                    #if '\u4e00' <= char <= '\u9fff':
                    #    character_counter[char] += 1
                    # 如果不需要过滤，直接使用下面这行：
                    character_counter[char] += 1
    
    except FileNotFoundError:
        print(f"错误: 文件 {csv_file_path} 不存在")
        return None
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return None
    
    return total_duration,character_counter

# 获取csv的总行数
def get_csv_row_count(csv_file):
    row_count = 0
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        row_count = sum(1 for row in reader) - 1
    
    return row_count


def get_data_info(csv_file):
    total_num = get_csv_row_count(csv_file)
    total_duration,result = count_chinese_characters(csv_file)
    
    duration_info = format_milliseconds_with_hours(total_duration)
    
    if result:
        txt_file = os.path.basename(csv_file)
        txt_file = txt_file + ".txt"
        
        # 保存结果到文件
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(f"总的行数:{total_num}\n")
            f.write(f"总时长:{duration_info}\n")
            f.write(f"共统计到 {len(result)} 个不同的汉字\n")
            f.write("\n出现次数最多的20个汉字:\n")
            for char, count in result.most_common(20):
                f.write(f"'{char}': {count}次\n")
            
            f.write("汉字出现次数统计结果:\n")
            f.write("=============================================\n\n")
            f.write("="*30 + "\n")
            for char, count in result.most_common():
                f.write(f"'{char}': {count}次\n")
        
        print(f"\n详细统计结果已保存到 {txt_file}")
        
            
if __name__ == "__main__":
    get_data_info("/data/nn/nn_trainsets.csv")
    get_data_info("/data/nn/nn_valsets.csv")
    get_data_info("/data/nn/nn_testsets.csv")