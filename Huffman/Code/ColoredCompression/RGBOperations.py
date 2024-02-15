import numpy

def DivideRGB(matrix_array, color : int):
  new_array = []
  for row in matrix_array:
    temp = []
    for item in row:
      temp.append(item[color])
    new_array.append(temp)
  new_array = numpy.array(new_array)
  return new_array

def MergeRGB(red_array,green_array,blue_array):
  result = []
  for i in range(0,red_array.shape[0]):
    temp = []
    for j in range(0,red_array.shape[1]):
        triplet = [red_array[i][j],green_array[i][j],blue_array[i][j]]
        temp.append(triplet)
    result.append(temp)
  result = numpy.array(result)
  return result
