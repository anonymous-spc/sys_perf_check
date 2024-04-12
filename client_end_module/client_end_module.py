#!/usr/bin/python3
from client_end_script_helper import (
    command_line_args,
    generate_test_id,
    create_test_directory,
    performance_test,
    get_server_logs,
    extract_data,
    showGraph,
)
from plotcpu import(
    plotcpu,
)
from maingui import(
    showgui,
)

if __name__ == '__main__':
    lower_bound, upper_bound, step_size, run_time = command_line_args()
    test_id = generate_test_id()
    create_test_directory(test_id)
    performance_test(lower_bound, upper_bound, step_size, run_time, test_id)
    get_server_logs(test_id)
    extract_data(test_id)
    showGraph(test_id)
    plotcpu(test_id)
    showgui(test_id)
    
