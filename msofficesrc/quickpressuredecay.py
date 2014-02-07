'''
Created on Nov 5, 2013

@author: PBS Biotech
'''


from tkinter.filedialog import askopenfilenames
from officelib import *


def get_raw_batch_file():
    
    filetypes = ["{Text, csv} {.txt .csv}"]
#     raw_file = askopenfilenames(Multiple=False, filetypes=filetypes)
    raw_file = "{C:/Users/PBS Biotech/Downloads/1.1.csv}"
    
    return raw_file.strip("{}")
    

def extract_csv_text():
   
    raw_file = get_raw_batch_file()
    with open(raw_file, 'r') as f:
        text = [x.split(",") for x in f.read().split("\n")]
    del text[-1]

    return text
    
    
def get_pressure_col_data(raw_data):
    for i in raw_data:
        if i[0] == 'Pumps&ValvesPressurePV(psi)':
            pressure_col = raw_data.index(i)
            break
    else:
        raise Exception
         
    pressure_data = {
                     'times' : [v for v in xllib.date_to_xl_float(raw_data[pressure_col][1:])],
                     'values' : [float(v) for v in raw_data[pressure_col + 1][1:]]
                    }
    return pressure_data


def box_average(data_list, FinalListSize=200):

    list_len = data_list.__len__()
    shrink_factor = list_len // FinalListSize
    samples_to_average = shrink_factor
   
    #odd number of samples to average to get equal # of data pts on each side to avg from
    if not samples_to_average % 2:
        samples_to_average += 1
    
    #sps - samples per side ie 5 -> middle item has 2 items on either side
    sps = (samples_to_average - 1) // 2

    boxed_data = [sum(data_list[i-sps : i+sps+1]) / samples_to_average for i in range(sps, list_len - sps, shrink_factor)]
    return boxed_data
         




def main():
    batch_data = extract_csv_text()
#     xl, wb, ws, cells = xlobjs()
# 
#     xl.EnableLargeOperationAlert = False
#     cells.Range(cells(1,1), cells(len(batch_data), len(batch_data[0]))).Value = batch_data
#     xl.EnableLargeOperationAlert = True
    
    data_as_columns = {k : box_average(v) for k, v in get_pressure_col_data(list(zip(*batch_data))).items()}

#     tempfile = "C:\\pressure.csv"
#     with open(tempfile, 'w') as f:
# # #         f.write(','.join([k for k in data_as_columns.keys()]))
#         f.write("Time, Pressure(psi)\n")
#         f.write('\n'.join([str(x).strip("()") for x in list(zip(data_as_columns['times'], data_as_columns['values']))]))
#                  

    xl, wb, ws, cells = xllib.xlobjs()
 
    xl.EnableLargeOperationAlert = False
    cells.Range(cells(1,1), cells(len(batch_data), len(batch_data[0]))).Value = batch_data
    xl.EnableLargeOperationAlert = True
if __name__ == '__main__':
    
    main()
