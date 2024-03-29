import numpy as np
import tifffile as tf
import ntpath
import os
import matplotlib.pyplot as plt
import seaborn as sns
import csv
from lxml import objectify
from lxml import etree
import math

#global plotting params
params = {'legend.fontsize': 'x-large',
         'axes.labelsize': 'x-large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'x-large',
         'ytick.labelsize':'x-large'}
plt.rcParams.update(params)
sns.set()
sns.set_style('white')

def dfof(arr):

    '''takes 1d list or array or 2d array and returns dfof array of same dim (JR 2019)'''

    if type(arr) is list or type(arr) == np.ndarray and len(arr.shape) == 1:
        F = np.median(arr)
        dfof_arr = [((f- F) / F) * 100 for f in arr]

    elif type(arr) == np.ndarray and len(arr.shape) == 2:
        dfof_arr = []
        for trace in arr:
            F = np.median(trace)
            dfof_arr.append([((f - F) / F) * 100 for f in trace])

    else:
        raise NotImplementedError('input type not recognised')

    return np.array(dfof_arr)


def get_tiffs(path):

    tiff_files = []
    for file in os.listdir(path):
        if file.endswith('.tif') or file.endswith('.tiff'):
            tiff_files.append(os.path.join(path,file))

    return tiff_files


def s2p_loader(s2p_path, subtract_neuropil=True):

    for root,dirs,files in os.walk(s2p_path):

        for file in files:

            if file == 'F.npy':
                all_cells = np.load(os.path.join(root, file))
            elif file == 'Fneu.npy':
                neuropil = np.load(os.path.join(root, file))
            elif file == 'iscell.npy':
                is_cells = np.load(os.path.join(root, file))[:,0]
                is_cells = np.ndarray.astype(is_cells, 'bool')
            elif file == 'stat.npy':
                stat = np.load(os.path.join(root, file))


    for i,s in enumerate(stat):
        s['original_index'] = i

    stat = stat[is_cells]

    if not subtract_neuropil:
        return all_cells[is_cells, :], stat

    else:
        neuropil_corrected = all_cells - neuropil
        return neuropil_corrected[is_cells, :], stat



def read_fiji(csv_path):

    '''reads the csv file saved through plot z axis profile in fiji'''

    data = []

    with open(csv_path, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for i,row in enumerate(spamreader):
            if i ==0 : continue
            data.append(float(row[0].split(',')[1]))

    return np.array(data)


def save_fiji(arr):
    '''saves numpy array in current folder as fiji friendly tiff'''
    tf.imsave('Vape_array.tiff', arr.astype('int16'))


def threshold_detect(signal, threshold):
    '''lloyd russell'''
    thresh_signal = signal > threshold
    thresh_signal[1:][thresh_signal[:-1] & thresh_signal[1:]] = False
    times = np.where(thresh_signal)
    return times[0]


def pade_approx_norminv(p):
    q = math.sqrt(2*math.pi) * (p - 1/2) - (157/231) * math.sqrt(2) * math.pi**(3/2) * (p - 1/2)**3
    r = 1 - (78/77) * math.pi * (p - 1/2)**2 + (241* math.pi**2 / 2310) * (p - 1/2)**4
    return q/r

def d_prime(hit_rate, false_alarm_rate):
    return pade_approx_norminv(hit_rate) - pade_approx_norminv(false_alarm_rate)


def paq_data(paq, chan_name, threshold_ttl=False, plot=False):
    '''
    returns the data in paq (from paq_read) from channel: chan_names
    if threshold_tll: returns sample that trigger occured on
    '''

    chan_idx = paq['chan_names'].index(chan_name)
    data = paq['data'][chan_idx, :]
    if threshold_ttl:
        data = threshold_detect(data, 1)

    if plot:
        if threshold_ttl:
            plt.plot(data, np.ones(len(data)), '.')
        else:
            plt.plot(data)

    return data


def stim_start_frame(paq, stim_chan_name):

    '''gets the frames (from channel frame_clock) that a stim occured on'''

    frame_clock = paq_data(paq, 'frame_clock', threshold_ttl=True)
    stim_times  = paq_data(paq, stim_chan_name, threshold_ttl=True)

    stim_times = [stim for stim in stim_times if stim < max(frame_clock)]

    frames = []

    for stim in stim_times:
        #the sample time of the frame immediately preceeding stim
        frame = next(frame_clock[i-1] for i,sample in enumerate(frame_clock) if sample - stim > 0)
        frames.append(frame)

    return(frames)

def myround(x, base=5):
    
    '''allow rounding to nearest base number for use with multiplane stack slicing'''
    
    return base * round(x/base)

def TraceExtractor(iscell,f_all):
    '''Extracts traces only from ROIs, leaving non-ROIs behind

    input:

    f_all: All traces
    iscell: Binary vector, 1 for ROIs, 0 for non-ROIs

    Returns traces of ROIs

    Packer-lab
    2019-07-30 Created by DAC'''

    index_ROIs = [i for i, e in enumerate(iscell[:,0]) if e != 0]
    return f_all[index_ROIs]