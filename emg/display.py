from matplotlib import pyplot as plt
from matplotlib.ticker import ScalarFormatter
import numpy as np
import warnings


def predict_report(inpt, output, target):
    fig, axs = plt.subplots(target.shape[1], 1, squeeze=False, figsize=(16, 9))

    for i in range(target.shape[1]):
        x, y, z = inpt[:, i], output[:, i], target[:, i]
        bottom, top = min(y.min(), z.min()), max(y.max(), z.max())

        r = z - y
        axs[i][0].plot(abs(r) + bottom, 'b-', linewidth=1, alpha=.5,
                       label='absolute errors')

        axs[i][0].plot(y, 'k-', linewidth=1, label='predictions')
        axs[i][0].plot(z, 'r-', linewidth=2, label='truth')

        axs[i][0].set_ylim([bottom, top])

    axs[0][0].legend()

def visualize_emg(model, start, stop):
    """ Creates a visualization of the emg signals contained in model
        
        Args:
            model (model.Experiment, model.Session, model.Recording, model.Trial): A data
                carrying entity from module model.model.
            start (float): Start time in seconds
            stop (float): Stop time in seconds

        Note:
            Works for model.Experiment only in the case of all setups specifying the same
            frequency.

        Raises:
            ValueError: If start is larger than duration

        Warnings:
            If stop is larger than duration of recording
    """
    data = model.get_data()

    fig, axes = plt.subplots(nrows = data.shape[1], figsize = (16,9))
    fig.tight_layout()
    f = model.get_frequency()

    fontdict = {
        'fontsize': 16,
        'fontweight' : 'bold',
        'verticalalignment': 'baseline',
        'horizontalalignment': 'center'
    }

    if f * start > data.shape[0]:
        warnings.warn(
            'Start point to large. Recording is %fs long, but wanted to view from %f' %
            (data.shape[0] / f, start)
        )
        return

    if f * stop > data.shape[0]:
        warnings.warn(
            (
                'Specified time longer than series. Series is %s long, wanted to' +
                'view til %f. Set stop to end of recording'
            ) %
            (data.shape[0]/f, stop)
        )
        stop = data.shape[0] / f

    minimum = data.iloc[start * f : stop * f, :].values.min()
    maximum = data.iloc[start * f : stop * f, :].values.max()

    for i in range(data.shape[1]):
        axes[i].plot(
            np.arange(start * f, stop * f, dtype = 'float') / f, 
            data.iloc[start * f : stop * f, i]
        )
        axes[i].axvline(start + 0.2, c='r')
        axes[i].set_title(data.columns.values[i], fontdict = fontdict)
        axes[i].set_ylim([minimum, maximum])

    plt.subplots_adjust(hspace = 0.5)


