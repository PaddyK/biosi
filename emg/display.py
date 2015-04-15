from matplotlib import pyplot as plt


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
