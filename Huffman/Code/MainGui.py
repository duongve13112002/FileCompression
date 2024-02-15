import tkinter as tk
from tkinter import *
from tkinter import filedialog
import tkinter.messagebox
from tkinter.filedialog import askopenfile
from PIL import Image, ImageTk
import os
import threading
import time
import csv
import numpy
from zipfile import ZipFile
from PIL import Image, ImageTk
from itertools import count, cycle

import ColoredCompression.ColoredHuffmanMain as chm
import  GrayLevelCompression.GrayHuffmanMain as ghm
import LoadingAnimation as An
import TextCompression.TextLevelCompression as tlg

def upload_file():
    f_types = [('PNG Files','*.png'),('JPG Files','*.jpg'),('BMP Files','*.bmp')]   # type of files to select ('Jpg Files', '*.jpg')
    global filename
    global lastfilename
    filename = tk.filedialog.askopenfilename(multiple=False,filetypes=f_types)
    global original_image
    if(filename==''):
        if('lastfilename' in globals() and lastfilename!=""):
            filename=lastfilename
        else:
            return
    global textfilename
    textfilename=""
    global uploaded_img_label
    uploaded_img=Image.open(filename) # read the image file
    original_image = uploaded_img.copy()
    uploaded_img=uploaded_img.resize((200,200)) # new width & height
    uploaded_img=ImageTk.PhotoImage(uploaded_img)
    uploaded_img_label =Label(my_w,background='bisque')

    x = width / 10
    y = height / 12
    uploaded_img_label.place(x=x/2, y=y*1.7)
    uploaded_img_label.image = uploaded_img
    uploaded_img_label['image']=uploaded_img 

    global input_image_size_label
    lastfilename=filename
    if ("/" in filename):
        name = filename[filename.rindex('/') + 1:len(filename)]
    else:
        name = filename
    input_image_size_label = tk.Label(my_w, text=f"{name}", width=30, font=font,background='bisque')
    input_image_size_label.place(x=x/3, y=y*6+20)

def UploadZip():
    f_types = [('Zip Files','*.zip')]
    global zipfilename
    zipfilename = tk.filedialog.askopenfilename(multiple=False,filetypes=f_types)
    global zip_name_label
    if ("/" in zipfilename):
        name = zipfilename[zipfilename.rindex('/') + 1:len(zipfilename)]
    else:
        name = zipfilename
    zip_name_label = tk.Label(my_w, text=f"{name}",width=30, font=font,background='bisque')
    zip_name_label.place(x=width / 2.8, y=(height/1.5) -20)

def UploadText():
    f_types = [('Text Files','*.txt'),('HTML Files','*.html'),('CSV Files','*.csv')]
    global textfilename
    global text_box
    global lasttextfilename
    global input_image_size_label
    textfilename = tk.filedialog.askopenfilename(multiple=False,filetypes=f_types)
    if(textfilename==''):
        if('lasttextfilename' in globals() and lasttextfilename!=''):
            textfilename=lasttextfilename
        else:
            return

    file = open(textfilename, "r", encoding='utf-8')
    text = file.read()
    text = text.rstrip()
    maxcount = 250
    temptext=text[0:maxcount]
    if(len(text)>maxcount):
        temptext = temptext+ "......."
    text_box = Text(my_w, height=12, width=24)
    text_box.insert(END,f"{temptext}")
    text_box.config(state=DISABLED)
    x = width / 10
    y = height / 12

    lasttextfilename=textfilename
    text_box.place(x=x/2, y=y*1.7)
    if "uploaded_img_label" in globals():
        uploaded_img_label.image = None
        input_image_size_label.config(text="")
        uploaded_img_label['image'] = None
    global filename
    filename = ""

    lasttextfilename=textfilename
    if ("/" in textfilename):
        name = textfilename[textfilename.rindex('/') + 1:len(textfilename)]
    else:
        name = textfilename
    input_image_size_label = tk.Label(my_w, text=f"{name}", width=30, font=font,background='bisque')
    input_image_size_label.place(x=x/3, y=y*6+20)
