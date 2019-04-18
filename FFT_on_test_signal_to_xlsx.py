import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib inline

#file = r'.\MD_result_S06.tim.xls'
file = r'.\153_OPG_Digging_OF_Rt90deg-dump.csv'
# data_raw = pd.read_csv(file, sep=',',header=None,skiprows=12)
loadcase_line_number = 1
sample_rate_line_number = 8
channel_name_line_number = 9
channel_unit_line_number = 12
data_start_line_number = 13


loadcase_name = pd.read_csv(file, sep=',', header=None, nrows=1).values[0][1]
channel_name = pd.read_csv(file, sep=',', header=None, skiprows=channel_name_line_number-1,nrows=1).values[0]
channel_unit = pd.read_csv(file, sep=',', header=None, skiprows=channel_unit_line_number-1,nrows=1).values[0]
sampling_rate = int(pd.read_csv(file, sep=',', header=None, skiprows=sample_rate_line_number-1,nrows=1).values[0][1])
data_raw = pd.read_csv(file, sep=',', header=None, skiprows=data_start_line_number-1)

#Butterworth bandpass digital filter
from scipy.signal import butter, lfilter


def butter_bandpass(lowcut, highcut, fs, order=2):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=8):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

#This is the complete FFT process on test data, produce the freq-amplitude data set
def FFT(data, sampling_rate, frequency_spacing, overlap_ratio, averaging_method='Peak hold', window_type='Hanning'):
    freq_end = 50 # up to 50Hz
    
    def FFT_transform(data_piece, sampling_rate):
        timestep = 1 / sampling_rate
        Amplitude = abs(np.fft.rfft(data_piece*np.hanning(len(data_piece))))/(len(data_piece))*4
        frequency = np.fft.rfftfreq(len(data_piece),d=timestep)
        return frequency[0:len(Amplitude)],Amplitude

    def peak_hold_data(data_table): # one piece of the freq curce is an (n,1) pd.Series, all of them make a table
        index_list = list()
        temp_values = list()
        for index, row in data_table.iterrows():
            index_list.append(index)
            temp_values.append(np.max(row))
        data_peak_hold = pd.Series(temp_values, index=index_list)
        return data_peak_hold
    
    piece_length = int(1 / frequency_spacing)
    piece_select_step_length = int(piece_length * overlap_ratio)
    piece_number = 2 * int((len(data) / sampling_rate)/ piece_length) - 1
    
    pieces_raw = dict()
    for i in range(piece_number):
        t_s = i*piece_select_step_length*sampling_rate
        t_e = t_s + piece_length*sampling_rate
        x, y = FFT_transform(data[t_s:t_e],sampling_rate)
        freq_piece = pd.Series(y[:freq_end*piece_length], index=x[:freq_end*piece_length])
        pieces_raw[str(i)] = freq_piece
    freq_pieces = pd.DataFrame(pieces_raw)
    
    if averaging_method == 'Peak hold':
        result = peak_hold_data(freq_pieces)
        
    return result

def peak_select(temp_peak_piece, number_of_peaks=7, threhold=0.8): # select peaks
    #Select first number_of_peaks peaks in the frequency domain
    temp_old = 0
    index_old = 0
    peaks = list()
    peaks_index = list()
    for index in temp_peak_piece.index:
        temp = temp_peak_piece[index]
        if temp >= temp_old:
            temp_old = temp
        else:
            peaks.append(temp_old)
            peaks_index.append(index_old)
            temp_old = temp
        index_old = index
    peaks_series = pd.Series(peaks, index=peaks_index)
    peaks_series_sorted = peaks_series.sort_values(ascending=False)

    peaks_series_sorted_selected = pd.Series()
    peaks_series_sorted_selected = peaks_series_sorted_selected.append(pd.Series([peaks_series_sorted.iloc[0],], index=[peaks_series_sorted.index[0],]))
    jsq = 0
    for i in range(1,len(peaks_series_sorted)):
        flag = False
        for j in peaks_series_sorted_selected.index:
            if abs(peaks_series_sorted.index[i]-j)<threhold:
                flag = True
        if flag == False:
            jsq += 1
            peaks_series_sorted_selected = peaks_series_sorted_selected.append(pd.Series([peaks_series_sorted.iloc[i],],index=[peaks_series_sorted.index[i],]))
        if len(peaks_series_sorted_selected) == number_of_peaks:
            break
            
    #form a table to introduce the values
    first_index = list()
    second_index = ['freq','Amplitude']
    for i in range(number_of_peaks):
        name = '#{} critical freq'.format(str(i+1))
        first_index.append(name)
    index_iter = [first_index, second_index]
    index = pd.MultiIndex.from_product(index_iter)
    
    #form the result list
    values_to_show = list()
    for i in peaks_series_sorted_selected.index:
        values_to_show.append(round(i,2))
        values_to_show.append(round(peaks_series_sorted_selected[i],2))
    peaks_series_sorted_selected_table = pd.Series(values_to_show, index = index)
    return peaks_series_sorted_selected_table

