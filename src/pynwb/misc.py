import numpy as np
from collections import Iterable

from .form.utils import docval, getargs, popargs, call_docval_func

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries, _default_conversion, _default_resolution
from .core import NWBContainer, ElementIdentifiers, DynamicTable


@register_class('AnnotationSeries', CORE_NAMESPACE)
class AnnotationSeries(TimeSeries):
    """
    Stores text-based records about the experiment. To use the
    AnnotationSeries, add records individually through
    add_annotation() and then call finalize(). Alternatively, if
    all annotations are already stored in a list, use set_data()
    and set_timestamps()
    """

    __nwbfields__ = ()

    _help = "Time-stamped annotations about an experiment."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries),
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames',
             'default': list()},
            {'name': 'timestamps', 'type': ('array_data', 'data', TimeSeries), 'shape': (None, ),
             'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'comments', 'type': str,
             'doc': 'Human-readable comments about this TimeSeries dataset', 'default': 'no comments'},
            {'name': 'description', 'type': str, 'doc':
             'Description of this TimeSeries dataset', 'default': 'no description'},
            {'name': 'parent', 'type': NWBContainer,
             'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        name, data, timestamps = popargs('name', 'data', 'timestamps', kwargs)
        super(AnnotationSeries, self).__init__(name, data, 'n/a',
                                               resolution=-1.0, conversion=1.0,
                                               timestamps=timestamps, **kwargs)

    @docval({'name': 'time', 'type': float, 'doc': 'The time for the annotation'},
            {'name': 'annotation', 'type': str, 'doc': 'the annotation'})
    def add_annotation(self, **kwargs):
        '''
        Add an annotation
        '''
        time, annotation = getargs('time', 'annotation', kwargs)
        self.fields['timestamps'].append(time)
        self.fields['data'].append(annotation)


@register_class('AbstractFeatureSeries', CORE_NAMESPACE)
class AbstractFeatureSeries(TimeSeries):
    """
    Represents the salient features of a data stream. Typically this
    will be used for things like a visual grating stimulus, where
    the bulk of data (each frame sent to the graphics card) is bulky
    and not of high value, while the salient characteristics (eg,
    orientation, spatial frequency, contrast, etc) are what important
    and are what are used for analysis
    """

    __nwbfields__ = ('feature_units',
                     'features')

    _help = "Features of an applied stimulus. This is useful when storing the raw stimulus is impractical."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'feature_units', 'type': Iterable, 'shape': (None, ), 'doc': 'The unit of each feature'},
            {'name': 'features', 'type': Iterable, 'shape': (None, ), 'doc': 'Description of each feature'},
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries), 'shape': ((None,), (None, None)),
             'default': list(),
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'resolution', 'type': float,
             'doc': 'The smallest meaningful difference (in specified unit) between values in data',
             'default': _default_resolution},
            {'name': 'conversion', 'type': float,
             'doc': 'Scalar to multiply each element in data to convert it to the specified unit',
             'default': _default_conversion},
            {'name': 'timestamps', 'type': ('array_data', 'data', TimeSeries), 'shape': (None, ),
             'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},
            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset',
             'default': 'no comments'},
            {'name': 'description', 'type': str,
             'doc': 'Description of this TimeSeries dataset', 'default': 'no description'},
            {'name': 'control', 'type': Iterable,
             'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable,
             'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': NWBContainer,
             'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        name, data, features, feature_units = popargs('name', 'data',
                                                              'features', 'feature_units', kwargs)
        super(AbstractFeatureSeries, self).__init__(name, data, "see 'feature_units'", **kwargs)
        self.features = features
        self.feature_units = feature_units

    @docval({'name': 'time', 'type': float, 'doc': 'the time point of this feature'},
            {'name': 'features', 'type': (list, np.ndarray), 'doc': 'the feature values for this time point'})
    def add_features(self, **kwargs):
        time, features = getargs('time', 'features', kwargs)
        if type(self.timestamps) == list and type(self.data) is list:
            self.timestamps.append(time)
            self.data.append(features)
        else:
            raise ValueError('Can only add feature if timestamps and data are lists')


