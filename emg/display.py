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

def visualize_modality(model, start, stop, modality=None):
    """ Creates a visualization of the modality signals contained in model

        Args:
            model (model.Experiment, model.Session, model.Recording, model.Trial): A data
                carrying entity from module model.model.
            start (float): Start time in seconds
            stop (float): Stop time in seconds
            modality (String, optional): Must be set if more than one modality specified

        Note:
            Works for model.Experiment only in the case of all setups specifying the same
            frequency.

        Raises:
            ValueError: If start is larger than duration

        Warnings:
            If stop is larger than duration of recording
    """
    data = model.get_data(modality=modality, from_=start, to=stop)
    fig, axes = plt.subplots(nrows = data.shape[1], figsize = (16, data.shape[1] * 2.5))
    fig.tight_layout()
    f = model.get_frequency(modality=modality)

    fontdict = {
        'fontsize': 16,
        'fontweight' : 'bold',
        'verticalalignment': 'baseline',
        'horizontalalignment': 'center'
    }

    minimum = data.values.min()
    maximum = data.values.max()

    for i in range(data.shape[1]):
        xvals = np.arange(
                start * f,
                start * f + data.shape[0],
                dtype = 'float') / f
        axes[i].plot(
            xvals,
            data.iloc[:, i]
        )
        axes[i].set_title(data.columns.values[i], fontdict = fontdict)
        axes[i].set_ylim([minimum, maximum])

    markers = model.get_marker(modality=modality, from_=start, to=stop)
    for t, l in markers:
        for axis in axes:
            axis.axvline(t, color='r')
            axis.text(t, maximum, l, color='r', verticalalignment='top')

    plt.subplots_adjust(hspace = 0.5)
#    plt.show()

if __name__ == '__main__':
    import sys
    sys.path.insert(0, '/home/patrick/GitHub/interdisciplinary_project')
    import model.knowledgeBase as kb
    import model.model as model
    e = kb.small_sport_kb()
    visualize_emg(e, 0, 18)