#To process the amplitude of the data in time domain
def Amplitude_in_time(data, sampling_rate, ts=0, te=-1):
    x_axis = np.arange(0, int(len(data)/sampling_rate), 1/sampling_rate)
    
    # overall reslut
    Acc_max_overall = np.max(data)
    Acc_max_overall_time = np.where(data == Acc_max_overall)[0][0] * (1/sampling_rate)
    Acc_min_overall = np.min(data)
    Acc_min_overall_time = np.where(data == Acc_min_overall)[0][0] * (1/sampling_rate)
    Acc_range_overall = Acc_max_overall-Acc_min_overall
    
    # result in specified time period
    if te==-1:
        Acc_max = np.max(data)
        Acc_max_time = np.where(data == Acc_max)[0][0] * (1/sampling_rate)
        Acc_min = np.min(data)
        Acc_min_time = np.where(data == Acc_min)[0][0] * (1/sampling_rate)
    else:    
        Acc_max = np.max(data[ts*sampling_rate:te*sampling_rate])
        Acc_max_time = np.where(data == Acc_max)[0][0] * (1/sampling_rate)
        Acc_min = np.min(data[ts*sampling_rate:te*sampling_rate])
        Acc_min_time = np.where(data == Acc_min)[0][0] * (1/sampling_rate)
    Acc_range = Acc_max-Acc_min
    
    Acc_processer_items = [('Acc min', 'time'),
                         ('Acc min', 'value'),
                         ('Acc max', 'time'),
                         ('Acc max', 'value'),
                         ('Acc Range', 'value'),
                         ('Acc Overall Range', 'value'),]
#     Accs_index = pd.MultiIndex.from_tuples(Acc_processer_items, names=['item', 'detail'])
    Accs_index = pd.MultiIndex.from_tuples(Acc_processer_items)
    Accs = [round(Acc_min_time,2),
            round(Acc_min,2),
            round(Acc_max_time,2),
            round(Acc_max,2),
            round(Acc_range,2),
            round(Acc_range_overall,2)]
    Acc_Series = pd.Series(Accs, index = Accs_index )
    return Acc_Series
  
  Output_file_name = r'.\313 OMSA preresult.xlsx'
freq_low, freq_high = 5, 50
frequency_spacing = 1 / 4
overlap_ratio = 1 / 2
ts, te = 160, 260

Final_result = pd.DataFrame()
for i in range(data_raw.shape[1]):
    channel_data = data_raw[[i]]
    # do digital filter on the raw data
    channel_data_filtered = butter_bandpass_filter(channel_data.values.ravel(),freq_low,freq_high,sampling_rate)
    # do FFT to get the freq info
    channel_data_filtered_freq = FFT(channel_data_filtered[ts*sampling_rate:te*sampling_rate], sampling_rate, frequency_spacing, overlap_ratio)
    # get the peaks in the freq info
    channel_data_filtered_peaks = peak_select(channel_data_filtered_freq)
    # get the Accs info in the filtered data
    Accs_data = Amplitude_in_time(channel_data_filtered, sampling_rate, ts, te)
    channel_result_series = Accs_data.append(channel_data_filtered_peaks)
    temp_dataframe = pd.DataFrame(channel_result_series, columns=[channel_name[i],])
    Final_result = pd.concat([Final_result,temp_dataframe], axis=1)
Final_result.to_excel(Output_file_name, sheet_name = loadcase_name)