@register_class('IntervalSeries', CORE_NAMESPACE)
class IntervalSeries(TimeSeries):
    """
    Stores intervals of data. The timestamps field stores the beginning and end of intervals. The
    data field stores whether the interval just started (>0 value) or ended (<0 value). Different interval
    types can be represented in the same series by using multiple key values (eg, 1 for feature A, 2
    for feature B, 3 for feature C, etc). The field data stores an 8-bit integer. This is largely an alias
    of a standard TimeSeries but that is identifiable as representing time intervals in a machine-readable
    way.
    """

    __nwbfields__ = ()

    _help = "Stores the start and stop times for events."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries), 'shape': (None,),
             'doc': '>0 if interval started, <0 if interval ended.', 'default': list()},
            {'name': 'timestamps', 'type': ('array_data', 'data', TimeSeries), 'shape': (None,),
             'doc': 'Timestamps for samples stored in data', 'default': list()},
            {'name': 'comments', 'type': str,
             'doc': 'Human-readable comments about this TimeSeries dataset', 'default':  'no comments'},
            {'name': 'description', 'type': str,
             'doc': 'Description of this TimeSeries dataset', 'default':  'no description'},
            {'name': 'control', 'type': Iterable,
             'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable,
             'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': NWBContainer,
             'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        name, data, timestamps = popargs('name', 'data', 'timestamps', kwargs)
        unit = 'n/a'
        self.__interval_timestamps = timestamps
        self.__interval_data = data
        super(IntervalSeries, self).__init__(name, data, unit,
                                             timestamps=timestamps,
                                             resolution=-1.0,
                                             conversion=1.0,
                                             **kwargs)

    @docval({'name': 'start', 'type': float, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'stop', 'type': float, 'doc': 'The name of this TimeSeries dataset'})
    def add_interval(self, **kwargs):
        start, stop = getargs('start', 'stop', kwargs)
        self.__interval_timestamps.append(start)
        self.__interval_timestamps.append(stop)
        self.__interval_data.append(1)
        self.__interval_data.append(-1)

    @property
    def data(self):
        return self.__interval_data

    @property
    def timestamps(self):
        return self.__interval_timestamps


@register_class('Units', CORE_NAMESPACE)
class Units(DynamicTable):
    """
    Event times of observed units (e.g. cell, synapse, etc.).
    """

    __columns__ = (
        {'name': 'spike_times', 'description': 'the spike times for each unit', 'index': True},
        {'name': 'obs_intervals', 'description': 'the observation intervals for each unit',
         'index': True},
        {'name': 'electrodes', 'description': 'the electrodes that each spike unit came from',
         'index': True, 'table': True},
        {'name': 'electrode_group', 'description': 'the electrode group that each spike unit came from'},
        {'name': 'waveform_mean', 'description': 'the spike waveform mean for each spike unit'},
        {'name': 'waveform_sd', 'description': 'the spike waveform standard deviation for each spike unit'}
    )

    @docval({'name': 'name', 'type': str, 'doc': 'Name of this Units interface', 'default': 'Units'},
            {'name': 'id', 'type': ('array_data', ElementIdentifiers),
             'doc': 'the identifiers for the units stored in this interface', 'default': None},
            {'name': 'columns', 'type': (tuple, list), 'doc': 'the columns in this table', 'default': None},
            {'name': 'colnames', 'type': 'array_data', 'doc': 'the names of the columns in this table',
             'default': None},
            {'name': 'description', 'type': str, 'doc': 'a description of what is in this table', 'default': None})
    def __init__(self, **kwargs):
        if kwargs.get('description', None) is None:
            kwargs['description'] = ""
        call_docval_func(super(Units, self).__init__, kwargs)
        if 'spike_times' not in self.colnames:
            self.__has_spike_times = False

    @docval({'name': 'spike_times', 'type': 'array_data', 'doc': 'the spike times for each unit',
             'default': None, 'shape': (None,)},
            {'name': 'obs_intervals', 'type': 'array_data',
             'doc': 'the observation intervals (valid times) for each unit. All spike_times for a given unit ' +
             'should fall within these intervals. [[start1, end1], [start2, end2], ...]',
             'default': None, 'shape': (None, 2)},
            {'name': 'electrodes', 'type': 'array_data', 'doc': 'the electrodes that each unit came from',
             'default': None},
            {'name': 'electrode_group', 'type': 'array_data', 'default': None,
             'doc': 'the electrode group that each unit came from'},
            {'name': 'waveform_mean', 'type': 'array_data', 'doc': 'the spike waveform mean for each unit',
             'default': None},
            {'name': 'waveform_sd', 'type': 'array_data', 'default': None,
             'doc': 'the spike waveform standard deviation for each unit'},
            {'name': 'id', 'type': int, 'default': None,
             'help': 'the id for each unit'},
            allow_extra=True)
    def add_unit(self, **kwargs):
        """
        Add a unit to this table
        """
        super(Units, self).add_row(**kwargs)

    @docval({'name': 'index', 'type': int,
             'doc': 'the index of the unit in unit_ids to retrieve spike times for'})
    def get_unit_spike_times(self, **kwargs):
        index = getargs('index', kwargs)
        return np.asarray(self['spike_times'][index])

    @docval({'name': 'index', 'type': int,
             'doc': 'the index of the unit in unit_ids to retrieve observation intervals for'})
    def get_unit_obs_intervals(self, **kwargs):
        index = getargs('index', kwargs)
        return np.asarray(self['obs_intervals'][index])


@register_class('DecompositionSeries', CORE_NAMESPACE)
class DecompositionSeries(TimeSeries):
    """
    Stores product of spectral analysis
    """

    __nwbfields__ = ('metric',
                     {'name': 'source_timeseries', 'child': False, 'doc': 'the input TimeSeries from this analysis'},
                     {'name': 'bands',
                      'doc': 'the bands that the signal is decomposed into', 'child': True})

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries),
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset'},
            {'name': 'metric', 'type': str, 'doc': "metric of analysis. recommended: 'phase', 'amplitude', 'power'"},
            {'name': 'unit', 'type': str, 'doc': 'SI unit of measurement', 'default': 'no unit'},
            {'name': 'bands', 'type': DynamicTable,
             'doc': 'a table for describing the frequency bands that the signal was decomposed into', 'default': None},
            {'name': 'source_timeseries', 'type': TimeSeries,
             'doc': 'the input TimeSeries from this analysis', 'default': None},
            {'name': 'resolution', 'type': float,
             'doc': 'The smallest meaningful difference (in specified unit) between values in data',
             'default': _default_resolution},
            {'name': 'conversion', 'type': float,
             'doc': 'Scalar to multiply each element by to convert to unit', 'default': _default_conversion},

            {'name': 'timestamps', 'type': ('array_data', 'data', TimeSeries),
             'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},

            {'name': 'comments', 'type': str,
             'doc': 'Human-readable comments about this TimeSeries dataset', 'default': 'no comments'},
            {'name': 'control', 'type': Iterable,
             'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable,
             'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        metric, source_timeseries, bands = popargs('metric', 'source_timeseries', 'bands', kwargs)
        super(DecompositionSeries, self).__init__(**kwargs)
        self.source_timeseries = source_timeseries
        self.metric = metric
        if bands is None:
            bands = DynamicTable("bands", "data about the frequency bands that the signal was decomposed into")
        self.bands = bands

    def __check_column(self, name, desc):
        if name not in self.bands.colnames:
            self.bands.add_column(name, desc)

    @docval({'name': 'band_name', 'type': str, 'doc': 'the name of the frequency band',
             'default': None},
            {'name': 'band_limits', 'type': ('array_data', 'data'),
             'doc': 'low and high frequencies of bandpass filter in Hz'},
            {'name': 'band_mean', 'type': float, 'doc': 'the mean of Gaussian filters in Hz',
             'default': None},
            {'name': 'band_stdev', 'type': float, 'doc': 'the standard deviation of Gaussian filters in Hz',
             'default': None},
            allow_extra=True)
    def add_band(self, **kwargs):
        """
        Add ROI data to this
        """
        band_name, band_limits, band_mean, band_stdev = getargs('band_name', 'band_limits', 'band_mean', 'band_stdev',
                                                                kwargs)
        if band_name is not None:
            self.__check_column('band_name', "the name of the frequency band (recommended: 'alpha', 'beta', 'gamma', "
                                             "'delta', 'high gamma'")
        if band_name is not None:
            self.__check_column('band_limits', 'low and high frequencies of bandpass filter in Hz')
        if band_mean is not None:
            self.__check_column('band_mean', 'the mean of Gaussian filters in Hz')
        if band_stdev is not None:
            self.__check_column('band_stdev', 'the standard deviation of Gaussian filters in Hz')

        self.bands.add_row({k: v for k, v in kwargs.items() if v is not None})
