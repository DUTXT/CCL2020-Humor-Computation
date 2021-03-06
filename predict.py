import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from time import strftime, localtime
import argparse
import random
from sklearn import metrics
import numpy as np
import pandas as pd
from torch.utils.data import DataLoader
from torch.nn.utils import clip_grad_norm_
from transformers import BertModel, AutoModel, XLMRobertaModel, GPT2Model, RobertaModel
from utils.data_utils import Tokenizer4Bert, BertSentenceDataset
from config import opt


class Inferer:
    ''' Model training and evaluation '''
    def __init__(self, opt):
        self.opt = opt
        tokenizer = Tokenizer4Bert(opt.max_length, opt.pretrained_bert_name)
        bert_model = BertModel.from_pretrained(opt.pretrained_bert_name, output_hidden_states=True)
        self.pretrained_bert_state_dict = bert_model.state_dict()
        self.model = opt.model_class(bert_model, opt).to(opt.device)

        print('loading model {0} ...'.format(opt.model_name))
        
        self.model.load_state_dict(torch.load(opt.state_dict_path))
        self.model = self.model.to(opt.device)
        
        torch.autograd.set_grad_enabled(False)

        testset = BertSentenceDataset(opt.dataset_file['test'], tokenizer, target_dim=self.opt.polarities_dim, opt=opt)
        self.test_dataloader = DataLoader(dataset=testset, batch_size=opt.eval_batch_size, shuffle=False)

    def evaluate(self):
        self.model.eval()
        predict = []
        prob = []
        with torch.no_grad():
            for batch, sample_batched in enumerate(self.test_dataloader):
                inputs = [sample_batched[col].to(self.opt.device) for col in self.opt.inputs_cols]
                outputs = self.model(inputs)
                outputs = F.softmax(outputs, dim=-1)
                predict.extend(torch.argmax(outputs, -1).cpu().numpy().tolist())
                outputs_array = outputs.cpu().numpy().tolist()
                for element in outputs_array:
                    # element = np.around(element, 4)
                    # prob.append(list(element))
                    prob.append(element)
        return predict, prob

    def save_prob_csv(self, id, predict, prob, save_path):
        df = pd.DataFrame({'ID':id,'Label':predict, 'Prob_0':[i[0] for i in prob], 'Prob_1':[i[1] for i in prob]})
        df['Prob_0'] = df['Prob_0'].round(4)
        df['Prob_1'] = df['Prob_1'].round(4)
        df.to_csv(save_path, index=False, sep=',')

