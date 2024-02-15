import math

def AverageLength(first_data,coded_map):
  global total_length
  global average_length
  total_length = len(first_data)
  average_length = 0
  key: Node
  for key in coded_map:
    temp_probabilty = key.data / total_length
    average_length = average_length + (temp_probabilty * len(coded_map[key]))
  return average_length

def Entropy(first_data,coded_map):
  entropy = 0
  key: Node
  for key in coded_map:
    temp_probabilty = key.data / total_length
    entropy = entropy + (temp_probabilty * math.log2(temp_probabilty))
  return -1 * entropy

def CompressionRatio(first_data,coded_map):
  return 8 / average_length

def CalculateAndPrintAll(first_data,coded_map):
  avg = AverageLength(first_data,coded_map)
  entropy=Entropy(first_data,coded_map)
  ratio=CompressionRatio(first_data,coded_map)
  return [avg, entropy, ratio, total_length * 8, int((total_length) * avg)]
