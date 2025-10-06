import os
import csv
import argparse

# 首先将标注的数据，放到一个目录，比如/data/nn, 该目录下面有A-1251，B-958 等子目录，然后再执行python程序进行csv文件的处理
# 枚举指定目录下面的全部子目录，并将子目录下面的csv文件合并为一个csv文件，为了方便wav文件不移动位置
# conda activate funasr
# python merge_csv_args.py -i /data/nn -o merged.csv


def get_directories(path):
    """安全地获取指定路径下的所有目录名"""
    try:
        # 检查路径是否存在
        if not os.path.exists(path):
            raise FileNotFoundError(f"路径 '{path}' 不存在")
        
        # 检查路径是否是目录
        if not os.path.isdir(path):
            raise NotADirectoryError(f"'{path}' 不是一个目录")
        
        # 获取所有目录
        directories = [d for d in os.listdir(path) 
                      if os.path.isdir(os.path.join(path, d))]
        
        return directories
    
    except PermissionError:
        print(f"没有权限访问路径: {path}")
        return []
    except Exception as e:
        print(f"发生错误: {e}")
        return []


def change_directory(old_name,new_name):
    try:
        # 重命名目录
        os.rename(old_name, new_name)
        # print(f"目录已从 '{old_name}' 重命名为 '{new_name}'")
    except FileNotFoundError:
        # print(f"目录 '{old_name}' 不存在")
        pass
    except FileExistsError:
        print(f"目录 '{new_name}' 已存在")
    except PermissionError:
        print("权限不足，无法重命名目录")


def merge_csv(parent_dir, valid_dirs, output_csv):
    """
    合并多个CSV文件到单个文件
    
    参数:
        parent_dir:  这些子目录所在的父目录          
        valid_dirs (list): 要合并的CSV文件路径
        output_csv (str): 输出的合并后CSV文件路径
    """
    exit = False
    output_fullname = os.path.join(parent_dir, output_csv)
    with open(output_fullname, 'w', newline='', encoding='utf-8') as csvOut:
        csvwriter = csv.writer(csvOut)
        # 写入标题行
        csvwriter.writerow(['Audio:FILE', 'Text:LABEL'])
        
        for child_dir in valid_dirs:
            if exit:
                break

            print(f"正在处理 {child_dir} 子目录下面的文件...")
            input_dir = os.path.join(parent_dir, child_dir)

            # 将 speech_asr_aishell_devsets 目录修改为 audio目录
            old_dir = os.path.join(input_dir, "speech_asr_aishell_devsets")
            audio_dir = os.path.join(input_dir, "audio")
            change_directory(old_dir, audio_dir)

            input_file = os.path.join(input_dir, "speech_asr_aishell_devsets.csv")
            with open(input_file, mode='r', encoding='utf-8', newline='') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader)  # 跳过标题行
                
                # 验证文件格式
                if headers != ['Audio:FILE', 'Text:LABEL']:
                    print(f"警告: 文件 {input_file} 的标题行不匹配，跳过标题行继续处理")
                
                # 写入数据行
                for row in reader:
                    try:
                        new_path = os.path.join(parent_dir, child_dir)
                        # 如果路径中存在 \，则替换为linux路径分割符
                        temp_dir = row[0].replace("\\", "/")
                        new_path = os.path.join(new_path, temp_dir)
                        # 将路径中的 "speech_asr_aishell_devsets" 替换为 "audio"
                        new_path = new_path.replace("speech_asr_aishell_devsets", "audio")
                        
                        if os.path.exists(new_path):
                            csvwriter.writerow([new_path, row[1]])
                        else:
                             print(f"文件不存在:{new_path}")
                             
                        # print(f"child_dir:{child_dir},row:{row}")
                    except Exception as e:
                        print(f"row: {row}")
                        print(f"发生错误: {e}")
                        exit = True

            # print(f"已处理文件: {input_file}")
    
    print(f"\n合并完成! 共合并 {len(valid_dirs)} 个文件")
    print(f"输出文件: {output_fullname}")

if __name__ == "__main__":
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='合并多个CSV文件', formatter_class=argparse.RawTextHelpFormatter)
    
    # 添加命令行参数
    parser.add_argument(
        '-i', '--input', 
        required=False,
        default='../nn2025_9_25',
        help='输入要合并csv文件的父目录'
    )
    
    parser.add_argument(
        '-o', '--output', 
        required=False,
        default='merged.csv',
        help='输出文件名，例如：merged.csv'
    )
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 枚举该目录下的全部子目录,返回子目录（非完整路径）
    valid_dirs = get_directories(args.input)
    print(valid_dirs)
    
    # 检查是否有有效文件
    if not valid_dirs:
        print("错误: 没有有效的CSV文件可供处理")
        exit(1)
    
    # 执行合并操作
    merge_csv(args.input, valid_dirs, args.output)