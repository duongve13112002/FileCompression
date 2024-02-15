import math
from queue import PriorityQueue
from PIL import Image
import numpy
import timeit
import csv
from zipfile import ZipFile
import os

import ColoredCompression.Calculations as Calculations
import ColoredCompression.RGBOperations as rgb

class Node:
  character: str = ''
  data: int = 0
  left = None
  right = None
  def __init__(self, character: str, data: int,left=None, right=None):
    self.character = character
    self.data = data
    self.right = right
    self.left = left

  def __str__(self):
    return str(self.character) + " " + str(self.data)
  def __repr__(self):
    return str(self.character) + " " + str(self.data)

  def __gt__(self, node2):
    return self.data > node2.data

  def __eq__(self, node2):
    if(isinstance(node2,Node) and isinstance(self,Node)):
      return self.character == node2.character
    elif(isinstance(node2,Node) ^ isinstance(self,Node)):
      return False
    return True

  def __hash__(self):
    return  hash((self.character))


def EncodeData(current_node : Node, code : str,coded_dict):

  if current_node == None:
    return
  if current_node.character != '-':
    coded_dict[current_node] = code
    code = ""
  EncodeData(current_node.left,code + '0',coded_dict )
  EncodeData(current_node.right, code + '1',coded_dict )
  return coded_dict


def SaveEncodedData(first_data,coded_map, color : int):
  encoded_data = ""
  for row in first_data:
    for item in row:
      temp_node = Node(item[color],0)
      encoded_data = encoded_data + str(coded_map[temp_node])
  return encoded_data

def DecodeData(root_node,pivot,coded_string,rowc,columnc,process_method_of_image):
  bit_list = []
  bit_list[:0] = coded_string
  temp_node = root_node
  result = []
  counter = 0
  temp=[]
  for tempbit in bit_list:

      if(tempbit == '1'):
        temp_node = temp_node.right
      else:
        temp_node = temp_node.left

      if (temp_node.character != '-'):
        temp.append(temp_node.character)
        temp_node = root_node
        counter = counter + 1
        if(counter == rowc):
          result.append(temp)
          temp = []
          counter = 0

  result = numpy.array(result, dtype=numpy.int8)
  if(process_method_of_image=="Difference"):
    result = RecoverDifferencedArray(result, pivot)
  return result

def BuildHuffmanTree(character_map):
  node_list = PriorityQueue()
  root_node = None

  for key in character_map:
    temp_node = Node(key, character_map.get(key))
    node_list.put(temp_node)

  while node_list.qsize() >= 2:
    first = node_list.get()
    second = node_list.get()
    char = '-'
    newdata = first.data + second.data

    new_node = Node(char, newdata, first, second)
    root_node = new_node
    node_list.put(new_node)

  return root_node

def Read_File(file : str):
  list = []
  file = open(file, "r")

  for line in file:
    for character in line:
      if(character != "\n" and character != ' ' and character != ''):
        list.append(character)

  return list

def Read_Image(file : str,process_method_of_image):
  list = []
  img = Image.open(file)
  img = img.convert('RGB')
  arr = numpy.array(img)

  red_array = rgb.DivideRGB(arr,0)
  green_array = rgb.DivideRGB(arr,1)
  blue_array = rgb.DivideRGB(arr,2)

  global red_pivot
  global green_pivot
  global blue_pivot
  red_pivot=0
  green_pivot=0
  blue_pivot=0
  if(process_method_of_image=="Difference"):
    red_array,red_pivot = CalculateDifferencedArray(red_array)
    green_array,green_pivot = CalculateDifferencedArray(green_array)
    blue_array,blue_pivot = CalculateDifferencedArray(blue_array)
    arr = rgb.MergeRGB(red_array,green_array,blue_array)

  return arr,red_array,green_array,blue_array

def RecoverDifferencedArray(char_list,pivot):
  recovered_array = numpy.array(char_list, copy=True)
  N = char_list.shape[0]
  M = char_list.shape[1]

  recovered_array[0][0] = pivot + int(char_list[0][0])
  for i in range(1, N):
    first_row = int(recovered_array[i - 1][0])
    second_row = int(recovered_array[i][0])
    recovered_array[i][0] = first_row + second_row

  for i in range(N):
    for j in range(1, M):
      second_column = recovered_array[i][j]
      first_column = int(recovered_array[i][j - 1])
      recovered_array[i][j] = int(second_column + first_column)

  return recovered_array
def CalculateDifferencedArray(char_list):
  diff_arr = numpy.array(char_list, copy=True)

  N = char_list.shape[0]
  M = char_list.shape[1]
  for i in range(N):
    for j in range(1, M):
      second_column = int(char_list[i][j])
      first_column = int(char_list[i][j - 1])
      diff_arr[i][j] = second_column - first_column

  pivot = char_list[0][0]
  diff_arr[0][0] = char_list[0][0] - pivot
  for i in range(1, N):
    first_row = int(char_list[i - 1][0])
    second_row = int(char_list[i][0])
    diff_arr[i][0] = second_row - first_row

  return diff_arr,pivot

