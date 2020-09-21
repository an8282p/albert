CURRENT_DIR=`pwd`
export DATA_DIR=$CURRENT_DIR/data
export MODEL_DIR =$CURRENT_DIR/output_albert

 ~/PycharmProjects/Pytorch/venv/Scripts/python run_squad.py \
  --model_type albert \
  --model_name_or_path output_albert \
  --do_eval \
  --do_lower_case \
  --predict_file $DATA_DIR/test_200.json \
  --per_gpu_train_batch_size 2 \
  --per_gpu_eval_batch_size 2 \
  --learning_rate 1e-5 \
  --num_train_epochs 1.0 \
  --max_seq_length 384 \
  --doc_stride 128 \
  --output_dir output_albert \
  --save_steps 10000