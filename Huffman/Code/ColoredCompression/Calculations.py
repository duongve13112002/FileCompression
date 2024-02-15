import math

def AverageLength(first_data,red_map,green_map,blue_map):
  global total_length
  total_length = len(first_data) * len(first_data[0]) 
  global average_length
  average_length = 0
  key: Node
  maps = [red_map,green_map,blue_map]
  for coded_map in maps:
    for key in coded_map:
      temp_probabilty = key.data / float(total_length)
      average_length = average_length + (temp_probabilty * len(coded_map[key]))

  average_length = average_length / 3
  return average_length

def Entropy(first_data,red_map,green_map,blue_map):
  entropy = 0
  key: Node
  maps = [red_map,green_map,blue_map]
  for coded_map in maps:
    for key in coded_map:
      temp_probabilty = key.data / float(total_length)
      entropy = entropy + (temp_probabilty * math.log2(temp_probabilty))
  return -1 * (entropy / 3)

def CompressionRatio():
  return 8 / average_length


def CalculateAndPrintAll(read_data, red_code_map,green_code_map,blue_code_map):
  avg = AverageLength(read_data, red_code_map,green_code_map,blue_code_map)
  entropy=Entropy(read_data, red_code_map,green_code_map,blue_code_map)
  ratio=CompressionRatio()
  return [avg,entropy,ratio,total_length*3*8,int((total_length*3)*average_length)]