def FillMap(char_list):
  result = dict()
  for row in char_list:
    for item in row:
      if(item in result):
        result[item] = result[item] + 1
      else:
        result.setdefault(item, 1)

  return result

def GetBitArray(encoded_string):
  b = bytearray()
  t=len(encoded_string)
  for i in range(0, len(encoded_string), 8):
    upper = i+8
    byte = encoded_string[i:upper]
    b.append(int(byte, 2))
  return b

def pad_encoded_text(encoded_text):
  extra_padding = 8 - len(encoded_text) % 8
  for i in range(extra_padding):
    encoded_text += "0"
  return encoded_text,extra_padding

def readBinaryFile(filename,red_length,green_length,blue_length):
  file = open(filename,"rb")  
  color_strings=["","","",""]
  color_lengths=[red_length,green_length,blue_length]

  count = 0
  current_color = 0
  temp_string = ""
  byte = file.read(1)
  while (len(byte) > 0):
    byte = ord(byte)
    bits = bin(byte)[2:].rjust(8, '0')
    temp_string += bits
    byte = file.read(1)
    count = count + 8
    if(count == color_lengths[current_color]):
      count=0
      color_strings[current_color] = temp_string
      temp_string=""
      current_color = current_color+1

  return color_strings[0],color_strings[1],color_strings[2]


def StoreDictionaryandOthers(red_character_map,green_character_map,blue_character_map,mainpath,redlen,greenlen,bluelen,redex,greenex,blueex,rowc,columc,encoded_string,name,process_method_of_image,extension):
  zipObj = ZipFile(f'{mainpath}BinaryandDictionary.zip', 'w')

  WriteBinaryFile(f"{mainpath}",encoded_string)
  with open(f"{mainpath}dictionary.csv", 'w', encoding='UTF8', newline='') as csvfile:

    csvwriter = csv.writer(csvfile)
    # writing the data rows
    csvwriter.writerow(['Row|Column',rowc,columc,"Colored",process_method_of_image,extension])
    csvwriter.writerow(['KeyLengths', len(red_character_map),len(green_character_map),len(blue_character_map)])
    csvwriter.writerow(['RedDictionary'])
    csvwriter.writerow(['RedPivot',red_pivot])
    csvwriter.writerow(['DecodedLength',redlen])
    csvwriter.writerow(['PadLength',redex])
    for key, value in red_character_map.items():
      csvwriter.writerow([key, value])

    csvwriter.writerow(['GreenDictionary'])
    csvwriter.writerow(['GreenPivot',green_pivot])
    csvwriter.writerow(['DecodedLength', greenlen])
    csvwriter.writerow(['PadLength', greenex])
    for key, value in green_character_map.items():
      csvwriter.writerow([key, value])

    csvwriter.writerow(['BlueDictionary'])
    csvwriter.writerow(['BluePivot', blue_pivot])
    csvwriter.writerow(['DecodedLength', bluelen])
    csvwriter.writerow(['PadLength', blueex])
    for key, value in blue_character_map.items():
      csvwriter.writerow([key, value])

  zipObj.write(f"{mainpath}dictionary.csv", f'{name}dictionary.csv')
  zipObj.write(f"{mainpath}compressedversion.bin", f'{name}compressedversion.bin')
  os.remove(f"{mainpath}dictionary.csv") 
  os.remove(f"{mainpath}compressedversion.bin") 

def ReadDictionaryFile(path):

  with open(path) as csv_file:
    csv_reader = csv.reader(csv_file)
    csvlist = list(csv_reader)
    rowcolumns = [eval(csvlist[0][1]),eval(csvlist[0][2])]
    extension = csvlist[0][5]
    keylengths = [eval(csvlist[1][1]),eval(csvlist[1][2]),eval(csvlist[1][3])]#don't return
    pivots = []
    decodedlengths = []
    extras = [] # padded ones

    red_map = dict()
    green_map = dict()
    blue_map = dict()

    pivots.append(numpy.uint8(csvlist[3][1]))
    decodedlengths.append(eval(csvlist[4][1]))
    extras.append(eval(csvlist[5][1]))
    for i in range(6,int(keylengths[0])+6):
      red_map.update({csvlist[i][0]: int(csvlist[i][1])})

    pivots.append(numpy.uint8(csvlist[int(keylengths[0])+6+1][1]))
    decodedlengths.append(eval(csvlist[int(keylengths[0])+6+2][1]))
    extras.append(eval(csvlist[int(keylengths[0])+6+3][1]))
    for i in range(int(keylengths[0])+6+4,int(keylengths[0])+6+4 + int(keylengths[1])):
      green_map.update({csvlist[i][0]: int(csvlist[i][1])})

    pivots.append(numpy.uint8(csvlist[int(keylengths[0])+6+4 + int(keylengths[1])+1][1]))
    decodedlengths.append(eval(csvlist[int(keylengths[0])+6+4 + int(keylengths[1])+2][1]))
    extras.append(eval(csvlist[int(keylengths[0])+6+4 + int(keylengths[1])+3][1]))
    for i in range(int(keylengths[0])+6+4 + int(keylengths[1])+4,int(keylengths[0])+6+4 + int(keylengths[1])+4+int(keylengths[2])):
      blue_map.update({csvlist[i][0]: int(csvlist[i][1])})

    red_root = BuildHuffmanTree(red_map)
    green_root = BuildHuffmanTree(green_map)
    blue_root = BuildHuffmanTree(blue_map)
    roots = [red_root,green_root,blue_root]
    return roots,pivots,extras,decodedlengths,rowcolumns,extension

