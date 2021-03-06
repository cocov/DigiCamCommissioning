import numpy as np
import h5py
import logging, sys


class telescope():

    def __init__(self, id,):

        self.eventNumber = 0
        self.adc_samples = {}
        self.id = id

class dl0():

    def __init__(self,id_list = [0], event_id=0):

        self.tels_with_data = []
        self.event_id = event_id
        self.tel = {}

        for id in id_list:

            self.tels_with_data.append(id)
            self.tel[id]=telescope(id)

    def set_data(self,telid,evtnum,adcs):

        self.tel[telid].eventNumber = evtnum
        self.tel[telid].adc_samples = {i: adcs[i] for i in range(len(adcs))}

class ToyReader(): # create a reader as asked

    def __init__(self, filename='../../digicamtoy/data_calibration_cts/toy_data_', id_list = [0], max_events=50000, n_pixel=1296, events_per_level=1000, seed=0, level_start=0):
        self.count = 0
        self.event_id = 0
        self.dl0 = dl0(id_list, event_id=self.count)
        self.evt_max = max_events
        self.id_list = id_list
        #open file
        self.filename = filename
        self.n_pixel = n_pixel
        self.hdf5_file = h5py.File(self.filename, 'r')
        self.events_per_level = events_per_level
        self.seed = seed
        self.level = level_start
        self.n_traces_tot = self.hdf5_file['dc_level_%d_ac_level_0'%self.level]['trace'].shape[0]
        self.n_samples = self.hdf5_file['dc_level_%d_ac_level_0'%self.level]['trace'].shape[1]
        np.random.seed(seed=self.seed)
        self.log = logging.getLogger(sys.modules['__main__'].__name__)

        self.log.info('\t\t-|> Will read a total of %d events with %d events per level for %d pixels, level_start = %d, seed = %d ' %(self.evt_max, self.events_per_level, self.n_pixel, self.level, self.seed))

        if self.events_per_level>self.evt_max:


            log.error('events_per_level %d must be <= than evt_max %d' %(self.events_per_level, self.evt_max))


        return


    def __iter__(self):

        return self

    def __next__(self):

         return self.next()


    def next(self):

        if self.count<self.evt_max:

            adcs = []

            i = 0

            data = self.hdf5_file['dc_level_%d_ac_level_0' % self.level]['trace']

            if self.n_traces_tot<self.n_pixel:
                self.log.error('Could not find trace in because file contains %d traces and asked for %d pixels' %(self.n_traces_tot, self.n_pixel))

            random_sample = np.arange(0, self.n_traces_tot, 1)
            np.random.shuffle(random_sample)
            random_sample = random_sample[0:self.n_pixel]
            #random_sample = np.random.randint(low=0, high=self.n_traces_tot, size=self.n_pixel)
            while i<self.n_pixel:

                adcs.append(data[random_sample[i]])
                i = i + 1



            adcs = np.array(adcs).reshape(self.n_pixel, self.n_samples)

            for telid in self.id_list:
                self.dl0.set_data(telid, self.count, adcs)

            self.count += 1
            if not self.count%self.events_per_level:

                self.log.debug('\t\t-|> DC level %d cointains %d traces for %d pixels' %(self.level, self.count/(self.level+1), self.n_pixel))
                self.level += 1

        else:

            self.hdf5_file.close()
            raise StopIteration

        return self


if __name__ == '__main__':

    _url = '../../digicamtoy/data_calibration_cts/toy_data_0.hdf5'
    inputfile_reader = ToyReader(filename=_url, id_list=[0], max_events=2, weights=1.)
    i = 0

    print('event.dl0.tels_with_data', inputfile_reader.dl0.tels_with_data)

    for event in inputfile_reader:

        print(i)
        print('event.dl0.tels_with_data',event.dl0.tels_with_data)
        telid=0
        print('event.dl0.tel[telid].eventNumber',event.dl0.tel[telid].eventNumber)
        print('adcs',np.array(list(event.dl0.tel[telid].adc_samples.values())))
        print('adcs max in pixel 0',np.max(np.array(list(event.dl0.tel[telid].adc_samples.values()))[0,:]))
        print ('adcs shape : ',np.array(list(event.dl0.tel[telid].adc_samples.values())).shape)


        i = i+1

    print (i)