if __name__=="__main__":
    # torch.set_printoptions(precision=3, threshold=float("inf"), edgeitems=None, linewidth=300, profile=None)

    model_state_dict_paths = {
        
        'en':{
            # '0': './recorder/第六周/en_aug_0721/bert_spc_batchsize=8_logstep=5/bert_spc_en_fold_0_aug_f1_0.6751_f1_0_0.8309_f1_1_0.5193_acc_0.7498_score_1.2691',
            # '1': './recorder/第六周/en_aug_0721/bert_spc_batchsize=8_logstep=5/bert_spc_en_fold_1_aug_f1_0.6571_f1_0_0.7906_f1_1_0.5235_acc_0.7090_score_1.2326',
            # '2': './recorder/第六周/en_aug_0721/bert_spc_batchsize=8_logstep=5/bert_spc_en_fold_2_aug_f1_0.6888_f1_0_0.8415_f1_1_0.5361_acc_0.7637_score_1.2999',
            # '3': './recorder/第六周/en_aug_0721/bert_spc_batchsize=8_logstep=5/bert_spc_en_fold_3_aug_f1_0.6959_f1_0_0.8388_f1_1_0.5530_acc_0.7631_score_1.3161',
            # '4': './recorder/第六周/en_aug_0721/bert_spc_batchsize=8_logstep=5/bert_spc_en_fold_4_aug_f1_0.6833_f1_0_0.8283_f1_1_0.5383_acc_0.7497_score_1.2879',
            # '0': './recorder/第六周/en_dia_aug/bert_spc_logstep=5_Linear/bert_spc_en_fold_0_dia_aug_f1_0.6982_f1_0_0.8512_f1_1_0.5452_acc_0.7758_score_1.3210',
            # '1': './recorder/第六周/en_dia_aug/bert_spc_logstep=5_Linear/bert_spc_en_fold_1_dia_aug_f1_0.6796_f1_0_0.8189_f1_1_0.5403_acc_0.7401_score_1.2804',
            # '2': './recorder/第六周/en_dia_aug/bert_spc_logstep=5_Linear/bert_spc_en_fold_2_dia_aug_f1_0.6600_f1_0_0.8175_f1_1_0.5024_acc_0.7330_score_1.2354',
            # '3': './recorder/第六周/en_dia_aug/bert_spc_logstep=5_Linear/bert_spc_en_fold_3_dia_aug_f1_0.6749_f1_0_0.8447_f1_1_0.5050_acc_0.7636_score_1.2686',
            # '4': './recorder/第六周/en_dia_aug/bert_spc_logstep=5_Linear/bert_spc_en_fold_4_dia_aug_f1_0.7035_f1_0_0.8346_f1_1_0.5724_acc_0.7615_score_1.3339',
            # '0': './recorder/第六周/en_dia_aug/bert_spc_logstep=5_nn.Linear_waccscore/bert_spc_en_fold_0_dia_aug_f1_0.6987_f1_0_0.8565_f1_1_0.5409_acc_0.7813_score_1.3223',
            # '1': './recorder/第六周/en_dia_aug/bert_spc_logstep=5_nn.Linear_waccscore/bert_spc_en_fold_1_dia_aug_f1_0.6780_f1_0_0.8132_f1_1_0.5427_acc_0.7348_score_1.2775',
            # '2': './recorder/第六周/en_dia_aug/bert_spc_logstep=5_nn.Linear_waccscore/bert_spc_en_fold_2_dia_aug_f1_0.6689_f1_0_0.8399_f1_1_0.4980_acc_0.7572_score_1.2552',
            # '3': './recorder/第六周/en_dia_aug/bert_spc_logstep=5_nn.Linear_waccscore/bert_spc_en_fold_3_dia_aug_f1_0.6718_f1_0_0.8428_f1_1_0.5007_acc_0.7609_score_1.2616',
            # '4': './recorder/第六周/en_dia_aug/bert_spc_logstep=5_nn.Linear_waccscore/bert_spc_en_fold_4_dia_aug_f1_0.7157_f1_0_0.8552_f1_1_0.5761_acc_0.7841_score_1.3602',
            # * 第六周
            # '0': './recorder/第六周/en_dia_aug/bert_spc_logstep=5_nn.Linear_wd=0.01_waccscore/bert_spc_en_fold_0_dia_aug_f1_0.6985_f1_0_0.8448_f1_1_0.5521_acc_0.7695_score_1.3216',
            # '1': './recorder/第六周/en_dia_aug/bert_spc_logstep=5_nn.Linear_wd=0.01_waccscore/bert_spc_en_fold_1_dia_aug_f1_0.6814_f1_0_0.8158_f1_1_0.5469_acc_0.7381_score_1.2850',
            # '3': './recorder/第六周/en_dia_aug/bert_spc_logstep=5_nn.Linear_wd=0.01_waccscore/bert_spc_en_fold_3_dia_aug_f1_0.6816_f1_0_0.8536_f1_1_0.5096_acc_0.7745_score_1.2842',
            # '4': './recorder/第六周/en_dia_aug/bert_spc_logstep=5_nn.Linear_wd=0.01_waccscore/bert_spc_en_fold_4_dia_aug_f1_0.7180_f1_0_0.8673_f1_1_0.5687_acc_0.7970_score_1.3657',
            # * 第七周
            # '0': './recorder/第七周/en_dia_aug/bert_spc_0730_bertTD/bert_spc_en_fold_0_dia_aug_f1_0.7141_f1_0_0.8604_f1_1_0.5678_acc_0.7890_score_1.3568',
            # '1': './recorder/第七周/en_dia_aug_0730/bert_spc_bert0728T/bert_spc_en_fold_1_dia_aug_f1_0.6906_f1_0_0.8388_f1_1_0.5424_acc_0.7616_score_1.3040',
            # '2': './recorder/第七周/en_aug/bert_spc_rev_0801_bertT/bert_spc_en_fold_3_aug_f1_0.6992_f1_0_0.8496_f1_1_0.5489_acc_0.7744_score_1.3233',
            # '3': './recorder/第七周/en_dia_aug/bert_spc_0729_bertT/bert_spc_en_fold_4_dia_aug_f1_0.7164_f1_0_0.8563_f1_1_0.5765_acc_0.7854_score_1.3619',
            # '4': './recorder/第七周/en_aug/bert_spc_rev_0801_bertT_adv/bert_spc_en_fold_4_aug_f1_0.7133_f1_0_0.8659_f1_1_0.5608_acc_0.7945_score_1.3553',
            # * 第九周
            # '0': './recorder/第九周/en_dia_aug/bert_spc_lay_0816/bert_spc_lay_en_fold_0_dia_aug_f1_0.7054_f1_0_0.8529_f1_1_0.5579_acc_0.7792_score_1.3371',
            # '1': './recorder/第九周/en_dia_aug/bert_spc_rev_0816/bert_spc_rev_en_fold_1_dia_aug_f1_0.6936_f1_0_0.8379_f1_1_0.5494_acc_0.7616_score_1.3109',
            # '2': './recorder/第九周/en_dia_aug/bert_spc_rev_0816/bert_spc_rev_en_fold_2_dia_aug_f1_0.6654_f1_0_0.8187_f1_1_0.5121_acc_0.7356_score_1.2477',
            # '3': './recorder/第九周/en_dia_aug/bert_spc_rev_0816/bert_spc_rev_en_fold_3_dia_aug_f1_0.6680_f1_0_0.8417_f1_1_0.4943_acc_0.7589_score_1.2531',
            # '4': './recorder/第九周/en_dia_aug/bert_spc_lay_0816/bert_spc_lay_en_fold_4_dia_aug_f1_0.7120_f1_0_0.8440_f1_1_0.5800_acc_0.7725_score_1.3524',
            '0': './recorder/第十周/refine_en/dia_aug/en_fold_0/bert_spc_layerlr_0819/bert_spc_en_fold_0_dia_aug_f1_0.7128_f1_0_0.8680_f1_1_0.5576_acc_0.7967_score_1.3542',
            '1': './recorder/第十周/refine_en/dia_aug/en_fold_1/bert_spc_rev_ce_0819/bert_spc_rev_en_fold_1_dia_aug_f1_0.6958_f1_0_0.8252_f1_1_0.5664_acc_0.7508_score_1.3173',
            '2': './recorder/第十周/refine_en/dia_aug/en_fold_2/bert_spc_rev_laylr_seed_7777_lr_3e-5_T/bert_spc_rev_en_fold_2_dia_aug_f1_0.6770_f1_0_0.8250_f1_1_0.5290_acc_0.7448_wacc_0.7468_score_1.2737',
            '3': './recorder/第十周/refine_en/dia_aug_pseudo/en_fold_3/bert_spc_rev_laylr_seed3000_0819/bert_spc_rev_en_fold_3_dia_aug_pseudo_f1_0.6747_f1_0_0.8480_f1_1_0.5015_acc_0.7670_score_1.2685',
            # '4': './recorder/第十周/refine_en/dia_aug/en_fold_4/bert_spc_lay_laylr_seed3000_0819/bert_spc_lay_en_fold_4_dia_aug_f1_0.7189_f1_0_0.8817_f1_1_0.5561_acc_0.8132_score_1.3693',
            '5': './recorder/第十周/refine_en/dia_aug/en_fold_4/bert_spc_laylr_seed3000_0819/bert_spc_en_fold_4_dia_aug_f1_0.7189_f1_0_0.8543_f1_1_0.5835_acc_0.7841_score_1.3676',
        },

        'cn':{
            # '0': './recorder/第六周/pick/cn/bert_spc_cn_fold_0_uuu_aug_f1_0.6662_f1_0_0.7927_f1_1_0.5397_acc_0.7141_score_1.2538',
            # '1': './recorder/第六周/pick/cn/bert_spc_cn_fold_1_uuu_aug_f1_0.6535_f1_0_0.7897_f1_1_0.5172_acc_0.7070_score_1.2242',
            # '2': './recorder/第六周/pick/cn/bert_spc_cn_fold_2_uuu_aug_f1_0.6541_f1_0_0.7851_f1_1_0.5232_acc_0.7037_score_1.2269',
            #  # '3': './recorder/第五周/pick_0719/cn/after_pseudo/bert_spc_lay_cn_fold_3_f1_0.6481_f1_0_0.7767_f1_1_0.5196_score_1.2147',
            # '4': './recorder/第六周/pick/cn/bert_spc_cn_fold_4_uuu_aug_f1_0.6581_f1_0_0.7787_f1_1_0.5375_acc_0.7006_score_1.2381',
            # * 七周
            '0': './recorder/第七周/pick/cn/bert_spc_rev_cn_fold_0_pseudo_f1_0.6770_f1_0_0.8228_f1_1_0.5312_acc_0.7428_score_1.2740',
            '1': './recorder/第七周/pick/cn/bert_spc_rev_cn_fold_1_pseudo_f1_0.6904_f1_0_0.8095_f1_1_0.5713_acc_0.7362_score_1.3075',
            '2': './recorder/第七周/pick/cn/bert_spc_rev_cn_fold_2_pseudo_f1_0.6723_f1_0_0.8055_f1_1_0.5391_acc_0.7264_score_1.2656',
            '3': './recorder/第七周/pick/cn/bert_spc_rev_cn_fold_3_pseudo_f1_0.6874_f1_0_0.8207_f1_1_0.5542_acc_0.7442_score_1.2984',
            '4': './recorder/第七周/pick/cn/bert_spc_rev_cn_fold_4_pseudo_f1_0.6702_f1_0_0.8100_f1_1_0.5303_acc_0.7295_score_1.2598',
            # * 十周
            # '0': './recorder/第十周/refine_cn/cn_aug/cn_fold_0/bert_spc_cn_fold_0_aug_f1_0.6789_f1_0_0.8222_f1_1_0.5356_acc_0.7429_score_1.2785',
            # '1': './recorder/第十周/refine_cn/cn_aug_pseudo_enhanced/cn_fold_1/bert_spc_rev_cn_fold_1_aug_pseudo_enhanced_0_f1_0.6670_f1_0_0.8042_f1_1_0.5298_acc_0.7236_score_1.2534',
            # '2': './recorder/第十周/refine_cn/cn_aug_pseudo/cn_fold_2/bert_spc_rev_cn_fold_2_aug_pseudo_f1_0.6640_f1_0_0.8030_f1_1_0.5249_acc_0.7215_score_1.2464',
            # '3': './recorder/第十周/refine_cn/cn_aug_pseudo/cn_fold_3/bert_spc_rev_cn_fold_3_aug_pseudo_f1_0.6619_f1_0_0.8134_f1_1_0.5104_acc_0.7298_score_1.2401',
            # '4': './recorder/第十周/refine_cn/cn_aug_pseudo/cn_fold_4/bert_spc_rev_cn_fold_4_aug_pseudo_f1_0.6673_f1_0_0.8030_f1_1_0.5316_acc_0.7227_score_1.2543',
        }
        
    }

    dataset_files = {
        'cn': {
            'test': './data/test_data/cn_test.csv'
        },
        'en': {
            'test': './data/test_data/en_test.csv'
        }
    }
    
    opt.dataset_file = dataset_files[opt.dataset]
    opt.state_dict_path = model_state_dict_paths[opt.dataset][opt.fold_n]

    inf = Inferer(opt)
    predict_label, prob = inf.evaluate()
    print(len(prob))
    # exit()

    id = [i for i in range(len(predict_label))]

    predict_df = pd.DataFrame(list(zip(id, predict_label)))

    if opt.pseudo:
        save_path = "./predict_data/{}_{}_pseudo/{}".format(opt.model_name, opt.date, opt.dataset)
    else:
        save_path = "./predict_data/{}_{}/{}".format(opt.model_name, opt.date, opt.dataset)
    if not os.path.exists(save_path):
        os.makedirs(save_path, mode=0o777)
    
    file_path = "{}/{}-{}-fold-{}.csv".format(save_path, opt.model_name, opt.dataset, opt.fold_n)
    save_prob_path = "{}/{}-{}-prob-{}.csv".format(save_path, opt.model_name, opt.dataset, opt.fold_n)
    # predict_df.to_csv(file_path, index=None, header=['ID', 'Label'])
    inf.save_prob_csv(id, predict_label, prob, save_prob_path)