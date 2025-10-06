import os
import csv
import pandas as pd

# 
# input_files 源文件
# begin_row   开始行
# max_num     最多拷贝行数量
# output_csv  输出的csv文件完整路径
def copy_part_csv(input_file, begin_row, max_num, output_csv):
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvOut:
        # 创建csv写入器对象
        csvwriter = csv.writer(csvOut)
        # 写header
        csvwriter.writerow(['Audio:FILE', 'Text:LABEL'])
        
        # 以UTF-8编码打开CSV文件
        with open(input_file, mode='r', encoding='utf-8', newline='') as csvfile:
            # 创建csv.reader对象
            reader = csv.reader(csvfile)
            # 读取标题行
            headers = next(reader)
            print(headers)
            
            index = 0   # 当前行号
            total = 0   # 已经写入文件的数量
            for row in reader:
                if index >= begin_row:
                    csvwriter.writerow(row)
                    total = total + 1
                    
                index = index + 1
                
                if max_num >0 and total >= max_num:
                    break


# 获取csv的总行数
def get_csv_row_count(csv_file):
    row_count = 0
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        row_count = sum(1 for row in reader) - 1
    
    return row_count
    


def shuffle_data(csv_file, output_csv):
    # 读取CSV文件，第一行作为表头
    df = pd.read_csv(csv_file, header=0)  # header=0表示第一行是列名
    
    # 随机打乱数据
    df_shuffled = df.sample(frac=1).reset_index(drop=True)
    
    # 保存到新的CSV文件，包含表头
    df_shuffled.to_csv(output_csv, index=False, header=True)
    
    print(f"数据已随机打乱并保存到 {output_csv}")
    print(f"原始数据条数: {len(df)}")
    print(f"打乱后数据条数: {len(df_shuffled)}")   
    

# python copy_part_csv.py 
if __name__ == "__main__":
    # 训练集、验证集、测试集 80% 15% 5%
    
    csv_file = "/data/nn/merged.csv"
    output_csv = "/data/nn/merged_shuffle.csv"
    # 随机打乱数据
    shuffle_data(csv_file, output_csv)
    
    total_num = get_csv_row_count(output_csv)
    print(f"total_num:{total_num}")
    
    begin_row = 0
    rows = int(total_num * 0.8)
    copy_part_csv(output_csv, begin_row, rows, "/data/nn/nn_trainsets.csv")
    
    begin_row = rows
    rows = int(total_num * 0.15)
    copy_part_csv(output_csv, begin_row, rows, "/data/nn/nn_valsets.csv")
    
    begin_row = begin_row + rows
    rows = int(total_num * 0.05)
    copy_part_csv(output_csv, begin_row, rows, "/data/nn/nn_testsets.csv")
    
    
