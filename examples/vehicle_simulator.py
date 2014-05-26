import os
import operator
#
import numpy
import pandas
#
from simulator import Simulator


def read_frame(filename, dirname='', index_col=None, colname_map=None):
    full_filename = os.path.join(dirname, filename)
    frame = pandas.read_csv(full_filename, index_col=index_col)
    if colname_map is not None:
        frame = frame.rename(columns=colname_map)
        pass
    return frame

gps_to_target = dict(GPSLat='y', GPSLon='x', Orientation='heading')
gps_frame_config = dict(filename='slam_gps.csv', index_col='TimeGPS',
        colname_map=gps_to_target)
control_frame_config = dict(filename='slam_control.csv', index_col='Time_VS')
laser_frame_config = dict(filename='slam_laser.csv', index_col='TimeLaser')
def read_frames(dirname):
    gps_frame = read_frame(dirname=dirname, **gps_frame_config)
    control_frame = read_frame(dirname=dirname, **control_frame_config)
    laser_frame = read_frame(dirname=dirname, **laser_frame_config)
    return gps_frame, control_frame, laser_frame

def create_gps_observes(gps_frame):
    def gps_xs_to_observe_tuple(gps_xs):
        time_as_float = gps_xs.name
        # FIXME: inject gps noise values
        observe_str = '(simulate_gps (get_pose %s) %s %s)' % (time_as_float, '%s', '%s')
        observe_val = (gps_xs.x, gps_xs.y, gps_xs.heading)
        return ((observe_str, observe_val), )
    process_tuple = lambda (t, xs): (t, gps_xs_to_observe_tuple(xs))
    return map(process_tuple, gps_frame.iterrows())

def create_control_observes(control_frame):
    def single_control_to_observe_tuples(dt, i, control_xs):
        return [
                ('(get_control_i %s 0)' % i, control_xs.Velocity),
                ('(get_control_i %s 1)' % i, control_xs.Steering),
                ('(dt %s)' % i, dt),
                ]
    dts = numpy.diff(list(control_frame.index))
    return [
            (t, single_control_to_observe_tuples(dt, i, control_xs))
            for (i, (dt, (t, control_xs))) in enumerate(zip(dts, control_frame.iterrows()))
            ]

def create_sample_strs(ts):
    get_sample_str = lambda t: '(get_pose %s)' % t
    return map(get_sample_str, ts)

def create_observe_sample_strs_lists(gps_frame, control_frame, N_timesteps=None):
    def interleave_observes(*args):
        all_observes = reduce(operator.add, map(list, args))
        my_cmp = lambda x, y: cmp(x[0], y[0])
        all_observes = sorted(all_observes, cmp=my_cmp)
        ts, observes = zip(*all_observes)
        return ts, observes
    gps_observes = create_gps_observes(gps_frame)
    control_observes = create_control_observes(control_frame)
    ts, observe_strs_list = interleave_observes(control_observes, gps_observes)
    sample_strs_list = create_sample_strs(ts)
    observe_strs_list, sample_strs_list = \
            observe_strs_list[:N_timesteps], sample_strs_list[:N_timesteps]
    return observe_strs_list, sample_strs_list

def create_vehicle_simulator(dirname, program, N_mripls, backend,
        N_infer, N_timesteps=None):
    gps_frame, control_frame, laser_frame = read_frames(dirname)
    observe_strs_list, sample_strs_list = create_observe_sample_strs_lists(
            gps_frame, control_frame, N_timesteps)
    # create/pass diagnostics functions?
    simulator = Simulator(program, observe_strs_list, sample_strs_list,
            N_mripls, backend, N_infer)
    return simulator

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_name', type=str, default='5_eight')
    args = parser.parse_args()
    #
    dataset_name = args.dataset_name
    base_dir = '/home/dlovell/Desktop/PPAML/CP1-Quad-Rotor/data/automobile/'
    dirname = os.path.join(base_dir, dataset_name, 'data', 'noisy')
    #
    program = '[assume var 1]'
    N_mripls=2
    backend='puma'
    N_infer=3
    simulator = create_vehicle_simulator(dirname, program, N_mripls, backend,
            N_infer, N_timesteps=10)
