import webbrowser
import json
import os
import pandas as pd
from flask import Flask, send_file
from config import RESULT_PORT
global img_test_id
app = Flask(__name__)


def open_html_file(file_path):
    try:
        webbrowser.open(file_path)
    except Exception as e:
        print(f"Error: {e}")


def showgui(testid):
    #creation of main html
    global img_test_id
    img_test_id = testid
    main="""<!doctype html>
<html lang="en">

<head>

    <!-- {% load static %} -->
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- <link rel="stylesheet" href="global.css"> -->
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet"
        integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">

    <title>Sys_Perf_Check_Results</title>
    <style>
        * {
            margin: 0;
            padding: 0;
        }
        
        .MLheading {
            padding: 10%;
            color: white;
            text-align: center;
            font-size: 300%;
            background-color: #6a757d;
            /* background-color: lightpink; */
        }
        
        .MLcontainer {
            border-radius: 20px;
            padding: 1%;
            margin-left: 20%;
            margin-right: 20%;
            background-color: black;
        }
        
        .dropcustom {
            padding: 5%;
        }
        
        .AlgoContainer {
            background-color: black;
            padding-bottom: 5%;
        }
        
        .doc {
            background-color: black;
        }
        
        /* For Algorithm 1 Page: */
        
        .ML1heading {
            padding: 1%;
            color: white;
            text-align: center;
            font-size: 150%;
            background-color: #6a757d;
            /* background-color: lightpink; */
        }
        
        .ML1container {
            border-radius: 10px;
            /* margin-bottom: 4%; */
            padding: 0%;
            margin-left: 30%;
            margin-right: 30%;
            background-color: black;
        }
        
        .searchfields {
            padding: 1%;
        }
        
        .SearchButton {
            padding: 1%;
            text-align: center;
            font-size: 100%;
        
        }
        
        .MLAlgorithms {
            padding: 0.5%;
        }
        
        .slightpad {
            margin-left: 1%;
            /* padding:0.5%; */
        }
        
        .imgselect {
            width: 50%;
            height: 50%;
            /* float: left; */
        }
        
        .divimg {
        
            padding: 5px;
            border: 0;
        }
        
        /* #div1 { background: #DDD; }
        #div2 { background: #AAA; }
        #div3 { background: #777; }
        #div4 { background: #444; } */
        .input-hidden {
            position: absolute;
            left: -9999px;
        }
        
        .imageoption[type=radio]:checked + label > img {
            border: 1px solid #fff;
            box-shadow: 0 0 3px 3px black;
        }
        
        .imageoption[type=radio] + label > img {
            border: 1px solid #444;
            transition: 500ms all;
        }
    </style>
</head>

<body class="doc">
    <div class="MLheading ">
        <!-- <div class="MLheading " style="  "> -->
        <!-- Content here -->
        <div class="MLcontainer">
            Sys_Perf_Check_Results
            <!-- <h1 ></h1>ML Visualizer -->
        </div>
    </div>
    <!-- <div class="alert alert-warning alert-dismissible fade show" role="alert"> -->
    <!-- <strong>Holy guacamole!</strong> You should check in on some of those fields below. -->
    <!-- <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button> -->
    <!-- </div> -->

    <div class="AlgoContainer">

        <!-- <div class="dropdown ">  -->
        <div class="dropdown container dropcustom" style="text-align:center;">
            <button class="btn btn-secondary dropdown-toggle" type="button" id="dropdownMenuButton2"
                data-bs-toggle="dropdown" aria-expanded="false">
                Choose a type of results to view
            </button>
            <ul class="dropdowncustom dropdown-menu dropdown-menu-dark " aria-labelledby="dropdownMenuButton2">
                <li><a class="dropdown-item " href="index2.html">Number of User Vs Response Time</a></li>
                <li><a class="dropdown-item" href="index4.html">Cpu utilization Vs Number of users</a></li>
                <li><a class="dropdown-item" href="index3.html">consolidated report</a></li>
            </ul>
        </div>
    </div>
    <!-- Optional JavaScript; choose one of the two! -->

    <!-- Option 1: Bootstrap Bundle with Popper -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"
        integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p"
        crossorigin="anonymous"></script>

    <!-- Option 2: Separate Popper and Bootstrap JS -->
    <!--
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.10.2/dist/umd/popper.min.js" integrity="sha384-7+zCNj/IqJ95wo16oMtfsKbZ9ccEh31eOz1HGyDuCQ6wgnyJNSYdrPa03rtR1zdB" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.min.js" integrity="sha384-QJHtvGhmr9XOIpI6YVutG+2QOK9T+ZnN4kzFN1RtK3zEFEIsxhlmWl5/YESvpZ13" crossorigin="anonymous"></script>
    -->
</body>

</html>"""
    file_html = open("index.html", "w")
    file_html.write(main)
    file_html.close()
    
    
    
    print("main file write completed")
    # creation of index1.html file
    start="""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Average Response Times Vs Number of Users</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
        }

        header {
            background-color: #333;
            color: #fff;
            text-align: center;
            padding: 1rem;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }

        .image-container {
            text-align: center;
            margin: 20px 0;
        }

        .image-container img {
            max-width: 100%;
        }

        .table-container {
            margin: 0 auto;
            border-collapse: collapse;
            width: 100%;
            max-width: 100%;
        }

        .styled-table {
            border-collapse: collapse;
            font-size: 1.5em;
            font-family: sans-serif;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
        }
        .styled-table thead tr {
            background-color: #009879;
            color: #ffffff;
            text-align: center;
        }
        .styled-table th,
        .styled-table td {
            padding: 12px 15px;
            text-align: center;
        }
        .styled-table tbody tr {
            border-bottom: 1px solid #dddddd;
        }
        
        .styled-table tbody tr:nth-of-type(even) {
            background-color: #f3f3f3;
        }
        
        .styled-table tbody tr:last-of-type {
            border-bottom: 2px solid #009879;
        }
        .styled-table tbody tr.active-row {
            font-weight: bold;
            color: #009879;
        }
    </style>
</head>
<body>
    <header>
        <h1>Number of users vs Response Times</h1>
    </header>

    <div class="container">
        <div class="image-container">"""
    start=start+"<img src="+testid+".png"
    start=start+""" alt="Beautiful Image">
        </div>

        <div class="table-container">
            <table class="styled-table">
                <thead>
                    <tr>"""
    columns=["Numusers"]
    merged_data = pd.DataFrame()
    f = open('components.json')
    data = json.load(f)

    for i in data:
        columns.append(i["componentName"]+"_time(ms)")
        res=i["componentName"]+"-"+testid+".csv"
        df = pd.read_csv(res)
        if len(merged_data)== 0:
            merged_data = df
        else:
            merged_data = pd.merge(merged_data,df, on=df.columns[0]) 
    for column in columns:
        start=start+"<th>"+column+"</th>"
        # print(column)
    start=start+"""</tr>
                </thead>
                <tbody>"""
                
    for row in merged_data.itertuples(index=False):
        s="<tr>"
        for it in row:
            s=s+"<td>"+str(it)+"</td>"
        s=s+"</tr>"
        start=start+s
             
    end= """
                </tbody>
            </table> 
    </div>
         </div>
      </body>
      </html>"""         
    start=start+end
    
    # saving the html file
    file_html = open("index2.html", "w")
    file_html.write(start)
    file_html.close()
    
    print("1st file write completed")
    # creation of index3.html
    start2="""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Number of Users Vs Response Times</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
        }

        header {
            background-color: #333;
            color: #fff;
            text-align: center;
            padding: 1rem;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }

        .image-container {
            text-align: center;
            margin: 20px 0;
        }

        .image-container img {
            max-width: 100%;
        }

        .table-container {
            margin: 0 auto;
            border-collapse: collapse;
            width: 100%;
            max-width: 100%;
        }

        .styled-table {
            border-collapse: collapse;
            font-size: 1.5em;
            font-family: sans-serif;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
        }
        .styled-table thead tr {
            background-color: #009879;
            color: #ffffff;
            text-align: center;
        }
        .styled-table th,
        .styled-table td {
            padding: 12px 15px;
            text-align: center;
        }
        .styled-table tbody tr {
            border-bottom: 1px solid #dddddd;
        }
        
        .styled-table tbody tr:nth-of-type(even) {
            background-color: #f3f3f3;
        }
        
        .styled-table tbody tr:last-of-type {
            border-bottom: 2px solid #009879;
        }
        .styled-table tbody tr.active-row {
            font-weight: bold;
            color: #009879;
        }
    </style>
</head>
<body>
    <header>
        <h1>Consolidated Results</h1>
    </header>

    <div class="container">"""                    
    f = open('components.json')
    data = json.load(f)
    res=data[0]["componentName"]+"-"+testid+".csv"
    df = pd.read_csv(res)
    numberofusers=[]
    for row in df.itertuples(index=False):
        numberofusers.append(row[0])
            
    for it in numberofusers:
        util="cpu_utilization/"+str(it)+".csv"
        heading="""<h1 style="min-width:100%;">"""+"CPU Utilization Vs Number of Users for "+str(it)+" users"+"</h1>"
        # start2=start2+heading
        df1=pd.read_csv(util)
        temp=""" <div class="table-container">"""+heading+"""<table class="styled-table" style="min-width: 100%;">
                <thead>
                    <tr>"""
        temp=temp+"<th>"+"CPU Number"+"</th>"+"<th>"+"% Utilization"+"</th>"
        temp=temp+"""</tr>
                </thead>
                <tbody>"""
        for row in df1.itertuples(index=False):
            s="<tr>"
            for it in row:
                s=s+"<td>"+str(it)+"</td>"
            s=s+"</tr>"
            temp=temp+s
        temp=temp+"""</tbody>
            </table> 
        </div>"""
        start2=start2+temp
    end2= """
         </div>
      </body>
      </html>"""         
    start2=start2+end2
    
    # saving the html file
    file_html = open("index3.html", "w")
    file_html.write(start2)
    file_html.close()
    
    
    print("second file write completed")
    # making the html3 file
    start3="""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Consolidated Reportindex3</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
        }

        header {
            background-color: #333;
            color: #fff;
            text-align: center;
            padding: 1rem;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }

        .image-container {
            text-align: center;
            margin: 20px 0;
        }

        .image-container img {
            max-width: 100%;
        }

        .table-container {
            margin: 0 auto;
            border-collapse: collapse;
            max-width: 100%;
            overflow: auto;
        }

        .styled-table {
            border-collapse: collapse;
            font-size: 1.5em;
            font-family: sans-serif;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
        }
        .styled-table thead tr {
            background-color: #009879;
            color: #ffffff;
            text-align: center;
        }
        .styled-table th,
        .styled-table td {
            padding: 12px 15px;
            text-align: center;
        }
        .styled-table tbody tr {
            border-bottom: 1px solid #dddddd;
        }
        
        .styled-table tbody tr:nth-of-type(even) {
            background-color: #f3f3f3;
        }
        
        .styled-table tbody tr:last-of-type {
            border-bottom: 2px solid #009879;
        }
        .styled-table tbody tr.active-row {
            font-weight: bold;
            color: #009879;
        }
    </style>
</head>
<body>
    <header>
        <h1>CPU Utilization vs Number of Users</h1>
    </header>

    <div class="">
        <div class="image-container">"""
    start3=start3+"<img src="+testid+"cpu.png"
    start3=start3+""" alt="Beautiful Image">
        </div>

        <div class="table-container" style="border:2px solid black;width:80%;margin:auto">
            <table class="styled-table" >
                <thead>
                    <tr>"""
    var=pd.read_csv("cpu_utilization/cpu_util.csv")
    columns=list(var.head(0))
    # ylist=ylist[1:]
    # columns=["Numusers"]
    # merged_data = pd.DataFrame()
    # f = open('components.json')
    # data = json.load(f)

    # for i in data:
    #     columns.append(i["componentName"]+"_time(ms)")
    #     res="./"+testid+"/"+i["componentName"]+"-"+testid+".csv"
    #     df = pd.read_csv(res)
    #     if len(merged_data)== 0:
    #         merged_data = df
    #     else:
    #         merged_data = pd.merge(merged_data,df, on=df.columns[0]) 
    for column in columns:
        start3=start3+"<th>"+column+"</th>"
        # print(column)
    start3=start3+"""</tr>
                </thead>
                <tbody>"""
                
    for row in var.itertuples(index=False):
        s="<tr>"
        for it in row:
            s=s+"<td>"+str(it)+"</td>"
        s=s+"</tr>"
        start3=start3+s
             
    end3= """
                </tbody>
            </table> 
    </div>
         </div>
      </body>
      </html>"""         
    start3=start3+end3
    
    # saving the html file
    file_html = open("index4.html", "w")
    file_html.write(start3)
    file_html.close()
    
    print("third file write completed")
    #launching of webbrowser
    # html_file_path = 'index.html'
    # open_html_file(html_file_path)
    print(start)
    print(start2)
    print(start3)
    run_flask_app()

