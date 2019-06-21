import random
from typing import List
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, Colormap
from scipy.interpolate import griddata

plt.style.use('seaborn-white')
import numpy as np
import math
import pandas as pd
import seaborn as sns
from pyspec.loader import Spectra


class Encoder:
    """
    class to easily encode spectra into a graphical form, to be used for machine learning
    """

    def __init__(self, width=512, height=512, min_mz=0, max_mz=2000, plot_axis=False, intensity_max=1000):
        """
            inits the encoder with some standard settings
        """
        self.width = width
        self.height = height
        self.min_mz = min_mz
        self.max_mz = max_mz
        self.axis = plot_axis
        self.intensity_max = intensity_max

    def encode(self, spec: Spectra):
        # dumb approach to find max mz

        data = []

        pairs = spec.spectra.split(" ")

        # convert spectra to arrays
        for pair in pairs:
            mass, intensity = pair.split(":")

            frac, whole = math.modf(float(mass))

            data.append(
                {
                    "intensity": float(intensity),
                    "mz": float(mass),
                    "nominal": int(whole),
                    "frac": round(float(frac), 4)
                }
            )

        dataframe = pd.DataFrame(data, columns=["intensity", "mz", "nominal", "frac"])

        # group by 5 digits
        dataframe = dataframe.groupby(dataframe['mz'].apply(lambda x: round(x, 5))).sum()

        # drop data outside min and max
        dataframe = dataframe[(dataframe['nominal'] >= self.min_mz) & (dataframe['nominal'] <= self.max_mz)]

        dataframe['intensity_min_max'] = (dataframe['intensity'] - dataframe['intensity'].min()) / (
                dataframe['intensity'].max() - dataframe['intensity'].min())

        # formatting
        fig = plt.figure(constrained_layout=True)

        widths = [1]
        heights = [16, 16, 1]
        specs = fig.add_gridspec(ncols=len(widths), nrows=len(heights), width_ratios=widths, height_ratios=heights)

        ax0 = plt.subplot(specs[0, 0])
        ax1 = plt.subplot(specs[1, 0])
        ax2 = plt.subplot(specs[2, 0])

        ax0.scatter(dataframe['nominal'], dataframe['frac'], c=dataframe['intensity_min_max'], vmin=0, vmax=1, s=2)
        ax0.set_xlim(self.min_mz, self.max_mz)
        ax0.set_ylim(0, 1)

        ax1.stem(dataframe['mz'], dataframe['intensity_min_max'], markerfmt=' ', linefmt='black')
        ax1.set_xlim(self.min_mz, self.max_mz)
        ax1.set_ylim(0, 1)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)

        ax2.barh("intensity", dataframe['intensity'].max(), align='center',color='black')
        ax2.set_xlim(0, self.intensity_max)

        if not axis:
            ax0.axis('off')
            ax1.axis('off')
            ax2.axis('off')

        plt.tight_layout()
        plt.show()
        return plt

    def encodes(self, spectra: List[Spectra],directory:str="data"):
        """
        encodes a spectra as picture. Conceptually wise
        we will render 3 dimensions

        x is MZ as nominal
        y is MZ as accurate
        z is intensity between 0 and 100
        :param spectra:
        :return:
        """
        from splash import Spectrum, SpectrumType, Splash

        import pathlib
        pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
        for spec in spectra:
            plt = self.encode(spec)
            name = Splash().splash(Spectrum(spec.spectra, SpectrumType.MS))
            plt.savefig("{}/{}.png".format(directory, name))