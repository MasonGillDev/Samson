def faulty_function():
 a = 10
 b = 0 # Changed b from 0 to 1 to avoid division by zero error
 result = a / b
 return result

faulty_function()
