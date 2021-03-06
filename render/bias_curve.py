import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline,UnivariateSpline
import logging,sys
from utils import histogram

def plot_gain_drop(datas,labels,xaxis='pe',colors=['k','b','g','r','c'],style=[],xlim=[0,200], ylim=[5e-3,1e8], title= 'Rates', axis=None):
    log = logging.getLogger(sys.modules['__main__'].__name__)
    fig = plt.figure(figsize=(14, 12))

    if axis is None:
        ax1 = fig.add_subplot(111)

    else:

        ax1 = axis
    #ax2 = ax1.twiny()
    if xaxis=='pe':
        index=5
    else:
        index=0
    xlim_min = xlim[0]
    xlim_max = xlim[1]
    ylim_min = float(ylim[0])
    ylim_max = float(ylim[1])
    for i,data in enumerate(datas):
        log.info('---> Data for plot %s %s in %s -------------------------------'%(title,labels[i],xaxis))

        #f = InterpolatedUnivariateSpline(data[index], data[3], w = 1./data[4], k=1)
        #xnew = np.linspace(data[index,0],data[index,-1], num=400, endpoint=True)
        #ynew = f(xnew)

        ax1.errorbar(data[index], data[3], yerr=data[4], fmt='o',color='%s'%(colors[i]), ecolor='%s'%(colors[i]), markersize = 6, linewidth=2)

        ax1.plot(data[index], data[3],color='%s'%colors[i], linestyle='%s'%style[i] ,label=labels[i], linewidth = 2)
        #ax1.plot(xnew, ynew, color='%s' % colors[i], linestyle='%s' % style[i], label=labels[i])

        ax1.fill_between(data[index], data[3]-data[4],data[3]+data[4], alpha= 0.3, edgecolor='%s'%colors[i], facecolor='%s'%colors[i])
        data0str = '%s - x: ['%labels[i]
        opt = ''
        for jj in data[0]:
            data0str+=' %s %s'%(opt,jj)
            opt=','
        data0str+=']'
        log.info(data0str)
        data3str = '%s - y: [' % labels[i]
        opt = ''
        for jj in data[3]:
            data3str += ' %s %s' % (opt,jj)
            opt = ','
        data3str += ']'
        log.info(data3str)
        data4str = '%s - y_err: [' % labels[i]
        opt = ''
        for jj in data[4]:
            data4str += ' %s %s' % (opt,jj)
            opt = ','
        data4str += ']'
        log.info(data4str)
        #ax1.plot(xnew, f(xnew) , color='%s'%colors[i])

    #ax1.plot(np.arange(xlim_min - 5, xlim_max + 5), np.ones(np.arange(xlim_min - 5, xlim_max + 5).shape[0]) * 6000.,
    #         label='Max. DAQ rate (6kHz)', linestyle='--',  color='k',linewidth=2.)
    #ax1.plot(np.arange(xlim_min - 5, xlim_max + 5), np.ones(np.arange(xlim_min - 5, xlim_max + 5).shape[0]) * 500.,
    #         label='Max. physics rate (500Hz)', linestyle='--', color='k', linewidth=2.)

    ax1.set_yscale('log')
    ax1.set_xlabel('Threshold for cluster of 21 pixels [p.e.]' if index==5 else 'Threshold for cluster of 21 pixels [LSB]')
    ax1.set_ylabel('Rate [Hz]')
    ax1.xaxis.get_label().set_ha('right')
    ax1.xaxis.get_label().set_position((1, 0))
    ax1.yaxis.get_label().set_ha('right')
    ax1.yaxis.get_label().set_position((0, 1))
    ax1.set_title(title)
    ax1.set_xlim(xlim_min, xlim_max)
    ax1.set_ylim(ylim_min, ylim_max)
    ax1.legend()

    plt.show()

    return ax1

def load_mc(file,var,nsb,offset = 0.):
    h = histogram.Histogram(filename=file)
    d = np.append(h.bin_centers.reshape(1,-1)+offset,h.bin_centers.reshape(1,-1),axis=0)
    d = np.append(d,h.bin_centers.reshape(1,-1),axis=0)
    d = np.append(d,h.data[int(var),:].reshape(1,-1),axis=0)
    d = np.append(d,h.errors[int(var),:].reshape(1,-1),axis=0)
    d = np.append(d,(d[0]*4/5.6/ (1. / (1 + 10000. * float(nsb) * 85e-15)) ).reshape(1,-1),axis=0)
    #

    return d

def load_care(file, nsb, offset = 0.):
    h = np.genfromtxt(file).T

    #print(h.shape)

    d = [h[0]+offset, h[0], h[0], h[1], h[2], h[0]*4/5.6/ (1. / (1 + 10000. * float(nsb) * 85e-15))]


    return d

def load_data(file):
    f = open(file,'r')
    keys = []
    line = ''
    #print(file)
    while '# HEADER' not in line:
        line = f.readline()
    keys = f.readline().split('# ')[1].split('\n')[0].split('\t')
    while '# DATA' not in line:
        line = f.readline()
    readlines = f.readlines()
    #print(len(readlines[0].split('\n')[0].split('\t')))
    #lines = []
    #for i in range(len(readlines[0].split('\n')[0].split('\t'))):
    #    lines+=[[]]
    #for l in readlines:
    #    for ii,v in enumerate(l.split('\n')[0].split('\t')):
    #        lines[ii].append(v)
    lines = list(
        map(list, zip(*[l.split('\n')[0].split('\t') for l in readlines])))

    _map_dict = dict(zip(keys, lines))
    for k in _map_dict.keys():
        _map_dict[k] = [float(x) for x in _map_dict[k]]
    # Sort by threshold
    for k in filter(lambda x: x != 'threshold', _map_dict.keys()):
        _map_dict[k] = np.array([v[1]for v in sorted(zip(_map_dict['threshold'], _map_dict[k]))])
        if k in ['trigger_cnt','readout_cnt'] : _map_dict[k]= _map_dict[k]-1
    # make it a list

    return _map_dict


