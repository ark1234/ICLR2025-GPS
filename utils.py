#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import torch
import torch.nn as nn
import sys

from scipy.stats import norm
import numpy as np

import math
#####################

class PointLoss_like_GPS(nn.Module):
    def __init__(self):
        super(PointLoss_like_GPS,self).__init__()
        
    def forward(self,array1,array2):
        return chamfer_distance_like_GPS(array1,array2)





def chamfer_distance_like_GPS(array1, array2):
    batch_size, num_point, num_features = array1.shape
    dist = 0
    for i in range(batch_size):
        av_dist1 = array2samples_distancelike_GPS(array1[i], array2[i])
        av_dist2 = array2samples_distancelike_GPS(array2[i], array1[i])
        dist = dist + (0.5*av_dist1+0.5*av_dist2)/batch_size
    return dist*100






def array2samples_distancelike_GPS(array1, array2):
    """
    arguments: 
        array1: the array, size: (num_point, num_feature)
        array2: the samples, size: (num_point, num_feature)
    returns:
        distances: each entry is the distance from a sample to array1 
    """
    num_point1, num_features1 = array1.shape
    num_point2, num_features2 = array2.shape
    expanded_array1 = array1.repeat(num_point2, 1)
    expanded_array2 = torch.reshape(
            torch.unsqueeze(array2, 1).repeat(1, num_point1, 1),
            (-1, num_features2))

    distances = (expanded_array1-expanded_array2)* (expanded_array1-expanded_array2)
    distances = torch.sqrt(distances)
    
    distances = torch.clamp(distances, min=1e-7)

    distances = torch.sum(distances,dim=1)
    distances = torch.reshape(distances, (num_point2, num_point1))
    distances = torch.min(distances,dim=1)[0]


####GPS
'''
    #hyperparameters can be tuned:
   

    alpha, beta
    
'''
    alpha = 1
    beta = 1

    delta = alpha**(-1/beta)

    distances = alpha * ((distances)**beta)

    scaler1 = distances+delta
    
    distances =  -scaler1 * torch.exp(- scaler1)


    distances = torch.sum(distances)

    return distances



####GPS









def index_points(points, idx):
    """
    Input:
        points: input points data, [B, N, C]
        idx: sample index data, [B, S]
    Return:
        new_points:, indexed points data, [B, S, C]
    """
    device = points.device
    B = points.shape[0]
    view_shape = list(idx.shape)
    view_shape[1:] = [1] * (len(view_shape) - 1)
    repeat_shape = list(idx.shape)
    repeat_shape[0] = 1
    batch_indices = torch.arange(B, dtype=torch.long).to(device).view(view_shape).repeat(repeat_shape)
    new_points = points[batch_indices, idx, :]
    return new_points

def farthest_point_sample(xyz, npoint,RAN = True):
    """
    Input:
        xyz: pointcloud data, [B, N, C]
        npoint: number of samples
    Return:
        centroids: sampled pointcloud index, [B, npoint]
    """
    device = xyz.device
    B, N, C = xyz.shape
    centroids = torch.zeros(B, npoint, dtype=torch.long).to(device)
    distance = torch.ones(B, N).to(device) * 1e10
    if RAN :
        farthest = torch.randint(0, 1, (B,), dtype=torch.long).to(device)
    else:
        farthest = torch.randint(1, 2, (B,), dtype=torch.long).to(device)
    
    batch_indices = torch.arange(B, dtype=torch.long).to(device)
    for i in range(npoint):
        centroids[:, i] = farthest
        centroid = xyz[batch_indices, farthest, :].view(B, 1, 3)
        dist = torch.sum((xyz - centroid) ** 2, -1)
        mask = dist < distance
        distance[mask] = dist[mask]
        farthest = torch.max(distance, -1)[1]
    return centroids





