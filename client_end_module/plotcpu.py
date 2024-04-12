import pandas as pd
import matplotlib.pyplot as plt
def plotcpu(testid):
    print("inside plot cpu")
    var=pd.read_csv("cpu_utilization/cpu_util.csv")
    ylist=list(var.head(0))
    ylist=ylist[1:]
    print(ylist)
    # print(ylist)
    x = list(var['num_of_users'])
    print(x)
    plt.figure(1)
    for i in range(1,len(ylist)):
        if i==1:
            plt.plot(x,list(var[ylist[i]]),marker='o',label="Core:0-"+str(len(ylist)-2),color='lightgrey')
        else:
            plt.plot(x,list(var[ylist[i]]),marker='o',color='lightgrey')
    plt.plot(x,list(var[ylist[0]]),marker='o',label=ylist[0],color='black')
    plt.grid(True)
    plt.legend(loc='best')
    plt.xlabel("Number of users")
    plt.ylabel("CPU Utilization %")
    resultimage1=testid+"cpu.png"
    plt.savefig(resultimage1)