def TextCompressThread():
    x = width / 10
    y = height / 12
    if 'textfilename' not in globals() or textfilename == '':
        tk.messagebox.showwarning("Compress Text", "Please Upload an Text File Before Compression")
        return

    if ('avg_cleared' in globals()):
        ClearImage()
    if 'decompressed_img_label' in globals():
        decompressed_img_label.image = None
    if ('zip_name_label' in globals()):
        zip_name_label.config(text="")
    if('decompressed_text_box' in globals()):
        decompressed_text_box.destroy()
    switchButtonState(upload_button)
    switchButtonState(decompress_upload_button)
    switchButtonState(text_upload_button)

    switchButtonState(level1compress)
    switchButtonState(level2compress)
    switchButtonState(level3compress)
    switchButtonState(level4compress)
    switchButtonState(level5compress)

    switchButtonState(level1decompress)
    switchButtonState(level2decompress)

    animation_label = Label(my_w,background='bisque')
    animation_label = ToggleAnimation(animation_label, x * 6.5 + 50, y * 1.7 + 50)
    differencevalue_label.config(text="")
    time_decompress.config(text="")
    thread_compression = threading.Thread(target=TextCompress,
                                          args=(animation_label,))
    thread_compression.start()

def TextCompress(animation_label):
    time_start = time.time()
    compressed_name, calculated_values = tlg.RunTextCompression(textfilename)
    time_end = time.time()
    calculated_values.append(time_end-time_start)
    x = width / 10
    y = height / 12
    switchButtonState(upload_button)
    switchButtonState(decompress_upload_button)
    switchButtonState(text_upload_button)

    switchButtonState(level1compress)
    switchButtonState(level2compress)
    switchButtonState(level3compress)
    switchButtonState(level4compress)
    switchButtonState(level5compress)

    switchButtonState(level1decompress)
    switchButtonState(level2decompress)

    animation_label = ToggleAnimation(animation_label)
    ShowCalculatedValues(calculated_values)
    tk.messagebox.showinfo(f"Compress Text",f"Text Has Been Compressed Successfully")

def TextDeCompressThread():
    x = width / 10
    y = height / 12
    if 'zipfilename' not in globals() or zipfilename == '':
        tk.messagebox.showwarning("DeCompress Data", "Please Upload an Zip file to decompress data")
        return

    if ("TXTBinandMap" not in zipfilename):
        tk.messagebox.showwarning("DeCompress Data", "It is not a Text ZIP file! \n"
                                                     "Please Upload an Zip file that contains 'TXTBinandMap'")
        return

    if 'uploaded_img_label' in globals():
        pass

    if('avg_cleared' in globals()):
        ClearImage()
    if 'decompressed_img_label' in globals():
        decompressed_img_label.image = None

    if('decompressed_text_box' in globals()):
        decompressed_text_box.destroy()

    switchButtonState(upload_button)
    switchButtonState(decompress_upload_button)
    switchButtonState(text_upload_button)

    switchButtonState(level1compress)
    switchButtonState(level2compress)
    switchButtonState(level3compress)
    switchButtonState(level4compress)
    switchButtonState(level5compress)

    switchButtonState(level1decompress)
    switchButtonState(level2decompress)

    animation_label = Label(my_w,background='bisque')
    animation_label=ToggleAnimation(animation_label,x * 6.5 + 50,y * 1.7 + 50)
    differencevalue_label.config(text="")
    time_decompress.config(text="")

    thread_decompression = threading.Thread(target=TextDeCompression, args=(animation_label, ))
    thread_decompression.start()

