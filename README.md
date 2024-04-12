# sys_perf_check_tool
## Description
* Modern web apps are composed of a frontend and a backend
* The backend is often composed of multiple components
* It is possible that you might have a component in backend that is choking the system at a certain load
* sys_perf_check helps us detect such a component
* e.g. of a such a system is shown below
![example_backend_components](resources/example_components_backend.png "Backend with multiple components")
* the tool itself is composed of two components the client_end_module and server_end_module

## Initial Setup
### Configuring hosts and ports

* the config.py file in client_end_module
```
TEST_SERVER_HOST="https://abc.com/" # host which will point to the backend app 
LOG_HOST="10.129.7.11" # host where logs will be collected
CPU_HOST ="10.129.7.11" # host where the application is running

# the below ones should only be configured in case ports are not available
# match with the config.py file in server_end_module
SERVER_DAEMON_PORT=5000
FTP_SERVER_PORT=5001
HTTP_PORT=5002 
RESULT_PORT = 5500
# this should be configured in case more log lines need to searched for each component
SEARCH_LINES_LIMIT=200000
```

* the config.py file in server_end_module
```
# maps with corresponding values in client_end_module
SERVER_DAEMON_PORT=5000
FTP_SERVER_PORT=5001
HTTP_PORT=5002
```

### components.json
* Need to define a components.json file that will be used by both the client_end_module and server_end_module
* you can specify **componentName** to be anything, **logPath** should point to location of logs and **timeUnit** can be **s,ms or micros**.
* e.g. of the components.json is shown below
```
[
    {
        "componentName":"outer-nginx",
        "logPath":"/var/log/nginx/System-X.log",
        "timeUnit":"s"
    },
    {
        "componentName":"inner-nginx",
        "logPath":"/home/System-X/logs/inner-nginx/access.log",
        "timeUnit":"s"
    },
    {
        "componentName":"uwsgi",
        "logPath":"/home/System-X/logs/uwsgi/uwsgi-daemonize.log",
        "timeUnit":"ms"
    },
    {
        "componentName":"django",
        "logPath":"/home/System-x/django.log",
        "timeUnit":"ms"
    }

]
```

### Registering sys_perf_check endpoint
* make sure to register the below code as an api end point in your web application at path: <host_name>/sys_perf_check/<test_id>/<num_users>
* e.g for python shown below
```
import timeit
# a function that uses cpu for 10 ms
def sys_perf_check_end_point(request,test_id,numuser):
    # for readability new function name
    current_time = timeit.default_timer
    
    dummy_variable=0
    start_time=current_time()
    while(current_time()-start_time<0.01):
        dummy_variable = dummy_variable+1
        
    end_time=current_time()
    res=(end_time-start_time)*1000
    
    return HttpResponse("the time taken to execute the test "+test_id+" is "+str(res)+" miliseconds for "+numuser+ " users")
```

### Logs
* turn on the logs for each component mentioned in components.json
* make sure the response time should be like \*\*\*<response_time>\*\*\* in logs
* request should be displayed like /sys_perf_check/<test_id>/<response_time>
* e.g. logs shown below
```
[24/Jul/2023:13:52:10 +0530] GET /sys_perf_check/2024-02-29_10-09-55/20/ HTTP/1.0***0.024***
```

## Running the tool
### Start the server_end_module
* install twisted module (using pip)
* install htop on the machine for cpu utilization

```
# requires a components.json file
# run the below script on the server where you are hosting your project and want to measure its performance
$ python3 server_end_module.py
```

### Running the cliend_end_script
* install docker if not present
#### Build the docker container
```
$ docker build -t <image_name>
```

#### Run the script using the docker container
```
$ docker run --rm -p <result_port>:5500 -v $(pwd):/app <image_name> python3 client_end_module.py -l <start_load> -u <end_load> -s <step_size> -t <duration>
```

### Results
* they will be available at <result_port> and can be seen in the browser
* e.g. image of result shown below
![result_home](resources/result_home.png "result homepage")
![result_response_time](resources/result_response_time.png "response time vs num of users")
![result_cpu](resources/result_cpu.png "cpu utilization vs num of users")
