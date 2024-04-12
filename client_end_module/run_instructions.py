import time

output="""
-------------------------------------------------------------
To run the docker contaner created using the Dockerfile
present in the current folder use:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
$ docker run -p 5500:5500 -v $(pwd):/app <container_name> python3 client_end_module.py -l <start load> -u <end load> -s <step size of increasing load> -t <duration>
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Before running the container make sure the following requirements are met: 
* hosts, ports, etc are configured correctly in the config.py file.
* there is a correct components.json file for log retrieval
-------------------------------------------------------------
"""
print(output)


