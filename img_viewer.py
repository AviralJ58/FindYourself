import PySimpleGUI as sg
import os.path

# Window layout of two columns

file_list_column = [
    [
        sg.Text("Image Viewer"),
        sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 20), key="-FILE-LIST-"
        )
    ],
]

image_column = [
    [sg.Text("Choose an image from list on the left")],
    [sg.Text(size=(40, 1), key="-TOUT-")],
    [sg.Image(filename="", key="-IMAGE-")],
]


#Layout
layout = [
    [
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(image_column),
    ]
]

window = sg.Window("Image Viewer", layout)

# event loop
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == "Exit":
        break

    if event == "-FOLDER-":
        folder = values["-FOLDER-"]
        try:
            file_list = os.listdir(folder)
        except:
            file_list = []
        
        fnames = [
            f
            for f in file_list
            if os.path.isfile(os.path.join(folder, f))
            and f.lower().endswith((".png", ".gif"))
        ]

        window["-FILE-LIST-"].update(fnames)
    elif event == "-FILE-LIST-":
        try:
            filename = os,path.join(
                values["-FOLDER-"], values["-FILE-LIST-"][0]

                    )
            window["-TOUT-"].update(filename)
            window["-IMAGE-"].update(filename)

        except:
            pass
window.close()