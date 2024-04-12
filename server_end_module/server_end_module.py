#!/usr/bin/python3
import socket
from time import sleep
import json
import os
import subprocess
import tarfile
import shutil
from twisted.cred.checkers import AllowAnonymousAccess
from twisted.cred.portal import Portal
from twisted.internet import reactor
from twisted.protocols.ftp import FTPFactory,FTPRealm
from config import SERVER_DAEMON_PORT,HTTP_PORT,FTP_SERVER_PORT

CPU_UTIL_TIME_MARGIN=3
CPU_UTIL_FILE="cpu_utilization.txt"
CPU_DIRECTORY="cpu_utilization"

childid = 0
def FTPthread():
    if os.path.isdir("public") == False:
        os.makedirs("public")
    portal = Portal(FTPRealm("./public"),[AllowAnonymousAccess()])
    factory = FTPFactory(portal)
    reactor.listenTCP(FTP_SERVER_PORT,factory)
    reactor.run()
    reactor.stop()

def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

def extractLogsNew(testName,numExtract):
    # to extract logs based on locations from components.json
    if os.path.isdir("logs") == False:
        os.makedirs("logs")
    if os.path.isdir("logs/"+testName) == False:
        os.makedirs("logs/"+testName)
    json_file=open(componentsFileName,"r")
    components=json.load(json_file)
    json_file.close()
    direc="logs/"+testName+"/"
    print(components)
    for component in components:
        # storing numExtract log lines in a temp file
        temp_file_name=".temp"
        file_name=component["componentName"]+"-"+testName+".log"
        command = ["tail","-n",str(numExtract),component["logPath"]]
        tempfd=open(temp_file_name,"w+")
        proc1=subprocess.run(command,stdout=tempfd)
        tempfd.close()

        # getting from line number 
        command = f"cat {temp_file_name} | grep -n START | tail -n 1 | awk -F':' '{{print $1}}'"  # Example command, replace with your desired command
        output = subprocess.check_output(command, shell=True, universal_newlines=True)
        from_line = output.strip()

        # getting to line number 
        command = f"cat {temp_file_name} | grep -n END | tail -n 1 | awk -F':' '{{print $1}}'"  # Example command, replace with your desired command
        output = subprocess.check_output(command, shell=True, universal_newlines=True)
        to_line = output.strip()

        # writing relevant log files
        command = ["sed","-n",f"{from_line},{to_line}p"]
        fd = open(direc+file_name,"w+")
        tempfd=open(temp_file_name,"r+")
        proc = subprocess.run(command,stdin=tempfd,stdout=fd)
        tempfd.close()
        fd.close()
    os.chdir("logs")
    tarfileName=testName+".tar.gz"
    make_tarfile(tarfileName,testName)
    os.chdir("..")
    shutil.copy('logs/'+tarfileName,'public')
    data="ExtractionComplete"
    return data

def extractLogs(testName,numExtract):
    # to extract logs based on locations from components.json
    if os.path.isdir("logs") == False:
        os.makedirs("logs")
    if os.path.isdir("logs/"+testName) == False:
        os.makedirs("logs/"+testName)
    json_file=open(componentsFileName,"r")
    components=json.load(json_file)
    json_file.close()
    direc="logs/"+testName+"/"
    print(components)
    for component in components:
        file_name=component["componentName"]+"-"+testName+".log"
        fd = open(direc+file_name,"w+")
        command = ["tail","-n",str(numExtract),component["logPath"]]
        grepCommand=["grep","-a",testName]
        tempfd=open(".temp","w+")
        proc1=subprocess.run(command,stdout=tempfd)
        tempfd.close()
        tempfd=open(".temp","r+")
        proc2=subprocess.run(grepCommand,stdin=tempfd,stdout=fd)
        tempfd.close()
        fd.close()
    os.chdir("logs")
    tarfileName=testName+".tar.gz"
    make_tarfile(tarfileName,testName)
    os.chdir("..")
    shutil.copy('logs/'+tarfileName,'public')
    data="ExtractionComplete"
    return data

def serverLogExtraction():
    host = "0.0.0.0"
    # port = 5000  # initiate port no above 1024

    server_socket = socket.socket()  # get instance
    server_socket.bind((host, SERVER_DAEMON_PORT))  # bind host address and port together

    # configure how many client the server can listen simultaneously
    server_socket.listen(2)
    while True:
        conn, address = server_socket.accept()  # accept new connection
        print("Connection from: " + str(address))

        # receive data stream. it won't accept data packet greater than 1024 bytes
        data = conn.recv(1024).decode()
        if data =="":
            print("received empty message from client")
            exit(1)
        msg_lst = data.split(",") 
        global childid

        # Extract logs and fork an ftp-server
        if msg_lst[0] == "ExtractLogs":
            childid=os.fork()
            if childid==0:
                FTPthread()
            print("TestName:",msg_lst[1])
            print("numLinesExtract:",msg_lst[2])
            data = extractLogs(msg_lst[1],msg_lst[2])
            print(data)
            conn.send(data.encode()) 
        elif msg_lst[0] == "ExtractLogsNew":
            childid=os.fork()
            if childid==0:
                FTPthread()
            print("TestName:",msg_lst[1])
            print("numLinesExtract:",msg_lst[2])
            data = extractLogsNew(msg_lst[1],msg_lst[2])
            print(data)
            conn.send(data.encode()) 

        # kill the ftp-server
        elif msg_lst[0]=="CloseFTPServer":
            killcommand=["kill","-9",str(childid)]
            subprocess.run(killcommand)
            sleep(2)
            data="FTPServerClosed"
            print(data + " procesesid:",childid)
            conn.send(data.encode()) 
            conn.close()  # close the connection

        elif msg_lst[0]=="MeasureCPU":
            cpu_measure_time=int(msg_lst[1])
            cpu_measure_time-=2*CPU_UTIL_TIME_MARGIN
            num_users=msg_lst[2]
            sleep(CPU_UTIL_TIME_MARGIN)
            os.chdir(CPU_DIRECTORY)
            measure_cpu(cpu_measure_time)
            extract_cpu_usage_for_num_users(num_users)
            os.chdir("..")

        elif msg_lst[0]=="start_http":
            global server_http
            print("start_http")
            server_http=run_http_server()

        elif msg_lst[0]=="stop_http":
            print("stop_http")
            server_http.terminate()
            os.chdir("..")
        endMessage="-----------------------------"
        print(endMessage)

def run_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print("Error executing the command:",command)

def measure_cpu(duration):
    command = "mpstat -P ALL 1 "+ str(duration) +">" + CPU_UTIL_FILE
    run_command(command)

def extract_cpu_usage_for_num_users(num):
    num_cpu = os.cpu_count()
    num_lines = num_cpu+2
    command = f"tail -{num_lines} {CPU_UTIL_FILE} > {num}_users.txt"
    run_command(command)

def run_http_server():
    os.chdir("./"+CPU_DIRECTORY)
    httpServer = ["python3","-m","http.server",str(HTTP_PORT),"-b","0.0.0.0"]   
    status=subprocess.Popen(httpServer)
    return status

def init():
    command=f"mkdir -p {CPU_DIRECTORY}"
    run_command(command)

if __name__ == '__main__':
    try:
        global componentsFileName
        componentsFileName="components.json"
        init()
        serverLogExtraction()
    except KeyboardInterrupt:
        print("")
        print("Exiting")
        