def TextDeCompression(animation_label):
    extension = zipfilename[len(zipfilename) - 4:len(zipfilename)]
    name_without_extension = ""
    if ("/" in zipfilename):
        name_without_extension = zipfilename[zipfilename.rindex('/') + 1:zipfilename.index(extension)] + '_'
    else:
        name_without_extension = zipfilename[0:zipfilename.index(extension)] + '_'

    path = zipfilename[0:len(zipfilename) - len(name_without_extension) - len(extension) + 1]
    name_without_extension = name_without_extension.replace("_TXTBinandMap", "")
    start_time = time.time()
    decompressed_text,extention = tlg.DecodeData(f"{path}{name_without_extension}",f"{name_without_extension}", True)
    end_time = time.time()
    first_text_path = f"{path}{name_without_extension}"
    first_text_path = first_text_path[0:len(first_text_path) - 1] + extention
    try:
        f = open(first_text_path, "r", encoding='utf-8')
        first_text = f.read()
        first_text = first_text.rstrip()
        differencevalue = abs(len(decompressed_text)-len(first_text))
        length_text = 0
        if len(decompressed_text) > len(first_text):
            length_text = len(first_text)
        else:
            length_text = len(decompressed_text)
        for i in range(0,length_text):
            if abs(ord(decompressed_text[i])-ord(first_text[i])) > 0:
                differencevalue +=1
    except:
        differencevalue = -1

    global time_for_decompress
    time_for_decompress =  end_time-start_time 
    global decompressed_text_box
    text = decompressed_text
    text = text.rstrip()
    maxcount = 250
    temptext=text[0:maxcount]
    if(len(text)>maxcount):
        temptext = temptext+ "......."
    decompressed_text_box = Text(my_w, height=12, width=24)
    decompressed_text_box.insert(END,f"{temptext}")
    decompressed_text_box.config(state=DISABLED)
    x = width / 10
    y = height / 12

    decompressed_text_box.place(x=x * 6.5, y=y * 1.7)
    ClearImage()
    if differencevalue == -1:
        differencevalue_label.config(text=f"Can not find the original file to compare")
    else:
        differencevalue_label.config(text=f"Difference = {differencevalue}")   
    time_decompress.config(text=f"Execution time = {round(time_for_decompress,2)}s")
    differencevalue_label.place(x=x * 7, y=y * 6+25)
    time_decompress.place(x=x * 7, y=y * 6+45)

    switchButtonState(upload_button)
    switchButtonState(decompress_upload_button)
    switchButtonState(text_upload_button)

    animation_label = ToggleAnimation(animation_label)

    switchButtonState(level1compress)
    switchButtonState(level2compress)
    switchButtonState(level3compress)
    switchButtonState(level4compress)
    switchButtonState(level5compress)

    switchButtonState(level1decompress)
    switchButtonState(level2decompress)
    tk.messagebox.showinfo(f"DeCompress Data", f"Data has been converted to text sucessfully!")

def CreateScreen(window_width,window_height):
    screen_width = my_w.winfo_screenwidth()
    screen_height = my_w.winfo_screenheight()
    position_top = int(screen_height / 2 - window_height / 2)
    position_right = int(screen_width / 2 - window_width / 2)
    my_w.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

def CreateLabels(width,height):
   pass

def CreateButtons(width,height):
    upload_button.place(x=width / 2.55, y=height / 7)
    decompress_upload_button.place(x=width / 2.55, y=(height/1.5))
    text_upload_button.place(x=width / 2.55, y=(height/7)+30)
def switchButtonState(button):
    if (button['state'] == tk.NORMAL):
        button['state'] = tk.DISABLED
    else:
        button['state'] = tk.NORMAL

def CompressionThread(color_of_compression,process_method_of_image):
    x = width / 10
    y = height / 12
    if 'filename' not in globals() or filename=='':
       tk.messagebox.showwarning("Compress Image", "Please Upload an Image Before Compression")
       return
    if('avg_cleared' in globals()):
        ClearImage()
    if 'decompressed_img_label' in globals():
        decompressed_img_label.image = None
    if('zip_name_label' in globals()):
        zip_name_label.config(text="")
    if('decompressed_text_box' in globals()):
        decompressed_text_box.destroy()
    switchButtonState(upload_button)
    switchButtonState(decompress_upload_button)
    switchButtonState(text_upload_button)

    switchButtonState(level1compress)
    switchButtonState(level2compress)
    switchButtonState(level3compress)
    switchButtonState(level4compress)
    switchButtonState(level5compress)

    switchButtonState(level1decompress)
    switchButtonState(level2decompress)

    animation_label = Label(my_w,background='bisque')
    animation_label=ToggleAnimation(animation_label,x * 6.5 + 50,y * 1.7 + 50)
    differencevalue_label.config(text="")
    time_decompress.config(text="")
    thread_compression = threading.Thread(target=Compression,args=(animation_label,color_of_compression,process_method_of_image))
    thread_compression.start()

