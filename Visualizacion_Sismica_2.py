# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 22:46:15 2023

@author: Alejandro
"""
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import scrolledtext
from segysak.segy import get_segy_texthead, segy_loader, segy_header_scan
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import mplcursors
import pandas as pd
import xarray as xr
from segysak import SeisGeom

sismica = None
header_data = None
header_text = None
seis_geom = None

def open_segy_file():
    global sismica, header_data, header_text, seis_geom
    sismica = askopenfilename(filetypes=[("SEGY files", "*.segy;*.sgy")])
    header_data = segy_header_scan(sismica)
    header_text = get_segy_texthead(sismica)
    seis_geom = segy_loader(sismica).seis

def show_header():
    header_window = tk.Toplevel(root)
    header_window.title("Análisis del Header")

    header_text_widget = tk.Text(header_window)
    header_text_widget.pack()
    header_text_widget.insert(tk.END, header_text)

    header_data_frame = pd.DataFrame(header_data)
    
    header_data_frame_widget = scrolledtext.ScrolledText(header_window, width=100, height=30)
    header_data_frame_widget.insert(tk.END, header_data_frame.to_string())
    header_data_frame_widget.pack(fill=tk.BOTH, expand=True)

def show_params():
    global params_window
    params_window = tk.Toplevel(root)
    params_window.title("Parámetros de la Sísmica")

    inline_label = tk.Label(params_window, text="Primer byte Inline:")
    inline_label.pack()
    inline_entry = tk.Entry(params_window)
    inline_entry.pack()

    xline_label = tk.Label(params_window, text="Primer byte Xline:")
    xline_label.pack()
    xline_entry = tk.Entry(params_window)
    xline_entry.pack()

    xcoord_label = tk.Label(params_window, text="Primer byte de X coordinate:")
    xcoord_label.pack()
    xcoord_entry = tk.Entry(params_window)
    xcoord_entry.pack()

    ycoord_label = tk.Label(params_window, text="Primer byte de Y coordinate:")
    ycoord_label.pack()
    ycoord_entry = tk.Entry(params_window)
    ycoord_entry.pack()

    domain_label = tk.Label(params_window, text="Dominio (TWT or DEPTH):")
    domain_label.pack()
    domain_entry = tk.Entry(params_window)
    domain_entry.pack()

    params_button = tk.Button(
        params_window,
        text="Guardar Parámetros",
        command=lambda: save_params(
            inline_entry.get(),
            xline_entry.get(),
            xcoord_entry.get(),
            ycoord_entry.get(),
            domain_entry.get(),
        ),
    )
    params_button.pack()

def save_params(inline, xline, xcoord, ycoord, domain):
    global sismica, inline_value, xline_value, xcoord_value, ycoord_value, domain_value
    sismica = segy_loader(
        sismica,
        iline=int(inline),
        xline=int(xline),
        cdpx=int(xcoord),
        cdpy=int(ycoord),
        vert_domain=domain.upper(),
    )
    inline_value = int(inline)
    xline_value = int(xline)
    xcoord_value = int(xcoord)
    ycoord_value = int(ycoord)
    domain_value = domain.upper()
    params_window.destroy()

def show_visualization():
    global visualize_window, section_var, iline_entry, color_var
    visualize_window = tk.Toplevel(root)
    visualize_window.title("Visualización de la Sísmica")

    section_var = tk.StringVar()
    section_var.set("1")
    section_label = tk.Label(
        visualize_window, text="Seleccione si quiere ver una INLINE o XLINE:"
    )
    section_label.pack()
    section_iline_radio = tk.Radiobutton(
        visualize_window, text="INLINE", variable=section_var, value="1"
    )
    section_iline_radio.pack()
    section_xline_radio = tk.Radiobutton(
        visualize_window, text="XLINE", variable=section_var, value="2"
    )
    section_xline_radio.pack()

    iline_label = tk.Label(
        visualize_window, text="Digite la inline o crossline que desea visualizar:"
    )
    iline_label.pack()
    iline_entry = tk.Entry(visualize_window)
    iline_entry.pack()

    color_var = tk.StringVar()
    color_var.set("1")
    color_label = tk.Label(
        visualize_window,
        text="Determine la escala de colores en la cual visualizar la sismica:",
    )
    color_label.pack()
    color_default_radio = tk.Radiobutton(
        visualize_window, text="Default", variable=color_var, value="1"
    )
    color_default_radio.pack()
    color_rdgy_radio = tk.Radiobutton(
        visualize_window, text="Rojo y Negro", variable=color_var, value="2"
    )
    color_rdgy_radio.pack()
    color_rdylbu_radio = tk.Radiobutton(
        visualize_window, text="Rojo y azul", variable=color_var, value="3"
    )
    color_rdylbu_radio.pack()
    color_viridis_radio = tk.Radiobutton(
        visualize_window, text="Viridis", variable=color_var, value="4"
    )
    color_viridis_radio.pack()
    color_greys_radio = tk.Radiobutton(
        visualize_window, text="Greys", variable=color_var, value="5"
    )
    color_greys_radio.pack()

    visualize_button = tk.Button(
        visualize_window, text="Generar gráfico", command=generate_graph
    )
    visualize_button.pack()

def generate_graph():
    global visualize_window
    visualize_window.withdraw()  # Ocultar la ventana de opciones de personalización

    graph_window = tk.Toplevel(root)
    graph_window.title("Gráfico de la Sismica")

    fig = plt.Figure()
    canvas = FigureCanvasTkAgg(fig, master=graph_window)
    canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)  # Rellenar todo el espacio disponible

    toolbar = NavigationToolbar2Tk(canvas, graph_window)
    toolbar.update()
    toolbar.pack()

    section = int(section_var.get())
    line = int(iline_entry.get())
    color = int(color_var.get())

    if section == 1:
        section_label = "iline"
    elif section == 2:
        section_label = "xline"
    else:
        print("Ha digitado un numero incorrecto")
        graph_window.destroy()
        visualize_window.deiconify()
        return

    if color == 1:
        cmap = "seismic"
    elif color == 2:
        cmap = "RdGy"
    elif color == 3:
        cmap = "RdYlBu"
    elif color == 4:
        cmap = "viridis"
    elif color == 5:
        cmap = "Greys"
    else:
        print("No escogió la escala de colores")
        graph_window.destroy()
        visualize_window.deiconify()
        return

    # Crear los subplots para la sismica y los límites de la encuesta
    ax_seismic = fig.add_subplot(111)
    ax_bounds = fig.add_axes([0.16, 0.17, 0.13, 0.13])

    ax_seismic.clear()
    seis_data = sismica.data.transpose("twt", "iline", "xline", transpose_coords=True).sel(
        **{section_label: line}
    )
    seis_data.plot(yincrease=False, cmap=cmap, ax=ax_seismic)
    ax_seismic.grid("k", linewidth=2)
    ax_seismic.set_ylabel("TWT (ms)", fontsize=12)
    ax_seismic.set_xlabel("XLINE" if section_label == "iline" else "INLINE", fontsize=12)
    ax_seismic.set_title(
        f"Gráfico de la Sismica\n{section_label.upper()} {line}",
        fontsize=14,
        fontweight="bold",
    )
    mplcursors.cursor(hover=True)

    ax_bounds.clear()
    seis_geom = SeisGeom(sismica)
    seis_geom.plot_bounds(ax=ax_bounds)
    ax_bounds.grid(True, linewidth=0.5, linestyle='--', color='gray')
    ax_bounds.set_xlabel("CDP X")
    ax_bounds.set_ylabel("CDP Y")
    ax_bounds.set_title("Perímetro de la Sismica", fontsize=12, fontweight="bold")

    # Agregar rosa de los vientos
    ax_bounds.text(0.85, 0.85, "N", horizontalalignment='center', verticalalignment='center', transform=ax_bounds.transAxes, fontsize=11, fontweight='bold')
    ax_bounds.text(0.85, 0.65, "S", horizontalalignment='center', verticalalignment='center', transform=ax_bounds.transAxes, fontsize=11, fontweight='bold')
    ax_bounds.text(0.8, 0.75, "W", horizontalalignment='center', verticalalignment='center', transform=ax_bounds.transAxes, fontsize=11, fontweight='bold')
    ax_bounds.text(0.9, 0.75, "E", horizontalalignment='center', verticalalignment='center', transform=ax_bounds.transAxes, fontsize=11, fontweight='bold')

    canvas.draw()

# Crear una ventana de Tkinter
root = tk.Tk()
root.geometry("400x400")

# Botón para abrir el archivo SEGY
open_segy_button = tk.Button(
    root, text="Abrir archivo SEGY", command=open_segy_file
)
open_segy_button.pack()

# Botón para ver el encabezado
show_header_button = tk.Button(
    root, text="Ver encabezado", command=show_header
)
show_header_button.pack()

# Botón para mostrar los parámetros de la sismica
show_params_button = tk.Button(
    root, text="Parámetros de la Sísmica", command=show_params
)
show_params_button.pack()

# Botón para visualizar la sismica
visualize_button = tk.Button(
    root, text="Visualizar sismica", command=show_visualization
)
visualize_button.pack()

# Mantener la ventana principal abierta
root.mainloop()
