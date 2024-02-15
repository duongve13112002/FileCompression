import math
from queue import PriorityQueue
from PIL import Image
import numpy
import timeit
import GrayLevelCompression.GrayCalculations as GrayCalculations
import csv
import os
from zipfile import ZipFile

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


def SaveEncodedData(first_data,coded_map):
  encoded_data = ""
  for row in first_data:
    for item in row:
      encoded_data = encoded_data + str(coded_map[Node(item,0)])

  return encoded_data

def DecodeData(root_node,pivotvalue,rowc,columnc,bit_list,process_method_of_image):
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
    result = RecoverDifferencedArray(result, pivotvalue)  

  return result

def BuildHuffmanTree(char_map):
  node_list = PriorityQueue()
  root_node = None

  for key in char_map:
    temp_node = Node(key, char_map.get(key))
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
def GetBitArray(encoded_string):
  b = bytearray()
  t=len(encoded_string)
  for i in range(0, len(encoded_string), 8):
    upper = i+8
    byte = encoded_string[i:upper]
    b.append(int(byte, 2))
  return b

  return list
def readBinaryFile(filename):
  file = open(filename,"rb")
  count = 0
  decoded_string = ""
  byte = file.read(1)
  while (len(byte) > 0):
    byte = ord(byte)
    bits = bin(byte)[2:].rjust(8, '0')
    decoded_string += bits
    byte = file.read(1)
    count = count + 8
  return decoded_string

def Read_Image(file : str,process_method_of_image):
  list = []
  img = Image.open(file)
  img = img.convert('L')# convert to gray
  arr = numpy.array(img)
  global pivot
  pivot = 0
  if (process_method_of_image == "Difference"):
    arr,pivot = CalculateDifferencedArray(arr)

  return arr

def RecoverDifferencedArray(char_list,pivot):
  recovered_array = numpy.array(char_list, copy=True)
  N = char_list.shape[0]
  M = char_list.shape[1]

  recovered_array[0][0] = pivot + char_list[0][0]
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

def pad_encoded_text(encoded_text):
  extra_padding = 0
  if(len(encoded_text) % 8 == 0):
    return encoded_text,extra_padding
  extra_padding = 8 - len(encoded_text) % 8
  for i in range(extra_padding):
    encoded_text += "0"
  return encoded_text,extra_padding

def ReadDictionaryFile(path):
  with open(path) as csv_file:
    csv_reader = csv.reader(csv_file)
    csvlist = list(csv_reader)
    rowcolumns = [eval(csvlist[0][1]),eval(csvlist[0][2])]
    extension = csvlist[0][5]
    keylength = eval(csvlist[1][1])
    gray_map = dict()

    pivot=numpy.uint8(csvlist[3][1])
    decodedlength=eval(csvlist[4][1])
    extra=eval(csvlist[5][1])

    for i in range(6,int(keylength)+6):
      gray_map.update({csvlist[i][0]: int(csvlist[i][1])})

    root = BuildHuffmanTree(gray_map)
    return root,pivot,extra,decodedlength,rowcolumns,extension

def WriteBinaryFile(mainpath,encoded_string):
  f = open(f"{mainpath}compressedversion.bin", "wb")
  b = GetBitArray(encoded_string)
  f.write((b))
  f.close()

def StoreDictionaryandOthers(character_map,mainpath,encodedlength,extra,rowc,columc,name,process_method_of_image,encoded_string,extension):
  zipObj = ZipFile(f'{mainpath}BinaryandDictionary.zip', 'w')
  WriteBinaryFile(f"{mainpath}",encoded_string)
  with open(f"{mainpath}dictionary.csv", 'w', encoding='UTF8', newline='') as csvfile:

    csvwriter = csv.writer(csvfile)

    csvwriter.writerow(['Row|Column', rowc, columc, "Gray",process_method_of_image,extension])
    csvwriter.writerow(['KeyLength', len(character_map)])
    csvwriter.writerow(['Dictionary'])
    csvwriter.writerow(['Pivot', pivot])
    csvwriter.writerow(['DecodedLength', encodedlength])
    csvwriter.writerow(['PadLength', extra])
    for key, value in character_map.items():
      csvwriter.writerow([key, value])

  zipObj.write(f"{mainpath}dictionary.csv", f'{name}dictionary.csv')
  zipObj.write(f"{mainpath}compressedversion.bin", f'{name}compressedversion.bin')
  os.remove(f"{mainpath}dictionary.csv")
  os.remove(f"{mainpath}compressedversion.bin")

def DecodeCompressedFile(mainpath,process_method_of_image,name,fromexternalzip=False):

  zipObj = ZipFile(f'{mainpath}BinaryandDictionary.zip', 'r')

  zipObj.extract(f'{name}dictionary.csv',f'{mainpath[:len(mainpath) - len(name)]}')
  zipObj.extract(f'{name}compressedversion.bin',f'{mainpath[:len(mainpath) - len(name)]}')

  root,pivot,extra,length,rowcolums,extension=ReadDictionaryFile(f"{mainpath}dictionary.csv")
  binarycodedstring = readBinaryFile(f"{mainpath}compressedversion.bin")

  result = DecodeData(root,pivot, rowcolums[0], rowcolums[1],binarycodedstring[0:len(binarycodedstring) - extra],process_method_of_image)

  im = Image.fromarray(numpy.uint8(result))
  im.save(f"{mainpath}decompressedversion{extension}")
  os.remove(f"{mainpath}dictionary.csv")
  os.remove(f"{mainpath}compressedversion.bin")

  return im

def RunGrayCompression(filename,process_method_of_image):
  extension = filename[len(filename) - 4:len(filename)]
  name_without_extension=""
  if("/" in filename):
    name_without_extension = filename[filename.rindex('/') + 1:filename.index(extension)] + '_'
  else:
    name_without_extension = filename[0:filename.index(extension)] + '_'
  path = filename[0:len(filename) - len(name_without_extension) - len(extension) + 1]
  start = timeit.default_timer()

  read_data = Read_Image(filename,process_method_of_image)

  global character_map
  character_map = FillMap(read_data)

  root_node = BuildHuffmanTree(character_map)

  code_map = EncodeData(root_node, "",dict())

  calculated_values = GrayCalculations.CalculateAndPrintAll(read_data,code_map)

  encoded_string=SaveEncodedData(read_data, code_map)
  encoded_string, extras= pad_encoded_text(encoded_string)

  StoreDictionaryandOthers(character_map,f"{path}{name_without_extension}",
                           len(encoded_string),extras,read_data.shape[1], read_data.shape[0],name_without_extension,process_method_of_image,encoded_string,f"{extension}")


  im = None
  stop = timeit.default_timer()

  return im,f"{path}{name_without_extension}decompressedversion{extension}",calculated_values
