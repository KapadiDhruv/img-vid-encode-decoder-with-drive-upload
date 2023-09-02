import os
import py_compile
import sys
import shutil

# to take userInput for the /u/
input_var = input("Enter folder to be uploaded from the original-data: ")
print ("you entered " + input_var) 

with open('sub_list.csv','w+') as file:
    file.write(input_var)

os.system('python3 encode.py')
os.system('python3 uploadtodrive.py')
os.system('python3 transfer_to_mongo.py')