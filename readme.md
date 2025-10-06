# 微调ASR

## 一、参考文档：
  https://github.com/modelscope/FunASR/blob/main/examples/industrial_data_pretraining/paraformer/README_zh.md

## 二、模型：
    /data/model/iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch
    
    
    
## 三、下载代码：
  cd /data
  git clone https://github.com/modelscope/FunASR.git   


## 四、准备数据
  训练数据集：train_wav.scp,train_text.txt
  验证数据集：val_wav.scp,val_text.txt
  将这些数据放到data/list目录下面
  
  conda activate asr_new
  cd /data/asr_finetune
  
  #将所有标注的数据合并成一个csv文件
  python merge_csv_args.py -i /data/nn -o merged.csv

  #分别生成 训练集、验证集、测试集的csv文件
  python copy_part_csv.py 

  #将训练集、验证集的csv文件处理成模型训练所需的数据格式，并放到指定目录下
  python data_process.py
  
  #获取训练集、验证集、测试集的统计信息，包括音频总时长
  python data_info.py

  #从测试服务器下载
  curl -O http://slive.peixunban.top/downdir/nn2025_9_26.zip

## 五、训练:
  
  cd /data/FunASR/examples/industrial_data_pretraining/paraformer
  
  #修改finetune.sh文件：
  model_name_or_model_dir="/data/model/iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch"
  
  根据情况修改max_epoch为实际期望的轮次。
  
  #单机多gpu训练
  export CUDA_VISIBLE_DEVICES="0,1,2,3,4,5"

  如果batch_size比较小，比如是1000，训练时间会较长，如果batch_size比较大，比如是10000，训练时间会比较短。
  当batch_size为10000时，GPU约19G。
  
  batch_size不能大于训练数据集的总数量。
  
  #执行命令,开始微调：
  bash finetune.sh
    
  #"log_file: ./outputs/log.txt
  #如果去掉最后面那一行的 &> ${log_file}，可以输出信息到屏幕。
  
  
  微调后生成的模型文件在： /data3/FunASR/examples/industrial_data_pretraining/paraformer/outputs  
​  ls /data3/FunASR/examples/industrial_data_pretraining/paraformer/outputs
​  面存在 config.yaml model.pt model.pt.ep1 model.pt.ep1.2000 等文件  


  差不多要14G显存。
  
  如果有问题，则可以vi outputs/log.txt
  
  
  训练集14326条，验证集7176条，2卡，50个轮次，差不多6个小时微调结束。
  
  假设需要100个小时的数据，那么就是100x3600秒=360000秒，假设每一个音频平均5秒，360000/5 = 72000条数据。
  
## 六、tensorboard可视化
  cd /data/FunASR/examples/industrial_data_pretraining/paraformer/outputs/
  
  #压缩日志文件目录
  tar -czvf tensorboard_logs.tar.gz tensorboard/
  
  #解压到当前目录
  tar -xzf tensorboard_logs.tar.gz
   
  tensorboard --logdir /data/FunASR/examples/industrial_data_pretraining/paraformer/outputs/tensorboard --port 6006
  浏览器中打开：http://localhost:6006/  
  
  conda activate qaanthing
  tensorboard --logdir /home/data/cdy/tensorboard --host 0.0.0.0 --port 30002
  http://ai.mnbaba.com:30002/  
  
## 七、新模型的推理：
  from funasr import AutoModel

  #需要configuration.json config.yaml model.pt，也可以将其它轮次的保存模型文件(比如：model.pt.ep20)重命名为model.pt
  model = AutoModel(model="/data3/FunASR/examples/industrial_data_pretraining/paraformer/outputs/")

  res = model.generate(input=wav_file)
  print(res)
  
## 八、测试集验证
  conda activate asr_new
  cd /data/asr_finetune  
  python verify_model.py -m /data/model/iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch -f /data/FunASR/examples/industrial_data_pretraining/paraformer/outputs -c /data/nn/nn_testsets.csv
  
 