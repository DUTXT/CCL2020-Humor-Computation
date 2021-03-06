import torch
import torch.nn as nn
import torch.nn.functional as F
from models_utils.linear_helper import Linear
from models_utils.attention_helper import SelfAttention
from models_utils.rnn_helper import DynamicLSTM, SqueezeEmbedding


class BERT_Att(nn.Module):
    def __init__(self, bert, opt):
        super(BERT_Att, self).__init__()
        self.bert = bert
        self.dropout = nn.Dropout(opt.dropout)
        self.attention = SelfAttention(opt.bert_dim, 5)
        self.squeeze_embedding = SqueezeEmbedding()
        # self.dense = Linear(opt.bert_dim, opt.polarities_dim)
        layers = [Linear(
            opt.bert_dim*2, opt.bert_dim), nn.ReLU(), Linear(opt.bert_dim, opt.polarities_dim)]
        self.dense = nn.Sequential(*layers)

    def forward(self, inputs):
        text_bert_indices, attention_mask = inputs[0], inputs[1]
        text_len = torch.sum(text_bert_indices != 0, dim=-1)
        sentence_output, pooled_output, all_hidden_states = self.bert(text_bert_indices, attention_mask=attention_mask)
        sentence_output = self.squeeze_embedding(sentence_output, text_len)
        sentence_output = self.dropout(sentence_output)
        pooled_output = self.dropout(pooled_output)

        mask = self.squeeze_embedding(attention_mask, text_len)
        att_hidden, attn_weights = self.attention(sentence_output, mask=mask)
        final_hidden = torch.cat((pooled_output, att_hidden), dim=-1)
        logits = self.dense(final_hidden)
        return logits