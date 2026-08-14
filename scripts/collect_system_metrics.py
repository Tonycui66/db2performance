"""1. 生成文件collect_system_metrics.py

2. 负责
	Linux
	CPU
	Memory
	Disk IO
	Network
	Load Average
	Process
	
3. 输出样式
	{
		"timestamp":"",
		"source":"system",
		"metrics":{}
	}
"""
import psutil
import time
import json


def collect():

    return {

        "cpu":
        psutil.cpu_percent(),

        "memory":
        psutil.virtual_memory().percent,


        "disk":
        psutil.disk_io_counters()
        ._asdict(),


        "network":
        psutil.net_io_counters()
        ._asdict()

    }



def run():

    while True:

        data={

        "timestamp":
        time.time(),

        "metrics":
        collect()

        }


        print(
            json.dumps(data)
        )


        time.sleep(1)



if __name__=="__main__":
    run()