@app.route('/')
def results():
    try:
        with open('index.html', 'r') as file:
            contents = file.read()
            print("read worked")
            return contents
    except FileNotFoundError:
        return "File not found."
    except Exception as e:
        return f"An error occurred: {e}"

# @app.route('/index2.html')
# def results2():
#     try:
#         with open('index2.html', 'r') as file:
#             contents = file.read()
#             print("read worked")
#             image_path = str(img_test_id)+".png"
#             return contents
#             return send_file(image_path, mimetype='image/jpg') + contents
#     except FileNotFoundError:
#         return "File not found."
#     except Exception as e:
#         return f"An error occurred: {e}"

# @app.route('/index3.html')
# def results3():
#     try:
#         with open('index3.html', 'r') as file:
#             contents = file.read()
#             image_path = str(img_test_id)+"cpu.png"
#             print("read worked")
#             return contents
#             return send_file(image_path, mimetype='image/jpg') + contents
#     except FileNotFoundError:
#         return "File not found."
#     except Exception as e:
#         return f"An error occurred: {e}"

# @app.route('/index4.html')
# def results4():
#     try:
#         with open('index4.html', 'r') as file:
#             contents = file.read()
#             return contents
#     except FileNotFoundError:
#         return "File not found."
#     except Exception as e:
#         return f"An error occurred: {e}"

@app.route('/<filename>.png')
def get_image(filename):
    # Assuming 'filename' corresponds to a valid image file path
    filename = img_test_id+"/"+filename +".png"

    return send_file(str(filename), mimetype='image/png')

# Route for handling HTML filenames
@app.route('/<filename>.html')
def get_html(filename):
    # Assuming 'filename' corresponds to a valid HTML file path
    with open(str(filename)+".html", 'r') as file:
        content = file.read()
    return content

def run_flask_app():
    app.run(host='0.0.0.0',port=RESULT_PORT)

def cleanup(*args):
    import sys,subprocess,os
    os.chdir("/app")
    subprocess.run(["rm","-r",str(img_test_id)])
    subprocess.run(["rm","-r",str(img_test_id)+".tar.gz"])
    sys.exit(0)
import signal
signal.signal(signal.SIGINT, cleanup)