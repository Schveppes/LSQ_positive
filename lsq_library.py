# -*- coding: utf-8 -*-
"""
Created on Sun Aug 18 14:04:24 2024

@author: schve
"""

# lsq_library.py
import numpy as np
from scipy import interpolate
from scipy.optimize import nnls
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class LSQAnalyzer:
    def __init__(self, x_lsq_range, x_model_range):
        self.x_lsq = np.arange(*x_lsq_range)
        self.x_model = np.arange(*x_model_range)
        self.data = {}
        self.results = {}

    def load_and_process(self, filename, tag):
        input_data = np.loadtxt(filename)
        x_data = input_data[:, 0]
        y_data = input_data[:, 1]
    
        x_lsq = np.clip(self.x_lsq, x_data.min(), x_data.max())
        x_model = np.clip(self.x_model, x_data.min(), x_data.max())
    
        lsq = interpolate.interp1d(x_data, y_data, kind='cubic', bounds_error=False, fill_value="extrapolate")(x_lsq)
        model = interpolate.interp1d(x_data, y_data, kind='cubic', bounds_error=False, fill_value="extrapolate")(x_model)
    
        self.data[tag] = {'lsq': lsq, 'model': model, 'filename': filename}

    def perform_lsq(self, base, *calc_spectra):
        calc_data = np.column_stack([self.data[calc]['lsq'] for calc in calc_spectra])
        result = nnls(calc_data, self.data[base]['lsq'])[0]
        coeff = result / sum(result) * 100
        model = sum(r * self.data[c]['model'] for r, c in zip(result, calc_spectra))
        key = f"{base}|||{'|||'.join(calc_spectra)}"
        self.results[key] = {'lsq': result, 'coeff': coeff, 'model': model}

    def save_results(self, filename):
        output = np.column_stack([self.x_model] + 
                                 [self.data[tag]['model'] for tag in self.data] + 
                                 [self.results[key]['model'] for key in self.results])
        header = ' '.join(['x_model'] + list(self.data.keys()) + list(self.results.keys()))
        np.savetxt(filename, output, header=header, comments='')
        
    def plot_results(self):
        num_results = len(self.results)
        fig, axes = plt.subplots(num_results, 1, figsize=(8, 5 * num_results), squeeze=False)
    
        for i, (ax, (key, result)) in enumerate(zip(axes.flatten(), self.results.items()), 1):
            parts = key.split('|||')
            base, _ = parts[0], parts[1:]
            ax.plot(self.x_model, self.data[base]['model'], 'b', label=f"Целевой спектр: {base}")
            ax.plot(self.x_model, result['model'], 'r', label='Модельный спектр (LSQ)')
            ax.set_title(f"Сравнение {i}: {base} и LSQ модель")
            ax.legend()
    
        plt.tight_layout()
        return fig