def DeCompressionThread():
    x = width / 10
    y = height / 12
    if 'zipfilename' not in globals() or zipfilename == '':
        tk.messagebox.showwarning("DeCompress Data", "Please Upload an Zip file to decompress data")
        return

    if ("BinaryandDictionary" not in zipfilename):
        tk.messagebox.showwarning("DeCompress Data", "It is not a Image ZIP file! \n"
                                                     "Please Upload an Zip file that contains 'BinaryandDictionary'")
        return

    if 'uploaded_img_label' in globals():
        pass

    if('avg_cleared' in globals()):
        ClearImage()
    if 'decompressed_img_label' in globals():
        decompressed_img_label.image = None
    if('decompressed_text_box' in globals()):
        decompressed_text_box.destroy()
    switchButtonState(upload_button)
    switchButtonState(decompress_upload_button)
    switchButtonState(text_upload_button)

    switchButtonState(level1compress)
    switchButtonState(level2compress)
    switchButtonState(level3compress)
    switchButtonState(level4compress)
    switchButtonState(level5compress)

    switchButtonState(level1decompress)
    switchButtonState(level2decompress)

    animation_label = Label(my_w,background='bisque')
    animation_label=ToggleAnimation(animation_label,x * 6.5 + 50,y * 1.7 + 50)
    differencevalue_label.config(text="")
    time_decompress.config(text="")
    thread_decompression = threading.Thread(target=DeCompression,args=(animation_label, ))
    thread_decompression.start()

def DeCompression(animation_label):
    extension = zipfilename[len(zipfilename) - 4:len(zipfilename)]
    name_without_extension = ""
    if ("/" in zipfilename):
        name_without_extension = zipfilename[zipfilename.rindex('/') + 1:zipfilename.index(extension)] +'_'
    else:
        name_without_extension = zipfilename[0:zipfilename.index(extension)] +'_'

    path = zipfilename[0:len(zipfilename) - len(name_without_extension) - len(extension) + 1]
    name_without_extension = name_without_extension.replace("BinaryandDictionary_","")

    color_type, process_type,ext_type = ReadTypes(zipfilename,f"{name_without_extension}",path)
    start_time = time.time()
    if color_type == "Colored" :
        decompressed_img = chm.DecodeCompressedFile(f"{path}{name_without_extension}", process_type,f"{name_without_extension}",True)
    elif color_type == "Gray" :
        decompressed_img = ghm.DecodeCompressedFile(f"{path}{name_without_extension}", process_type,f"{name_without_extension}", True)

    end_time = time.time()
    global time_for_decompress
    time_for_decompress = end_time - start_time
    first_image_path = f"{path}{name_without_extension}"
    first_image_path = first_image_path[0:len(first_image_path)-1]+ext_type
    differencevalue = ComputeDifference(decompressed_img,first_image_path)

    decompressed_img=decompressed_img.resize((200,200)) # new width & height
    decompressed_img=ImageTk.PhotoImage(decompressed_img)
    global decompressed_img_label
    decompressed_img_label =Label(my_w,background='bisque')

    x = width / 10
    y = height / 12


    decompressed_img_label.place(x=x*6.5, y=y*1.7)
    decompressed_img_label.image = decompressed_img
    decompressed_img_label['image']=decompressed_img 
    ClearImage()
    if differencevalue == -1:
        differencevalue_label.config(text=f"Can not find the original file to compare")
    else:
        differencevalue_label.config(text=f"Difference = {differencevalue}") 
    time_decompress.config(text=f"Execution time = {round(time_for_decompress,2)}s")
    differencevalue_label.place(x=x*7, y=y * 6+25)
    time_decompress.place(x=x*7, y=y*6+45)
    switchButtonState(upload_button)
    switchButtonState(decompress_upload_button)
    switchButtonState(text_upload_button)
    animation_label=ToggleAnimation(animation_label)

    switchButtonState(level1compress)
    switchButtonState(level2compress)
    switchButtonState(level3compress)
    switchButtonState(level4compress)
    switchButtonState(level5compress)

    switchButtonState(level1decompress)
    switchButtonState(level2decompress)
    tk.messagebox.showinfo(f"DeCompress Data", f"Data has been converted to image sucessfully! \n Color:{color_type} \n Method:{process_type}")


def ReadTypes(zipfilename,name,path):
    zipObj = ZipFile(zipfilename, 'r')
    zipObj.extract(f'{name}dictionary.csv', f'{path}')
    with open(f'{path}{name}dictionary.csv') as csv_file:
        csv_reader = csv.reader(csv_file)
        csvlist = list(csv_reader)
        color = (csvlist[0][3])
        method = (csvlist[0][4])
        extension = (csvlist[0][5])
    os.remove(f'{path}{name}dictionary.csv')
    return color,method,extension

