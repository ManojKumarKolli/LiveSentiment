# my_app/model.py
import torch
from torch import nn
from transformers import DistilBertModel

class DistilBERTClass(nn.Module):
    def __init__(self):
        super(DistilBERTClass, self).__init__()
        self.l1 = DistilBertModel.from_pretrained("distilbert-base-uncased", return_dict=False)
        self.lstm = nn.LSTM(input_size=768, hidden_size=256, num_layers=1, batch_first=True, bidirectional=True)
        self.pre_classifier = nn.Linear(512, 768)
        self.dropout = nn.Dropout(0.1)
        self.classifier = nn.Linear(768, 6)

    def forward(self, input_ids, attention_mask):
        output = self.l1(input_ids=input_ids, attention_mask=attention_mask)
        hidden_state = output[0]
        lstm_output, _ = self.lstm(hidden_state)
        lstm_output = lstm_output[:, -1, :]
        pooler = self.pre_classifier(lstm_output)
        pooler = nn.Tanh()(pooler)
        pooler = self.dropout(pooler)
        output = self.classifier(pooler)
        return output
