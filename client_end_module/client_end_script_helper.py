import os,json,subprocess,argparse,csv,re,socket,csv,tkinter as tk
from datetime import datetime
from ftplib import FTP
from configparser import ConfigParser
from tkinter import ttk
from math import ceil
from time import sleep

# external modules
# locust is also there
import metrohash
import pandas as pd
import matplotlib.pyplot as plt
from PIL import ImageTk, Image

# test configuration
from config import LOG_HOST,CPU_HOST,HTTP_PORT,SERVER_DAEMON_PORT,FTP_SERVER_PORT,SEARCH_LINES_LIMIT
# LOG_HOST="10.129.7.11"
# TEST_SERVER_HOST="https://abc.com/"
# CPU_HOST ="10.129.7.11"
# HTTP_PORT=5002
# SERVER_DAEMON_PORT=5000
# FTP_SERVER_PORT=5001
# SEARCH_LINES_LIMIT=200000

def get_util_list(num):
    lst=[]
    in_file=str(num)+"_users.txt"
    out_file=str(num)+".csv"
    command = "awk -F' ' '{print $2\",\"$3}' "+in_file+" > "+out_file
    subprocess.run(command,shell=True)

    lst.append(str(num))
    with open(out_file,'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            lst.append(row[1])
    return lst

def get_util_header(num):
    lst=[]
    out_file=str(num)+".csv"

    lst.append("num_of_users")
    with open(out_file,'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            if(row[0]=="all"):
                lst.append(row[0])
            else:
                lst.append("core:"+row[0])
    return lst


def generate_utilization_csv(low,upper,step):
    write_lst=[]
    os.chdir("./cpu_utilization")
    for num in range(low,upper+1,step):
        write_lst.append(get_util_list(num))
        # get_util_list(num)
    write_lst.insert(0,get_util_header(low))
    cpu_util_file="cpu_util.csv"
    with open(cpu_util_file,'w+') as file:
        for row in write_lst:
            file.write(",".join(row) +"\n")
    os.chdir("..")
    for row in write_lst:
        print(row)


def extract_data(test_id):
    os.chdir(str(test_id))
    file_lst=[]
    f = open('components.json')
    data = json.load(f)
    for i in data:
        print(i["componentName"]+"-"+test_id+".log")
        res=i["componentName"]+"-"+test_id+".log"
        file_lst.append([res,i["timeUnit"]])
    f.close()
    for file in file_lst:
        id_pattern=test_id
        extract_time(id_pattern,file[0],file[1])

def generate_test_id():
    hash_input=str(datetime.now()).encode('utf-8')
    test_id=str(metrohash.metrohash64(hash_input).hex())
    return test_id

# def generate_test_id():
#     now=datetime.now()
#     custom_format = "%Y-%m-%d_%H-%M-%S"
#     test_id = now.strftime(custom_format)
#     return test_id



def create_test_directory(test_id):
    current_dir = os.getcwd()
    make_dir=["mkdir",f"{test_id}"]
    subprocess.run(make_dir)

def get_cpu_files(lower,upper,step):
    create_dir=["mkdir","-p","cpu_utilization"]
    subprocess.run(create_dir)
    os.chdir("cpu_utilization")
    for users in range(lower,upper+1,step):
        file_name=str(users)+"_users"+".txt"
        file_address="http://"+CPU_HOST+":"+str(HTTP_PORT)+"/"+file_name
        get_file=["curl",file_address]
        response = subprocess.run(get_file,capture_output=True,text=True)
        print("hit")
        if(response.returncode !=0 ):
            print(get_file)
            print(response.stderr)
            print("HTTP server is not working correctly")
            input()
        else:
            print("get_cpu_files",file_name)
            f = open(file_name,"w+")
            f.write(response.stdout)
            f.close()
    os.chdir("..")

def performance_test(lower_bound,upper_bound,step_size,run_time,test_id):
    for num_user in range(lower_bound,upper_bound+1,step_size):
        write_config(test_id,num_user)
        rate=ceil(num_user*0.2)
        time=run_time #seconds
        message=["MeasureCPU",str(time),str(num_user)]
        send_client_status_no_receive(CPU_HOST,message)
        locust_cmd=["locust","-f","./perfcheck.py",\
            "--headless","-u",f"{num_user}","-r",f"{rate}","-t",f"{time}",\
                "--csv-full-history",f"--csv={test_id}/{num_user}"]
        subprocess.run(locust_cmd)
    subprocess.run(["rm","test.ini"])
    os.chdir(f"./{test_id}")
    message=["start_http"]
    send_client_status_no_receive(CPU_HOST,message)
    sleep(5)
    get_cpu_files(lower_bound,upper_bound,step_size)
    message=["stop_http"]
    send_client_status_no_receive(CPU_HOST,message)
    generate_utilization_csv(lower_bound,upper_bound,step_size)
    os.chdir("..")


def command_line_args():
    parser = argparse.ArgumentParser(prog='./client_end_module.py',\
    description='To figure out system level bottleneck component for REST API based services')
    parser.add_argument('-l',metavar="LOWER_BOUND_USERS",required=True,type=int,help='Specify the lower bound of the number of users.')
    parser.add_argument('-u',metavar="UPPER_BOUND_USERS",required=True,type=int,help='Specify the upper bound of the number of users.')
    parser.add_argument('-s',metavar="STEP_SIZE",required=True,type=int,help='Specify the step size for incrementing the number of users.')
    parser.add_argument('-t',metavar="RUN_TIME",default=60,type=int,help='Specify the runtime for each user number being tested')
    args = parser.parse_args()
    return args.l,args.u,args.s,args.t

def get_server_logs(test_id):
    num_lines_extract=SEARCH_LINES_LIMIT# change this in the future
    client_run(test_id,LOG_HOST,num_lines_extract)
    extract_file = str(test_id)+ ".tar.gz"
    subprocess.run(["tar","-xvzf",extract_file])
    subprocess.run(['cp','components.json',test_id])

def write_config(test_id,num_users):
    config=ConfigParser()
    config["test"]={
        "test-id":test_id,
        "num-of-users":num_users
    }
    with open("test.ini","w+") as f:
        config.write(f)
def read_config():
    config=ConfigParser()
    config.read("test.ini")
    config_data = config["test"]
    return config_data["test-id"],config_data["num-of-users"]

# def extract_time(id_pattern,file_name,timeUnit):
#     s=file_name.split(".")
#     head=['Numusers','Averagetime']
#     head1=['Responsetime']
#     data=[]
#     data1=[]
#     outfile=s[0]+"restime.csv"
#     outputfile=s[0]+".csv"
#     print(outputfile)
#     only_id_pattern=re.compile(id_pattern)
#     id_pattern="/"+id_pattern+"/"+"[0-9]+"
#     num_users_pattern = re.compile(id_pattern)
#     response_time_pattern = re.compile("\*\*\*.*\*\*\*")
#     current_users=-1
#     with open(file_name) as file_h:
#         count=0
#         time=0
#         for line in file_h:
#             try:
#                 if line.strip()!="":
#                     users=int(num_users_pattern.search(line).group(0)[18:])
#                     if current_users==-1:
#                         current_users=users
#                     if current_users!=users:
#                         avg_time=time/count
#                         #print(str(current_users)+","+str(avg_time))
#                         if (timeUnit=="s"):
#                             avg_time=avg_time*1000
#                             avg_time = round(avg_time,2)
#                             data.append([str(current_users),str(avg_time)])
#                         else:
#                             avg_time = round(avg_time,2)
#                             data.append([str(current_users),str(avg_time)])
#                         current_users=users
#                         count=0
#                         time=0
#                     response_time=float(response_time_pattern.search(line).group(0)[3:][:-3])
#                     if (timeUnit=="s"):
#                         data1.append([str(response_time*1000)])
#                     else:
#                         data1.append([str(response_time)])
#                     count+=1
#                     time+=response_time
#             except AttributeError :
#                 if only_id_pattern.search(line) == None:
#                     print(line)
#                     print("AttributeError")
#                     exit(1)
#         avg_time=time/count
#         if (timeUnit=="s"):
#             avg_time=avg_time*1000
#             avg_time = round(avg_time,2)
#             data.append([str(current_users),str(avg_time)])
#         else:
#             avg_time = round(avg_time,2)
#             data.append([str(current_users),str(avg_time)])
#     with open(outfile, 'w') as csvfile:
#         csvwriter = csv.writer(csvfile) 
#         csvwriter.writerow(head1) 
#         csvwriter.writerows(data1)
#     with open(outputfile, 'w') as csvfile:
#         csvwriter = csv.writer(csvfile) 
#         csvwriter.writerow(head) 
#         csvwriter.writerows(data)

def extract_time(id_pattern,file_name,timeUnit):
    s=file_name.split(".")
    head=['Numusers','Averagetime']
    head1=['Responsetime']
    data=[]
    data1=[]
    outfile=s[0]+"restime.csv"
    outputfile=s[0]+".csv"
    print(outputfile)
    only_id_pattern=re.compile(id_pattern)
    id_pattern="/"+id_pattern+"/"+"[0-9]+"
    num_users_pattern = re.compile(id_pattern)
    response_time_pattern = re.compile("\*\*\*.*\*\*\*")
    current_users=-1
    with open(file_name) as file_h:
        # count=0
        # time=0
        x=dict()
        y=dict()
        for line in file_h:
            try:
                if line.strip()!="":
                    users=int(num_users_pattern.search(line).group(0)[18:])
                    response_time=float(response_time_pattern.search(line).group(0)[3:][:-3])
                    if users not in x:
                        if(timeUnit=="s"):
                            x[users]=(response_time*1000)
                            y[users]=1
                            data1.append([str(response_time*1000)])
                        elif(timeUnit=="micros"):
                            x[users]=(response_time/1000)
                            y[users]=1
                            data1.append([str(response_time/1000)])
                        else:
                            x[users]=(response_time)
                            y[users]=1
                            data1.append([str(response_time)])
                    else:
                        if(timeUnit=="s"):
                            x[users]+=(response_time*1000)
                            y[users]+=1
                            data1.append([str(response_time*1000)])
                        elif(timeUnit=="micros"):
                            x[users]+=(response_time/1000)
                            y[users]+=1
                            data1.append([str(response_time/1000)])
                        else:
                            x[users]+=(response_time)
                            y[users]+=1
                            data1.append([str(response_time)])
            except AttributeError :
                if only_id_pattern.search(line) == None:
                    print(line)
                    print("AttributeError")
                    exit(1)
                    
        for cur in x:
            avg_time=x[cur]/y[cur]
            avg_time = round(avg_time,2)
            data.append([str(cur),str(avg_time)])
    with open(outfile, 'w') as csvfile:
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(head1) 
        csvwriter.writerows(data1)
    with open(outputfile, 'w') as csvfile:
        csvwriter = csv.writer(csvfile) 
        csvwriter.writerow(head) 
        csvwriter.writerows(data)


def client_run(testName,logHost,numLinesExtract):
    message = ["ExtractLogs",testName,str(numLinesExtract)]
    extractionStatus=send_client_status(logHost,message)
    if extractionStatus != "ExtractionComplete":
        print("Unable to Extract Logs")
        exit(1)
    print(extractionStatus)
    print("Fetching log files")
    ftp_client(logHost,testName)
    message=["CloseFTPServer"]
    FTPServerStatus=send_client_status(logHost,message)
    if  FTPServerStatus!= "FTPServerClosed":
        print("Unable to close FTP server")
        exit(1)
    print(FTPServerStatus)

def send_client_status_no_receive(host,message):
    port = SERVER_DAEMON_PORT  # socket server port number

    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server

    message= ",".join(message)
    print(message)
    client_socket.send(message.encode())  # send message

def send_client_status(host,message):
    port = SERVER_DAEMON_PORT# socket server port number

    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server

    # if message[0]=="ExtractLogs" or message[0]=="CloseFTPServer":
    message= ",".join(message)
    print(message)
    client_socket.send(message.encode())  # send message
    data = client_socket.recv(1024).decode()  # receive response
    client_socket.close()  # close the connection
    return data
    # else:
    #     print("No message Received at client check for errors")
    #     exit(1)

def ftp_client(host,testName):
    port=FTP_SERVER_PORT
    fileName = testName+".tar.gz"
    ftp = FTP()
    ftp.connect(host,port)
    ftp.login()
    ftp.retrbinary("RETR " +fileName,open(fileName,"wb").write)
    print("log files received")

def showGraph(test_id):
    file_lst=[]
    y_list=[]
    components=[]
    f = open('components.json')
    data = json.load(f)
    for i in data:
        res=i["componentName"]+"-"+test_id+".csv"
        file_lst.append(res)
        y_list.append("y_"+i["componentName"])
        components.append(i["componentName"])
    # Closing file
    f.close()
    for i in range(len(file_lst)):
        var=pd.read_csv(file_lst[i])
        y_list[i]=list(var['Averagetime'])
    
    for p in y_list:
        p.insert(0,0)

    x = list(var['Numusers'])
    x.insert(0,0)
    plt.figure(0)
    for i in range(len(y_list)):
        plt.plot(x,y_list[i],marker='o',label=components[i])

    plt.grid(True)
    plt.legend(loc='best')
    plt.xlabel("Number of users")
    plt.ylabel("Response time (ms)")
    resultimage=test_id+".png"
    plt.savefig(resultimage)

def showgui(test_id):
    result=test_id+".png"
    window = tk.Tk()
    window.title("Image and Table Presentation")

    # # Set a colored background
    background_color = "#FF7A7A"  # Specify the desired background color

    canvas = tk.Canvas(window)
    # canvas.configure(bg=background_color)
    canvas.pack(side=tk.LEFT,fill=tk.BOTH, expand=True)


    # Create a Scrollbar widget
    scrollbar = tk.Scrollbar(window, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Configure the Canvas to use the Scrollbar
    canvas.configure(yscrollcommand=scrollbar.set)


    # Create a Frame inside the Canvas to hold the content




    frame = tk.Frame(canvas,bg=background_color,bd=10)


    canvas.create_window((0,0), window=frame, anchor=tk.NW,width=1835)


    heading_label = tk.Label(frame, text="Image and Table Presentation", font=("Arial", 40, "bold"), fg="black",bg=background_color)
    heading_label.pack()
    heading_label.pack(pady=10)


    image = Image.open(result)
    image = image.resize((800, 600))  # Resize the image if needed
    photo = ImageTk.PhotoImage(image)
    image_label = ttk.Label(frame, image=photo, borderwidth=2, relief="solid")
    # image_label.place(x=50, y=100)  # Customize the position of the image label
    image_label.pack(expand=True)
    # image_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    image_label.pack()
    image_label.pack(pady=10)



    heading_label1 = tk.Label(frame, text="Table containing Response Time(ms) vs number of users ", font=("Arial", 40, "bold"), fg="black",bg=background_color)
    heading_label1.pack()
    heading_label1.pack(pady=10,padx=30)


    # merging the csv files# Read the CSV files into DataFrames
    columns=["Numusers"]
    merged_data = pd.DataFrame()
    f = open('components.json')
    data = json.load(f)

    for i in data:
        columns.append(i["componentName"]+"_time(ms)")
        res=i["componentName"]+"-"+test_id+".csv"
        df = pd.read_csv(res)
        if len(merged_data)== 0:
            merged_data = df
        else:
            # print(df.columns)
            merged_data = pd.merge(merged_data,df, on=df.columns[0])

    table = ttk.Treeview(frame)

    style = ttk.Style()

    style.configure("Treeview.Heading",
                    font=('Arial', 20, 'bold'),  # Set the font size for headers
                    anchor="center",
                    borderwidth=1,
                    relief="solid") 
    style.configure("Treeview",
                    font=('Arial', 16),  # Set the font size
                    anchor="center",
                    borderwidth=1,
                    relief="solid")     # Set alignment to center

    style.configure("Custom.Treeview.Cell",
                    borderwidth=1,
                    relief="solid")
    table['columns'] = columns

    table.heading('#0', text='Index')
    for column in columns:
        table.heading(column, text=column)
    for row in merged_data.itertuples(index=False):
        table.insert("", tk.END, values=row)
        table.insert("", tk.END)
    for column in table["columns"]:
        table.column(column, anchor="center")
    table.configure(show="headings")  # Hide the first empty column
    table.configure(height=25)
    table.pack(fill="both",expand="True")
    table.pack(pady=(10,50),padx=80)
    frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox(tk.ALL))
    canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

    window.mainloop()