def SelectedColor(preference):
    global color_of_compression
    color_of_compression=None
    if(preference=="Colored"):
        color_of_compression="Colored"
    else:
        color_of_compression="Gray"

def SelectedMethod(preference):
    global process_method_of_image
    process_method_of_image=None
    if(preference=="Difference"):
        process_method_of_image="Difference"
    else:
        process_method_of_image="Standard"

def Compression(animation_label,color_of_compression,process_method_of_image):
    time_start = time.time()
    if(color_of_compression=="Colored"):
        compressed_img,compressed_name,calculated_values = chm.RunColoredCompression(filename,process_method_of_image)
    else:
        compressed_img, compressed_name, calculated_values = ghm.RunGrayCompression(filename,process_method_of_image)
    time_end = time.time()
    calculated_values.append(time_end-time_start)
    x = width / 10
    y = height / 12

    switchButtonState(upload_button)
    switchButtonState(decompress_upload_button)
    switchButtonState(text_upload_button)
    switchButtonState(level1compress)
    switchButtonState(level2compress)
    switchButtonState(level3compress)
    switchButtonState(level4compress)
    switchButtonState(level5compress)

    switchButtonState(level1decompress)
    switchButtonState(level2decompress)

    animation_label=ToggleAnimation(animation_label)
    ShowCalculatedValues(calculated_values)
    tk.messagebox.showinfo(f"Compress Image", f"Image Has Been Compressed Successfully \n Color:{color_of_compression} \n Method:{process_method_of_image}")
def ShowCalculatedValues(values):
    x = width / 15
    y = height / 1.6
    avg_label = tk.Label(my_w,text= f"Average Length = {values[0]:.3f} bits/symbol",width=30, justify=LEFT,anchor="w",font=font,background='bisque')
    entrophy_label = tk.Label(my_w,text= f"Entropy(H) = {values[1]:.3f} bits/symbol",width=30, justify=LEFT,anchor="w", font=font,background='bisque')
    ratio_label = tk.Label(my_w,text= f"Compression Rate = {round(100*values[2],2)}%",width=30, justify=LEFT,anchor="w", font=font,background='bisque')
    before_comp_lable = tk.Label(my_w,text= f"Before Compression = {values[3]} bits", justify=LEFT,anchor="w",width=30, font=font,background='bisque')
    after_comp_lable = tk.Label(my_w,text= f"After Compression = {values[4]} bits", justify=LEFT,anchor="w",width=30, font=font,background='bisque')
    time_excute_compress = tk.Label(my_w,text= f"Execution time = {round(values[5],2)}s", justify=LEFT,anchor="w",width=30, font=font,background='bisque')

    avg_label.place(x=width / 1.4,y=y-240)
    entrophy_label.place(x=width / 1.4, y=y-210)
    ratio_label.place(x=width / 1.4, y=y-180)
    before_comp_lable.place(x=width / 1.4, y=y-150)
    after_comp_lable.place(x=width / 1.4, y=y-120)
    time_excute_compress.place(x=width / 1.4, y=y-90)
    ClearQueue(avg_label,entrophy_label,ratio_label,before_comp_lable,after_comp_lable,time_excute_compress)

def ToggleAnimation(image_label,x=0,y=0):

   if(not hasattr(image_label,'frames')):
       image_label.config(background='bisque')
       image_label = An.AnimationGui()
       image_label.pack()
       image_label.load('LoadingGif/loading.gif')
       image_label.place(x=x,y=y)
   else:
       image_label.unload()

   return  image_label

def ClearQueue(avg_label,entrophy_label,ratio_label,before_comp_lable,after_comp_lable,time_excute_compress):
    global avg_cleared
    global entrophy_cleared
    global ratio_cleared
    global before_comp_cleared
    global after_comp_cleared
    global time_excute_compress_cleared
    avg_cleared=avg_label
    entrophy_cleared=entrophy_label
    ratio_cleared=ratio_label
    before_comp_cleared=before_comp_lable
    after_comp_cleared=after_comp_lable
    time_excute_compress_cleared = time_excute_compress

def ClearImage():
    if ('avg_cleared' not in globals()):
        return
    avg_cleared.config(text="")
    entrophy_cleared.config(text="")
    ratio_cleared.config(text="")
    before_comp_cleared.config(text="")
    after_comp_cleared.config(text="")
    time_excute_compress_cleared.config(text="")

