import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.cm import get_cmap
from matplotlib import colors, colorbar


np.random.seed(12345)

sample_data = pd.DataFrame([np.random.normal(32000, 200000, 3650),
                            np.random.normal(43000, 100000, 3650),
                            np.random.normal(43500, 140000, 3650),
                            np.random.normal(48000, 70000, 3650)],
                           index=[1992, 1993, 1994, 1995])


class MeansAndIntervals:
    """
    Calculates column-wise mean and error for the input dataframe. Default z value
    is for the 95% confidence interval.
    """
    def __init__(self, df=sample_data, z=1.96):
        self.means = df.mean(axis=1)
        self.error = df.sem(axis=1) * z


class InteractiveBarChart:
    """
    Interactive bar chart plotting means with errors. Users can click a region in the chart
    to select a y-value they want to compare to these distributions. A line will be drawn
    at that y-value and bars will be colored based on the likelihood that value is
    contained in the distribution.
    """
    def __init__(self, means, error, cmap):
        self.means = means
        self.error = error
        self.cmap = cmap  # color mapping to use for bars
        self.pos = np.arange(len(self.means))  # bar positions
        plt.figure(figsize=(7, 5))
        self.gspec = gridspec.GridSpec(3, 3, width_ratios=[0.3, 2, 2], height_ratios=[3, 3, 1], hspace=0.3)
        self.barchart = plt.subplot(self.gspec[0:2, 0:])
        self.cbar_plot = plt.subplot(self.gspec[2, 1:])
        self.rects = self.plot_bars()
        self.prettify_barchart()
        self.add_colorbar()

    def plot_bars(self):
        """
        Plots the means as bars with error lines.
        :return: list of rectangles (bars) in the chart
        """
        rects = self.barchart.bar(self.pos, self.means, yerr=self.error, capsize=7,
                                  color='white', edgecolor=[0, 0, 0, 0.8], ecolor=[0, 0, 0, 0.8])
        self.barchart.set_xticks(self.pos)
        self.barchart.set_xticklabels(self.means.index)
        left_xlim = self.barchart.get_xlim()[0]
        right_xlim = self.barchart.get_xlim()[1] + 1
        self.barchart.set_xlim([left_xlim, right_xlim])
        return rects

    def prettify_barchart(self):
        """
        Adjusts the opacity and visibility of the bar chart's frame. Adjusts the the opacity
        of the ticks and tick labels.
        """
        self.barchart.spines['top'].set_visible(False)
        self.barchart.spines['right'].set_visible(False)
        self.barchart.spines['left'].set_alpha(0.8)
        self.barchart.spines['bottom'].set_alpha(0.8)
        self.barchart.tick_params(axis=u'both', color=[0, 0, 0, 0.8], labelcolor=[0, 0, 0, 0.8])

    def add_colorbar(self):
        """
        Adds a colorbar below the bar chart showing the meaning of the bar colorings.
        """
        bounds = np.linspace(0, 1, num=12)
        norm = colors.BoundaryNorm(bounds, self.cmap.N)
        cbar = colorbar.ColorbarBase(self.cbar_plot, cmap=self.cmap, norm=norm, orientation='horizontal')
        colorbar_labels = [f'{n:.2f}' for n in bounds]
        cbar.set_ticks(bounds)
        cbar.set_ticklabels(colorbar_labels)
        cbar.set_label('Probability of a Distribution Containing the Given y-value', alpha=0.8)
        for spine in self.cbar_plot.spines.values():
            spine.set_alpha(0.8)
        self.cbar_plot.tick_params(axis='x', color=[0, 0, 0, 0.8], labelcolor=[0, 0, 0, 0.8])

    def on_click(self, event, barchart, rects, means, error, cmap):
        """
        Plots a horizontal line at a selected y-value, then colors the bars of the bar chart
        based on the likelihood that those distributions contain that y-value.
        :param event: mouse click
        :param barchart: chart on which to draw the line
        :param rects: bars whose colors are to be changed
        :param means: mean values
        :param error: error values
        :param cmap: color mapping to use for the bars
        """
        y_val = event.ydata
        # if we already drew a line in response to user click, remove it
        if len(barchart.lines) > 2:  # barchart.lines includes the error lines, so it is already len=2
            barchart.lines[-1].remove()
        # if we annotated the above line, remove the annotation as well
        if len(barchart.texts) > 0:
            barchart.texts[-1].remove()
        # draw the line and annotate with the y-value
        barchart.axhline(y_val, c='darkgrey')
        barchart.annotate(f'y = {y_val:.2f}', xy=(barchart.get_xlim()[1] - 1, y_val + 500))
        # recolor the bars
        for i, rect in enumerate(rects):
            total = error.iloc[i] * 2
            low = means.iloc[i] - error.iloc[i]
            p = 1 - (y_val - low) / total
            rect.set_facecolor(cmap(p))

    def show_plot(self):
        """
        Opens a window with the interactive plot
        :return:
        """
        plt.gcf().canvas.mpl_connect('button_press_event',
                                     lambda event: self.on_click(event,
                                                                 self.barchart,
                                                                 self.rects,
                                                                 self.means,
                                                                 self.error,
                                                                 self.cmap))
        plt.show()


def main():
    processed_data = MeansAndIntervals()
    my_chart = InteractiveBarChart(processed_data.means, processed_data.error, get_cmap('seismic'))

    my_chart.show_plot()


if __name__ == '__main__':
    main()
