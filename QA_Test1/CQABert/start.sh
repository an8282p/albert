CURRENT_DIR=`pwd`
export DATA_DIR=$CURRENT_DIR/data

python bert_qa.py \
  --model_type bert \
  --model_name_or_path bert-base-chinese \
  --do_train \
  --do_eval \
  --do_lower_case \
  --train_file $DATA_DIR/train_200.json \
  --predict_file $DATA_DIR/test_200.json \
  --per_gpu_train_batch_size 16 \
  --learning_rate 3e-5 \
  --num_train_epochs 3.0 \
  --max_seq_length 384 \
  --doc_stride 128 \
  --output_dir output \
  --save_steps 1000