def InitializeComponents():
   global radio_button_colored
   global radio_button_gray
   global radio_button_difference
   global radio_button_standard
   global differencevalue_label
   global time_decompress
   differencevalue_label = tk.Label(my_w,  justify=LEFT, anchor="w", width=30,
                                    font=('times', 8, 'bold'),background='bisque')
   time_decompress = tk.Label(my_w,  justify=LEFT, anchor="w", width=30,
                                    font=('times', 8, 'bold'),background='bisque')

   SelectedColor("Colored")
   SelectedMethod("Difference")
   radio_button_colored = tkinter.Radiobutton(text='Colored',font=font, variable=1, value=1,
                                              command=lambda: SelectedColor("Colored"))
   radio_button_gray = tkinter.Radiobutton(text='Gray',font=font, variable=1, value=2,
                                           command=lambda: SelectedColor("Gray"))
   radio_button_colored.select()

   radio_button_difference = tkinter.Radiobutton(text='Difference',font=font, variable=2, value=1,
                                              command=lambda: SelectedMethod("Difference"))
   radio_button_standard = tkinter.Radiobutton(text='Standard',font=font, variable=2, value=2,
                                           command=lambda: SelectedMethod("Standard"))
   radio_button_difference.select()

   run_once = (lambda:None)

def on_closing():
    if  tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
        my_w.destroy()

def ComputeDifference(decompressed_img,filename):
    try:
        input_image = Image.open(filename)
    except:
        return -1
    input_image_array = numpy.array(input_image)
    output_image_array = numpy.array(decompressed_img)
    inputcolor=""
    outputcolor=""
    if(numpy.isscalar(input_image_array[0][0])):
        inputcolor="Gray"
    else:
        inputcolor="Colored"
    if (numpy.isscalar(output_image_array[0][0])):
        outputcolor = "Gray"
        input_image = input_image.convert('L')
        input_image_array = numpy.array(input_image)
        inputcolor="Gray"
    else:
        if(inputcolor=="Gray"):
            decompressed_img=decompressed_img.convert('L')
            output_image_array=numpy.array(decompressed_img)
            outputcolor="Gray"
        else:
            outputcolor="Colored"
    diff = 0
    if(outputcolor=="Colored" and inputcolor=="Colored"):
        for i in range(len(input_image_array)):
            for j in range(len(input_image_array[i])):
                for k in range(0,3):
                    if pow((input_image_array[i][j][k]-output_image_array[i][j][k]),2) >0:
                        diff +=1
        return diff
    if(outputcolor=="Gray" and inputcolor=="Gray"):
        for i in range(len(input_image_array)):
            for j in range(len(input_image_array[i])):
                if pow((input_image_array[i][j]-output_image_array[i][j]),2) >0: 
                    diff +=1
        return diff
    return -1

def ColorButtons():
    global btn2
    global btn3
    global btn4
    global btn5
    x = width / 10
    y = height / 12
    btn2 = tk.Button(my_w, text='Grayscale', bg='gray', font=font,width=10)
    btn2.place(x=x/30, y=y/30)
    btn2['command'] = lambda: display_in_grayscale()
    # create and place the third button that shows the red channel of the image
    btn3 = tk.Button(my_w, text='Red', bg='red', font=font, width=10)
    btn3.place(x=x*1.1, y=y/30)
    btn3['command'] = lambda: display_color_channel('red')
    # create and place the third button that shows the green channel of the image
    btn4 = tk.Button(my_w, text='Green', bg='SpringGreen2', font=font,width=10)
    btn4.place(x=x*2.2, y=y/30)
    btn4['command'] = lambda: display_color_channel('green')
    # create and place the third button that shows the blue channel of the image
    btn5 = tk.Button(my_w, text='Blue', bg='DodgerBlue2', font=font,width=10)
    btn5.place(x=x*3.2, y=y/30)
    btn5['command'] = lambda: display_color_channel('blue')

    btn6 = tk.Button(my_w, text='Colored', bg="Yellow",font=font,width=10)
    btn6.place(x=x*4.2, y=y/30)
    btn6['command'] = lambda: reset_color()
def reset_color():
    if ('filename' not in globals() or filename == ''):
        return

    img_rgb = Image.open(filename)
    img_rgb = img_rgb.resize((193, 193))
    img = ImageTk.PhotoImage(image=img_rgb)
    uploaded_img_label.config(image=img)
    uploaded_img_label.photo_ref = img
