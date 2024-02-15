import math
from queue import PriorityQueue
from PIL import Image
import numpy

import TextCompression.Calculations as Calculations
from zipfile import ZipFile
import csv
import os

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
  if current_node.character != None:
    coded_dict[current_node] = code
    code = ""
  EncodeData(current_node.left,code + '0',coded_dict)
  EncodeData(current_node.right, code + '1',coded_dict)
  return coded_dict


def SaveEncodedData(first_data,character_map,coded_map,mainpath,name):
  zipObj = ZipFile(f'{mainpath}TXTBinandMap.zip', 'w')
  encoded_data = ""
  for tempchr in first_data:
    encoded_data = encoded_data + str(coded_map[Node(tempchr,0)])

  encoded_data = pad_encoded_text(encoded_data)
  b = get_byte_array(encoded_data)
  f = open(f"{mainpath}compressedbinary.bin", "wb")
  f.write(bytes(b))
  f.close()
  global exten
  insert_exten = 1
  with open(f"{mainpath}Map.csv", 'w', encoding='UTF8', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    for key, value in character_map.items():
      if insert_exten == 1:
        csvwriter.writerow([key, value,exten])
        insert_exten = 0
      else:
        csvwriter.writerow([key, value])
  zipObj.write(f"{mainpath}Map.csv", f'{name}Map.csv')
  zipObj.write(f"{mainpath}compressedbinary.bin", f'{name}compressedbinary.bin')
  os.remove(f"{mainpath}Map.csv")
  os.remove(f"{mainpath}compressedbinary.bin")

def ReadBinaryFile(path):
  file = open(path, "rb")
  bit_string = ""
  byte = file.read(1)
  while (len(byte) > 0):
    byte = ord(byte)
    bits = bin(byte)[2:].rjust(8, '0')
    bit_string += bits
    byte = file.read(1)
  return bit_string

def ReadDictionaryFile(path):
  with open(path, encoding='utf-8') as csv_file:
    csv_reader = csv.reader(csv_file)
    csvlist = list(csv_reader)
    char_map = dict()

    for i in range(0,len(csvlist)):
      char_map.update({csvlist[i][0]: int(csvlist[i][1])})

    root = BuildHuffmanTree(char_map)
    return root,csvlist[0][2]
def DecodeData(mainpath,name,fromexternalzip=False):
  zipObj = ZipFile(f'{mainpath}TXTBinandMap.zip', 'r')

  zipObj.extract(f'{name}Map.csv',f'{mainpath[:len(mainpath) - len(name)]}')
  zipObj.extract(f'{name}compressedbinary.bin',f'{mainpath[:len(mainpath) - len(name)]}')

  bit_list = list(ReadBinaryFile(f'{mainpath}compressedbinary.bin'))

  root_node,extention= ReadDictionaryFile(f'{mainpath}Map.csv')

  temp_node = root_node
  result = ""
  padded_info = ""
  for i in range(0,8):
    padded_info= padded_info+ bit_list[i]

  bit_list = bit_list[8:]
  extra_padding = int(padded_info, 2)
  bit_list = bit_list[:-1 * extra_padding]
  for tempbit in bit_list:

      if(tempbit == '1'):
        temp_node = temp_node.right
      else:
        temp_node = temp_node.left

      if (temp_node.character != None):
        result = result + str(temp_node.character)
        temp_node = root_node

  f = open(f"{mainpath}decodedText{extention}", "w", encoding='utf-8')
  f.write(f"{result}")
  os.remove(f"{mainpath}Map.csv")
  os.remove(f"{mainpath}compressedbinary.bin")

  return result,extention
def BuildHuffmanTree(char_map):
  node_list = PriorityQueue()
  root_node = None

  for key in char_map:
    temp_node = Node(key, char_map.get(key))
    node_list.put(temp_node)

  while node_list.qsize() >= 2:
    first = node_list.get()
    second = node_list.get()
    char = None
    newdata = first.data + second.data

    new_node = Node(char, newdata, first, second)
    root_node = new_node
    node_list.put(new_node)

  return root_node

def Read_File(file : str):
  list = []
  file = open(file, "r", encoding='utf-8')
  text = file.read()
  text = text.rstrip()
  for character in text:
    list.append(character)

  return list

def FillMap(char_list):
  result = dict()
  for item in char_list:
    if(item in result):
      result[item] = result[item] + 1
    else:
      result.setdefault(item, 1)

  return result


def pad_encoded_text(encoded_text):
  extra_padding = 8 - len(encoded_text) % 8
  for i in range(extra_padding):
    encoded_text += "0"

  padded_info = "{0:08b}".format(extra_padding)
  encoded_text = padded_info + encoded_text
  return encoded_text

def remove_padding(padded_encoded_text):
  padded_info = padded_encoded_text[:8]
  extra_padding = int(padded_info, 2)

  padded_encoded_text = padded_encoded_text[8:]
  encoded_text = padded_encoded_text[:-1 * extra_padding]

  return encoded_text

def get_byte_array(padded_encoded_text):
  if (len(padded_encoded_text) % 8 != 0):
    print("Encoded text not padded properly")
    exit(0)

  b = bytearray()
  for i in range(0, len(padded_encoded_text), 8):
    byte = padded_encoded_text[i:i + 8]
    b.append(int(byte, 2))
  return b

def RunTextCompression(filename):
  extension = filename[len(filename) - len(filename.split(".")[1])-1:len(filename)]
  global exten
  exten = extension
  #print(extension)
  name_without_extension=""
  if("/" in filename):
    name_without_extension = filename[filename.rindex('/') + 1:filename.index(extension)] + '_'
  else:
    name_without_extension = filename[0:filename.index(extension)] + '_'
  path = filename[0:len(filename) - len(name_without_extension) - len(extension) + 1]

  read_data = Read_File(filename)

  global character_map
  character_map = FillMap(read_data)

  root_node = BuildHuffmanTree(character_map)

  code_map = EncodeData(root_node,"",dict())

  values=Calculations.CalculateAndPrintAll(read_data,code_map)

  SaveEncodedData(read_data,character_map,code_map,f"{path}{name_without_extension}",f'{name_without_extension}')

  return f"{path}{name_without_extension}decompressedversion{extension}",values
