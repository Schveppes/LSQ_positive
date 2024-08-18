# -*- coding: utf-8 -*-
"""
Created on Sun Aug 18 14:04:02 2024

@author: schve
"""

# gui.py
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from lsq_library import LSQAnalyzer
import numpy as np


class LSQGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("МНК+ анализатор")
        self.master.geometry("1200x800")
        self.master.configure(bg='#e6e6e6')
        self.analyzer = None
        
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_rowconfigure(0, weight=1)
        
        self.create_widgets()
        self.master.bind('<Configure>', self.update_layout)
        self.create_widgets()
        self.update_calculate_button_state()

    def create_widgets(self):
        # Создание стиля для ttk виджетов
        style = ttk.Style()
        style.configure('TLabel', background='#e6e6e6', font=('Helvetica', 10))
        style.configure('TButton', font=('Helvetica', 10))
        style.configure('TEntry', font=('Helvetica', 10))
        style.configure('TFrame', background='#e6e6e6')
    
        # Основная рамка
        main_frame = ttk.Frame(self.master, padding="10 10 10 10")
        main_frame.grid(row=0, column=0, sticky='nsew')
    
        # Секция настроек диапазона
        range_frame = ttk.LabelFrame(main_frame, text="Настройки диапазона", padding="10 10 10 10")
        range_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        
        ttk.Label(range_frame, text="Начало:").grid(row=0, column=0, sticky='w')
        self.start_var = tk.StringVar(value="72")
        ttk.Entry(range_frame, textvariable=self.start_var).grid(row=0, column=1, padx=5)
    
        ttk.Label(range_frame, text="Конец:").grid(row=1, column=0, sticky='w')
        self.end_var = tk.StringVar(value="106.1")
        ttk.Entry(range_frame, textvariable=self.end_var).grid(row=1, column=1, padx=5)
    
        ttk.Label(range_frame, text="Шаг:").grid(row=2, column=0, sticky='w')
        self.step_var = tk.StringVar(value="0.1")
        ttk.Entry(range_frame, textvariable=self.step_var).grid(row=2, column=1, padx=5)
    
        # Секция загрузки файлов
        file_frame = ttk.LabelFrame(main_frame, text="Загрузить файлы", padding="10 10 10 10")
        file_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
    
        self.file_listbox = tk.Listbox(file_frame, width=70, height=10)
        self.file_listbox.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        ttk.Button(file_frame, text="Добавить файл", command=self.add_file).grid(row=1, column=0, pady=5)
        ttk.Button(file_frame, text="Удалить файл", command=self.remove_file).grid(row=1, column=1, pady=5)
    
        # Секция сравнения
        comp_frame = ttk.LabelFrame(main_frame, text="Сравнение", padding="10 10 10 10")
        comp_frame.grid(row=2, column=0, sticky='ew', padx=5, pady=5)
    
        self.comp_listbox = tk.Listbox(comp_frame, width=70, height=10)
        self.comp_listbox.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        ttk.Button(comp_frame, text="Добавить сравнение", command=self.add_comparison).grid(row=1, column=0, pady=5)
        ttk.Button(comp_frame, text="Удалить сравнение", command=self.remove_comparison).grid(row=1, column=1, pady=5)
    
        # Секция анализа и результатов
        ttk.Button(main_frame, text="Выполнить расчет", command=self.perform_analysis).grid(row=3, column=0, pady=10)
    
        # Рамка для текстового вывода и полосы прокрутки
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=4, column=0, padx=5, pady=5, sticky='nsew')
    
        self.result_text = tk.Text(text_frame, width=70, height=15)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
        # Полоса прокрутки для текстового вывода
        text_scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.result_text.yview)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
        # Настройка текстового виджета для использования полосы прокрутки
        self.result_text.configure(yscrollcommand=text_scrollbar.set)
    
        # Секция графиков с прокруткой
        plot_frame = ttk.Frame(self.master)
        plot_frame.grid(row=0, column=1, sticky='nsew')
    
        plot_canvas = tk.Canvas(plot_frame)
        plot_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
        plot_scrollbar = ttk.Scrollbar(plot_frame, orient='vertical', command=plot_canvas.yview)
        plot_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
        plot_canvas.configure(yscrollcommand=plot_scrollbar.set)
    
        self.plot_inner_frame = ttk.Frame(plot_canvas)
        plot_canvas.create_window((0, 0), window=self.plot_inner_frame, anchor='nw')
    
        # Настройка весов колонок
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)  # Установите одинаковый вес для равномерного распределения
        self.master.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(4, weight=1)  # Позволяет текстовой рамке расширяться
    
        # Привязка события конфигурации для обновления области прокрутки
        self.plot_inner_frame.bind("<Configure>", lambda e: plot_canvas.configure(scrollregion=plot_canvas.bbox("all")))
        self.calculate_button = ttk.Button(main_frame, text="Выполнить расчет", command=self.perform_analysis, state='disabled')
        self.calculate_button.grid(row=3, column=0, pady=10)


    def update_layout(self, event=None):
        width = self.master.winfo_width()
        # height = self.master.winfo_height()
        
        self.master.grid_columnconfigure(0, minsize=width//2)
        self.master.grid_columnconfigure(1, minsize=width//2)
        
    def update_calculate_button_state(self):
        if self.comp_listbox.size() > 0:
            self.calculate_button['state'] = 'normal'
        else:
            self.calculate_button['state'] = 'disabled'

    def apply_settings(self):
        """Applies range settings and creates an LSQAnalyzer object"""
        try:
            start = float(self.start_var.get())
            end = float(self.end_var.get())
            step = float(self.step_var.get())
            self.analyzer = LSQAnalyzer((start, end, step), (start, end, step))
            messagebox.showinfo("Успех", "Настройки применены успешно")
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числовые значения")

    def add_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if filename:
            class TagDialog(simpledialog.Dialog):
                def __init__(self, parent, title, existing_tags):
                    self.existing_tags = existing_tags
                    super().__init__(parent, title)
    
                def body(self, master):
                    ttk.Label(master, text="Введите уникальный тег для удобства:").grid(row=0)
                    self.e1 = ttk.Entry(master, width=50)
                    self.e1.grid(row=0, column=1)
                    return self.e1  # initial focus
        
                def validate(self):
                    tag = self.e1.get().strip()
                    if not tag:
                        messagebox.showwarning("Ошибка", "Тег не может быть пустым")
                        return False
                    if tag in self.existing_tags:
                        messagebox.showwarning("Ошибка", "Этот тег уже используется. Пожалуйста, выберите другой.")
                        return False
                    self.result = tag
                    return True
    
            existing_tags = list(self.analyzer.data.keys()) if self.analyzer else []
            tag_dialog = TagDialog(self.master, "Добавить тег", existing_tags)
            
            if tag_dialog.result:
                tag = tag_dialog.result
                if self.analyzer is None:
                    self.analyzer = LSQAnalyzer((0, 1, 0.1), (0, 1, 0.1))
                
                self.analyzer.data[tag] = {'filename': filename}
                self.file_listbox.insert(tk.END, f"{tag}: {filename}")
            else:
                messagebox.showwarning("Внимание", "Добавление файла отменено")

    def remove_file(self):
        selection = self.file_listbox.curselection()
        if selection:
            tag = self.file_listbox.get(selection).split(":")[0]
            del self.analyzer.data[tag]
            self.file_listbox.delete(selection)

    def add_comparison(self):
        if self.analyzer is None or len(self.analyzer.data) < 2:
            tk.messagebox.showwarning("Внимание", "Должно быть не менее 2-х файлов для сравнения")
            return
        
        top = tk.Toplevel(self.master)
        top.title("Добавить сравнение")
        top.geometry("600x500")
        top.configure(bg='#f0f0f0')
        
        # Create a style for ttk widgets within the popup
        style = ttk.Style(top)
        style.configure('Popup.TFrame', background='#f0f0f0')
        style.configure('Popup.TLabel', background='#f0f0f0', font=('Helvetica', 10))
        style.configure('Popup.TButton', font=('Helvetica', 10))
        style.configure('Popup.TCombobox', font=('Helvetica', 10))
    
        main_frame = ttk.Frame(top, style='Popup.TFrame', padding="10 10 10 10")
        main_frame.pack(fill=tk.BOTH, expand=True)
    
        canvas_frame = ttk.Frame(main_frame, style='Popup.TFrame')
        canvas_frame.pack(fill=tk.BOTH, expand=True)
    
        canvas = tk.Canvas(canvas_frame, bg='#f0f0f0')
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
        canvas.configure(yscrollcommand=scrollbar.set)
    
        scrollable_frame = ttk.Frame(canvas, style='Popup.TFrame')
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    
        ttk.Label(scrollable_frame, text="Целевой спектр:", style='Popup.TLabel', font=('Helvetica', 12, 'bold')).grid(row=0, column=0, sticky='w', pady=(0, 10))
        base_var = tk.StringVar(top)
        base_menu = ttk.Combobox(scrollable_frame, textvariable=base_var, values=list(self.analyzer.data.keys()), width=40, style='Popup.TCombobox')
        base_menu.grid(row=0, column=1, sticky='w', pady=(0, 10))
    
        spectrum_frames = []
    
        def add_spectrum():
            index = len(spectrum_frames) + 1
            frame = ttk.Frame(scrollable_frame, style='Popup.TFrame')
            frame.grid(row=index, column=0, columnspan=2, sticky='w', pady=5)
            
            ttk.Label(frame, text=f"Спектр {index}:", style='Popup.TLabel').pack(side=tk.LEFT, padx=(0, 10))
            var = tk.StringVar(top)
            menu = ttk.Combobox(frame, textvariable=var, values=list(self.analyzer.data.keys()), width=40, style='Popup.TCombobox')
            menu.pack(side=tk.LEFT, padx=(0, 10))
            
            def remove_spectrum(f):
                f.destroy()
                spectrum_frames.remove(f)
                update_layout()
            
            remove_button = ttk.Button(frame, text="Удалить", command=lambda f=frame: remove_spectrum(f), style='Popup.TButton')
            remove_button.pack(side=tk.LEFT)
            
            spectrum_frames.append(frame)
            update_layout()
    
        def update_layout():
            for i, frame in enumerate(spectrum_frames, start=1):
                frame.grid(row=i, column=0, columnspan=2, sticky='w', pady=5)
            
            add_spectrum_button.grid(row=len(spectrum_frames) + 1, column=0, columnspan=2, sticky='w', pady=10)
            add_comparison_button.grid(row=len(spectrum_frames) + 2, column=0, columnspan=2, pady=10)
            
            scrollable_frame.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
    
        add_spectrum_button = ttk.Button(scrollable_frame, text="Добавить спектр", command=add_spectrum, style='Popup.TButton')
        add_spectrum_button.grid(row=1000, column=0, columnspan=2, sticky='w', pady=10)
    

        def add():
            spectra = [base_var.get()] + [frame.winfo_children()[1].get() for frame in spectrum_frames if frame.winfo_children()[1].get()]
            if len(spectra) < 2:
                messagebox.showwarning("Внимание", "Выберите как минимум один спектр для сравнения")
                return
            
            # Проверка на уникальность набора
            new_comparison = ", ".join(sorted(spectra))
            existing_comparisons = [", ".join(sorted(item.split(", "))) for item in self.comp_listbox.get(0, tk.END)]
            
            if new_comparison in existing_comparisons:
                messagebox.showwarning("Внимание", "Такое сравнение уже существует")
                return
        
            self.comp_listbox.insert(tk.END, ", ".join(spectra))
            self.update_calculate_button_state()
            top.destroy()
    
        add_comparison_button = ttk.Button(scrollable_frame, text="Добавить сравнение", command=add, style='Popup.TButton')
        add_comparison_button.grid(row=1001, column=0, columnspan=2, pady=10)
    
        add_spectrum()
    
        scrollable_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
    
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
    
        scrollable_frame.bind("<Configure>", on_frame_configure)
    
        top.update_idletasks()
        width = top.winfo_width()
        height = top.winfo_height()
        x = (top.winfo_screenwidth() // 2) - (width // 2)
        y = (top.winfo_screenheight() // 2) - (height // 2)
        top.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def remove_comparison(self):
        selection = self.comp_listbox.curselection()
        if selection:
            self.comp_listbox.delete(selection)
            self.update_calculate_button_state()

    def format_coefficient(self, value):
        if np.isnan(value):
            return "0.00"
        return f"{value:.2f}"


    def perform_analysis(self):
        try:
            start = float(self.start_var.get())
            end = float(self.end_var.get())
            step = float(self.step_var.get())
            
            new_analyzer = LSQAnalyzer((start, end, step), (start, end, step))
            
            for tag, data in self.analyzer.data.items():
                filename = data['filename']
                new_analyzer.load_and_process(filename, tag)
            
            self.analyzer = new_analyzer
            
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числовые значения для настроек диапазона")
            return
    
        if not self.analyzer.data:
            messagebox.showwarning("Внимание", "Сначала загрузите файлы для анализа")
            return
    
        self.analyzer.results.clear()
        for item in self.comp_listbox.get(0, tk.END):
            spectra = item.split(", ")
            base = spectra[0]
            calc_spectra = spectra[1:]
            self.analyzer.perform_lsq(base, *calc_spectra)
    
        self.result_text.delete('1.0', tk.END)
        for i, (key, result) in enumerate(self.analyzer.results.items(), 1):
            parts = key.split('|||')
            base = parts[0]
            calc_spectra = parts[1:]
            self.result_text.insert(tk.END, f"Сравнение {i}, коэффициенты для {base}:\n")
            for i, calc in enumerate(calc_spectra):
                self.result_text.insert(tk.END, f"{calc}: {self.format_coefficient(result['coeff'][i])}%\n")
            self.result_text.insert(tk.END, "\n")
    
        self.analyzer.save_results("output.txt")
        
        fig = self.analyzer.plot_results()
        
        # Clear previous plot widgets
        for widget in self.plot_inner_frame.winfo_children():
            widget.destroy()
        
        # Create new plot widgets
        for i, ax in enumerate(fig.axes):
            plot_frame = ttk.Frame(self.plot_inner_frame)
            plot_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            new_fig, new_ax = plt.subplots(figsize=(8, 6))
            new_ax.plot(*ax.lines[0].get_data(), label=ax.lines[0].get_label())
            new_ax.plot(*ax.lines[1].get_data(), label=ax.lines[1].get_label())
            new_ax.set_title(ax.get_title())
            new_ax.legend()
            new_ax.set_xlabel(ax.get_xlabel())
            new_ax.set_ylabel(ax.get_ylabel())
            
            canvas_widget = FigureCanvasTkAgg(new_fig, master=plot_frame)
            canvas_widget.draw()
            canvas_widget.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            
            toolbar = NavigationToolbar2Tk(canvas_widget, plot_frame)
            toolbar.update()
            toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        plt.close(fig)

if __name__ == "__main__":
    root = tk.Tk()
    app = LSQGUI(root)
    root.mainloop()