def display_in_grayscale():
   if('filename' not in globals() or filename==''):
       return

   img_rgb = Image.open(filename)
   img_grayscale = img_rgb.convert('L')
   width, height = img_rgb.size
   img_rgb_array = numpy.array(img_rgb)
   width, height = img_grayscale.size
   img_grayscale_array = numpy.array(img_grayscale)
   img_grayscale = img_grayscale.resize((193, 193))
   img = ImageTk.PhotoImage(image = img_grayscale)
   uploaded_img_label.config(image = img)
   uploaded_img_label.photo_ref = img
def display_color_channel(channel):
   if('filename' not in globals() or filename==''):
       return

   if channel == 'red':
      channel_index = 0
   elif channel == 'green':
      channel_index = 1
   else:
      channel_index = 2
   img_rgb = Image.open(filename)
   image_array = numpy.array(img_rgb)
   n_rows = image_array.shape[0]
   n_cols = image_array.shape[1]
   for row in range(n_rows):
      for col in range(n_cols):

         for rgb in range(3):
            if (rgb != channel_index):
               image_array[row][col][rgb] = 0
   pil_img = Image.fromarray(numpy.uint8(image_array))
   pil_img = pil_img.resize((193, 193))
   img = ImageTk.PhotoImage(image = pil_img)
   uploaded_img_label.config(image = img)
   uploaded_img_label.photo_ref = img

def CompandDecompButtons():
    global level1compress
    global level2compress
    global level3compress
    global level4compress
    global level5compress

    global level1decompress
    global level2decompress

    x = width / 10
    y = height / 12
    level1compress = tk.Button(my_w, text='Compress Text', bg='lightblue', font=font, width=20)
    level1compress.place(x=width / 2.55, y=(height/7)+60)  
    level1compress['command'] = lambda: TextCompressThread()

    level2compress = tk.Button(my_w, text='Compress Gray', bg='lightblue',font=font, width=20)
    level2compress.place(x=width / 2.55, y=(height/7)+90)  
    level2compress['command'] = lambda: CompressionThread("Gray","Standard")

    level3compress = tk.Button(my_w, text='Compress Gray Difference', bg='lightblue', font=font,width=20)
    level3compress.place(x=width / 2.55, y=(height/7)+120)  
    level3compress['command'] = lambda: CompressionThread("Gray","Difference")

    level4compress = tk.Button(my_w, text='Compress Color', bg='lightblue', font=font,width=20)
    level4compress.place(x=width / 2.55, y=(height/7)+150) 
    level4compress['command'] = lambda: CompressionThread("Colored","Standard")

    level5compress = tk.Button(my_w, text='Compress Color Difference', bg='lightblue', font=font,width=20)
    level5compress.place(x=width / 2.55, y=(height/7)+180)  
    level5compress['command'] = lambda: CompressionThread("Colored","Difference")


    level1decompress = tk.Button(my_w, text='Decompress Text', bg='lightgreen', font=font,width=20)
    level1decompress.place(x=width / 2.55, y=(height/1.5) +30)  
    level1decompress['command'] = lambda: TextDeCompressThread()

    level2decompress = tk.Button(my_w, text='Decompress Image', bg='lightgreen', font=font,width=20)
    level2decompress.place(x=width / 2.55, y=(height / 1.5)+60)  
    level2decompress['command'] = lambda: DeCompressionThread()


my_w = Tk()
height = 500
width = 700
my_w.configure(background='bisque')
CreateScreen(width,height);
my_w.resizable(False, False)
my_w.title('Huffman')
font=('times', 8, 'bold')
my_w.protocol("WM_DELETE_WINDOW", on_closing)

ColorButtons()
upload_button = Button(my_w, text='Upload Image', font=font, width=20, bg='magenta',command=lambda: upload_file())
decompress_upload_button = Button(my_w, text='Upload Zip', font=font, width=20, bg='green',foreground="white",command=lambda: UploadZip())
text_upload_button = Button(my_w, text='Upload Text', font=font, width=20, bg='orange',command=lambda: UploadText())
decompress_data_button = Button(my_w, text='DeCompress Data', font=font, width=27, command=lambda: DeCompressionThread())
InitializeComponents()
CompandDecompButtons()
CreateLabels(width,height)
CreateButtons(width,height)

my_w.mainloop()