def DecodeCompressedFile(mainpath,process_method_of_image,name,fromexternalzip=False):

  zipObj = ZipFile(f'{mainpath}BinaryandDictionary.zip', 'r')

  zipObj.extract(f'{name}dictionary.csv',f'{mainpath[:len(mainpath) - len(name)]}')
  zipObj.extract(f'{name}compressedversion.bin',f'{mainpath[:len(mainpath) - len(name)]}')

  roots,pivots,extras,lengths,rowcolums,extension=ReadDictionaryFile(f"{mainpath}dictionary.csv")

  red, green, blue = readBinaryFile(f"{mainpath}compressedversion.bin", lengths[0],
                                    lengths[1], lengths[2])


  red_component = DecodeData(roots[0], pivots[0], red[0:len(red) - extras[0]], rowcolums[0],
                             rowcolums[1], process_method_of_image)
  green_component = DecodeData(roots[1], pivots[1], green[0:len(green) -  extras[1]], rowcolums[0],
                               rowcolums[1], process_method_of_image)
  blue_component = DecodeData(roots[2], pivots[2], blue[0:len(blue) - extras[2]], rowcolums[0],
                              rowcolums[1], process_method_of_image)

  result = rgb.MergeRGB(red_component, green_component, blue_component)
  im = Image.fromarray(numpy.uint8(result))
  im.save(f"{mainpath}decompressedversion{extension}")
  os.remove(f"{mainpath}dictionary.csv")
  os.remove(f"{mainpath}compressedversion.bin")
  return im

def WriteBinaryFile(mainpath,encoded_string):
  f = open(f"{mainpath}compressedversion.bin", "wb")
  b = GetBitArray(encoded_string)
  f.write((b))
  f.close()
def RunColoredCompression(filename,process_method_of_image):
  extension = filename[len(filename)-4:len(filename)]
  name_without_extension=""
  if("/" in filename):
    name_without_extension = filename[filename.rindex('/') + 1:filename.index(extension)] + '_'
  else:
    name_without_extension = filename[0:filename.index(extension)] + '_'
  path = filename[0:len(filename)-len(name_without_extension)-len(extension)+1]
  start = timeit.default_timer()

  read_data,red_array,green_array,blue_array = Read_Image(filename,process_method_of_image)

  red_character_map = FillMap(red_array)
  green_character_map = FillMap(green_array)
  blue_character_map = FillMap(blue_array)

  red_root_node = BuildHuffmanTree(red_character_map)
  green_root_node = BuildHuffmanTree(green_character_map)
  blue_root_node = BuildHuffmanTree(blue_character_map)

  red_code_map = EncodeData(red_root_node,"",dict())
  green_code_map = EncodeData(green_root_node,"",dict())
  blue_code_map = EncodeData(blue_root_node,"",dict())


  encoded_string = ""
  red_string = SaveEncodedData(read_data,red_code_map,0)
  green_string = SaveEncodedData(read_data, green_code_map,1)
  blue_string = SaveEncodedData(read_data,blue_code_map,2)

  red_string,red_extras = pad_encoded_text(red_string)
  green_string, green_extras = pad_encoded_text(green_string)
  blue_string, blue_extras = pad_encoded_text(blue_string)

  encoded_string = red_string + green_string + blue_string

  StoreDictionaryandOthers(red_character_map,green_character_map,blue_character_map,f"{path}{name_without_extension}",
                           len(red_string),len(green_string),len(blue_string),red_extras,green_extras,
                           blue_extras,read_data.shape[1],read_data.shape[0],encoded_string,name_without_extension,process_method_of_image,f"{extension}")


  calculated_values = Calculations.CalculateAndPrintAll(read_data, red_code_map,green_code_map,blue_code_map)

  im = None
  stop = timeit.default_timer()
  return im,f"{path}{name_without_extension}decompressedversion{extension}",calculated_values
