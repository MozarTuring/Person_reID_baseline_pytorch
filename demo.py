import argparse
import scipy.io
import torch
import numpy as np
import os
from torchvision import datasets
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
#######################################################################
# Evaluate
parser = argparse.ArgumentParser(description='Demo')
parser.add_argument('--query_index', default=777, type=int, help='test_image_index')
parser.add_argument('--test_dir',default='../Market/pytorch',type=str, help='./test_data')
opts = parser.parse_args()

data_dir = opts.test_dir
# folder_ls = ['gallery','query']
folder_ls = ["body", "body_query"]
image_datasets = {x: datasets.ImageFolder( os.path.join(data_dir,x) ) for x in folder_ls}

#####################################################################
#Show result


######################################################################
result = scipy.io.loadmat(os.path.join(data_dir,'pytorch_result.mat'))
query_feature = torch.FloatTensor(result['query_f'])
# query_cam = result['query_cam'][0]
# query_label = result['query_label'][0]
gallery_feature = torch.FloatTensor(result['gallery_f'])
# gallery_cam = result['gallery_cam'][0]
# gallery_label = result['gallery_label'][0]

# multi = os.path.isfile('multi_query.mat')

# if multi:
#     m_result = scipy.io.loadmat('multi_query.mat')
#     mquery_feature = torch.FloatTensor(m_result['mquery_f'])
#     mquery_cam = m_result['mquery_cam'][0]
#     mquery_label = m_result['mquery_label'][0]
#     mquery_feature = mquery_feature.cuda()

query_feature = query_feature.cuda()
gallery_feature = gallery_feature.cuda()

#######################################################################
# sort the images
def sort_img(qf, gf):
    query = qf.view(-1,1)
    # print(query.shape)
    score = torch.mm(gf,query)
    score = score.squeeze(1).cpu()
    score = score.numpy()
    # predict index
    index = np.argsort(score)  #from small to large
    index = index[::-1]
    # # index = index[0:2000]
    # # good index
    # query_index = np.argwhere(gl==ql)
    # #same camera
    # camera_index = np.argwhere(gc==qc)

    # #good_index = np.setdiff1d(query_index, camera_index, assume_unique=True)
    # junk_index1 = np.argwhere(gl==-1)
    # junk_index2 = np.intersect1d(query_index, camera_index)
    # junk_index = np.append(junk_index2, junk_index1) 

    # mask = np.in1d(index, junk_index, invert=True)
    # index = index[mask]
    return index

i = opts.query_index
index = sort_img(query_feature[i],gallery_feature)

########################################################################
# Visualize the rank result

query_path, _ = image_datasets[folder_ls[1]].imgs[i]
# query_label = query_label[i]
print(query_path)
print('Top 10 images are as follow:')
try: # Visualize Ranking Result 
    # Graphical User Interface is needed
    fig = plt.figure(figsize=(16,4))
    ax = plt.subplot(1,11,1)
    ax.axis('off')
    imshow(query_path,'query')
    for i in range(10):
        ax = plt.subplot(1,11,i+2)
        ax.axis('off')
        img_path, _ = image_datasets[folder_ls[0]].imgs[index[i]]
        # label = gallery_label[index[i]]
        imshow(img_path)
        # if label == query_label:
        #     ax.set_title('%d'%(i+1), color='green')
        # else:
        #     ax.set_title('%d'%(i+1), color='red')
        # print(img_path)
except RuntimeError:
    for i in range(10):
        img_path = image_datasets.imgs[index[i]]
        print(img_path[0])
    print('If you want to see the visualization of the ranking result, graphical user interface is needed.')

fig.savefig("show.png")


# python demo.py --query_index 111 --test_dir ../camera1_bak
