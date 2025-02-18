from model.sbert import SpanBertClassificationModel
from Datareader.data_reader_new import SpanClDataset
from torch.utils.data import DataLoader
import torch.nn as nn
import torch
from torch.optim.lr_scheduler import ReduceLROnPlateau
import torch.nn.functional as F

from transformers import AdamW, WarmupLinearSchedule
from tqdm import tqdm

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def train(model, train_loader, dev_loader):
    model.to(device)
    model.train()
    criterion = nn.CrossEntropyLoss()

    param_optimizer = list(model.named_parameters())
    no_decay = ['bias', 'LayerNorm.bias', 'LayerNorm.weight']
    # 设置模型参数的权重衰减
    optimizer_grouped_parameters = [
        {'params': [p for n, p in param_optimizer if not any(nd in n for nd in no_decay)],
         'weight_decay': 0.01},
        {'params': [p for n, p in param_optimizer if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}
    ]
    # 学习率的设置
    optimizer_params = {'lr': 1e-5, 'eps': 1e-6, 'correct_bias': False}
    # AdamW 这个优化器是主流优化器
    optimizer = AdamW(optimizer_grouped_parameters, **optimizer_params)

    # 学习率调整器，检测准确率的状态，然后衰减学习率
    scheduler = ReduceLROnPlateau(optimizer, mode='max', factor=0.5, min_lr=1e-7, patience=5, verbose=True,
                                  threshold=0.0001, eps=1e-08)

    t_total = len(train_loader)
    total_epochs = 1500
    bestAcc = 0
    correct = 0
    total = 0
    print('Training begin!')
    for epoch in range(total_epochs):
        for step, (indextokens_a, input_mask_a, indextokens_b, input_mask_b, label) in enumerate(train_loader):
            indextokens_a, input_mask_a, indextokens_b, input_mask_b, label = indextokens_a.to(device), input_mask_a.to(
                device), indextokens_b.to(device), input_mask_b.to(device), label.to(device)
            optimizer.zero_grad()
            out_put = model(indextokens_a, input_mask_a, indextokens_b, input_mask_b)
            loss = criterion(out_put, label)
            _, predict = torch.max(out_put.data, 1)
            correct += (predict == label).sum().item()
            total += label.size(0)
            loss.backward()
            optimizer.step()

            if (step + 1) % 2 == 0:
                train_acc = correct / total
                print("Train Epoch[{}/{}],step[{}/{}],tra_acc{:.6f} %,loss:{:.6f}".format(epoch + 1, total_epochs,
                                                                                          step + 1, len(train_loader),
                                                                                          train_acc * 100, loss.item()))

            if (step + 1) % 500 == 0:
                train_acc = correct / total
                acc = dev(model, dev_loader)
                if bestAcc < acc:
                    bestAcc = acc
                    path = 'savedmodel/span_bert_hide_model.pkl'
                    torch.save(model, path)
                print("DEV Epoch[{}/{}],step[{}/{}],tra_acc{:.6f} %,bestAcc{:.6f}%,dev_acc{:.6f} %,loss:{:.6f}".format(
                    epoch + 1, total_epochs, step + 1, len(train_loader), train_acc * 100, bestAcc * 100, acc * 100,
                    loss.item()))
        scheduler.step(bestAcc)


def dev(model, dev_loader):
    model.eval()
    with torch.no_grad():
        correct = 0
        total = 0
        for step, (
                indextokens_a, input_mask_a, indextokens_b, input_mask_b, label) in tqdm(enumerate(
            dev_loader), desc='Dev Itreation:'):
            indextokens_a, input_mask_a, indextokens_b, input_mask_b, label = indextokens_a.to(device), input_mask_a.to(
                device), indextokens_b.to(device), input_mask_b.to(device), label.to(device)
            out_put = model(indextokens_a, input_mask_a, indextokens_b, input_mask_b, mode)
            _, predict = torch.max(out_put.data, 1)
            correct += (predict == label).sum().item()
            total += label.size(0)
        res = correct / total
        return res


def predict(model, test_loader, mode):
    model.to(device)
    model.eval()
    predicts = []
    predict_probs = []
    with torch.no_grad():
        correct = 0
        total = 0
        for step, (
                indextokens_a, input_mask_a, indextokens_b, input_mask_b, label) in enumerate(
            test_loader):
            indextokens_a, input_mask_a, indextokens_b, input_mask_b, label = indextokens_a.to(device), input_mask_a.to(
                device), indextokens_b.to(device), input_mask_b.to(device), label.to(device)
            out_put = model(indextokens_a, input_mask_a, indextokens_b, input_mask_b, mode)
            _, predict = torch.max(out_put.data, 1)

            pre_numpy = predict.cpu().numpy().tolist()
            predicts.extend(pre_numpy)
            probs = F.softmax(out_put).detach().cpu().numpy().tolist()
            predict_probs.extend(probs)

            correct += (predict == label).sum().item()
            total += label.size(0)
        res = correct / total
        print('predict_Accuracy : {} %'.format(100 * res))
        return predicts, predict_probs


if __name__ == '__main__':
    batch_size = 48
    train_data = SpanClDataset('data/LCQMC/train.tsv')
    dev_data = SpanClDataset('data/LCQMC/dev.tsv')
    test_data = SpanClDataset('data/LCQMC/test.tsv')

    train_loader = DataLoader(dataset=train_data, batch_size=batch_size, shuffle=True)
    dev_loader = DataLoader(dataset=dev_data, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(dataset=test_data, batch_size=batch_size, shuffle=False)

    model = SpanBertClassificationModel()
    train(model, train_loader, dev_loader)
    path = 'savedmodel/span_bert_hide_model.pkl'
    model1 = torch.load(path)
    predicts, predict_probs = predict(model1, test_loader)