def rate_calc(data,nsb=1.e9):
    # data[0,1,2]: threshold, cnt, time
    data = np.array(data)
    if data.shape[0]==3:
        samples = data[2] / 4e-9
        p = data[1] / data[2] * 4e-9
        q = 1. - p
        # in data[3], put the rate in Hz
        data = np.append(data,(data[1]/data[2]).reshape(1,data.shape[1]),axis=0)
        # in data[4], put the binomial error on rate in Hz
        data = np.append(data,(np.sqrt(samples*p*q)/samples).reshape(1,data.shape[1]),axis=0)
    # in data[5], put the gain drop corrected NPE
    data = np.append(data,(data[0]*4./5.6 / (1. / (1 + 10000. * float(nsb) * 85e-15))).reshape(1,data.shape[1]),axis=0)
    #
    #sort0 = data[0,:].argsort()
    #for i,d in enumerate(data):
    #    data[i]=data[i,sort0]
    return np.copy(data)


def get_datasets(options):
    datasets = []
    for i,legend in enumerate(options.legends):
        datasets.append([])
        for j, l in enumerate(legend):
            if l.count('TOY')>0.:
                data = load_mc(options.base_directory+options.dataset[i][j],options.variable[i][j], nsb=options.NSB[i][j],offset=options.offset[i][j])
                datasets[-1].append(data )

            elif l.count('CARE')>0.:

                data = load_care(options.base_directory+options.dataset[i][j], nsb=options.NSB[i][j], offset=options.offset[i][j])
                datasets[-1].append(data )
            else:
                data = load_data(options.base_directory+options.dataset[i][j])
                datasets[-1].append(rate_calc([data['threshold'],data[options.variable[i][j]],data['time']] , nsb=options.NSB[i][j]))

    return datasets

def plot(options):
    plt.ion()
    datasets = get_datasets(options)
    for i,d in enumerate(datasets):
        plot_gain_drop(d,labels=options.legends[i],xaxis=options.xaxis[i],colors=options.color[i],style=options.style[i],xlim=options.x_lim[i],ylim=options.y_lim[i],title=options.title[i])


def plot_mc_vs_data(options):

    datasets = np.array(get_datasets(options=options))
    print(datasets.shape)

    import matplotlib.gridspec as gridspec
    from scipy.interpolate import interp1d

    gs = gridspec.GridSpec(2, 1, width_ratios=[1], height_ratios=[3, 1], hspace=0.05)

    color = ['r', 'g']

    plt.figure(figsize=(10, 10))
    axis_histogram = plt.subplot(gs[0])
    axis_residue = plt.subplot(gs[1])
    #axis_slope = plt.subplot(gs[2])

    plot_gain_drop(datasets[1], labels=options.legends[1], xaxis=options.xaxis[1], colors=options.color[1],
                   style=options.style[1], xlim=options.x_lim[1], ylim=options.y_lim[1], title=options.title[1], axis=axis_histogram)


    data = datasets[1][0]
    toy = datasets[1][1]
    care = datasets[1][2]
    print(toy)

    x_residu = np.linspace(max(np.min(data[0]), np.min(toy[0]), min(care[0])), min(np.max(data[0]), toy[0][np.where(toy[3]==0)[0][0]-1], np.max(care[0])), num=20)

    print(x_residu)
    print(np.max(toy[0]))
    print(toy[3])
    print(toy[0][np.where(toy[3] == 0)[0][0]])
    print(np.where(toy[3] == 0)[0][0])
    y_data = interp1d(data[0], data[3], kind='linear')(x_residu)
    y_toy = interp1d(toy[0], toy[3], kind='linear')(x_residu)
    y_care = interp1d(care[0], care[3], kind='linear')(x_residu)
    err_data = interp1d(data[0], data[4], kind='linear')(x_residu)
    err_toy = interp1d(toy[0], toy[4], kind='linear')(x_residu)
    err_care = interp1d(care[0], care[4], kind='linear')(x_residu)

    axis_residue.errorbar(x_residu, np.abs(y_toy/y_data), yerr=np.sqrt((err_data/y_data)**2 + (err_toy/y_toy)**2), color=color[0], linestyle='None', marker='o')
    axis_residue.errorbar(x_residu, np.abs(y_care/y_data), yerr=np.sqrt((err_data/y_data)**2 + (err_care/y_care)**2), color=color[1], linestyle='None', marker='o')
    #axis_slope.errorbar((x_residu[1:] + x_residu[:-1]) / 2, np.abs(np.diff(y_data) - np.diff(y_toy)), color=color[0], linestyle='None', marker='o')
    #axis_slope.errorbar((x_residu[1:] + x_residu[:-1]) / 2, np.abs(np.diff(y_data) - np.diff(y_care)), color=color[1], linestyle='None', marker='o')




    axis_histogram.legend(loc='best')
    axis_histogram.set_yscale('log')
    axis_residue.set_yscale('log')
    #axis_slope.set_yscale('log')
    axis_residue.set_xlabel('[LSB]')
    axis_residue.set_ylabel('MC over Data', fontsize=12)
    axis_histogram.axes.get_xaxis().set_visible(False)
    lims = np.arange(0, 22, 2)
    axis_residue.set_xticks(lims)
    axis_histogram.set_xlim(lims[0], lims[-1])


    plt.show()

