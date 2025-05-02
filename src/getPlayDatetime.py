import os
import re
from collections import defaultdict
from matplotlib import pyplot as plt
from datetime import datetime
import math

file_list = os.listdir("../logs")
file_list.sort()

play_time = {}
ip_dict = {}

join_pattern = r"\[(\d{2}:\d{2}:\d{2})\] \[Server thread/INFO\]: ([^\[]+)\[([^:]+):\d+\] logged in"
left_pattern = r"\[(\d{2}:\d{2}:\d{2})\] \[[^\]]+\]: ([^\s]+) left the game"
remove_pattern = r" \(formerly known as [^\)]+\)"


def main():
    global a, b, n
    ip = False
    for file in file_list:
        if file.split(".")[-1] == "log":
            with open("../logs/"+file, mode="r") as f:
                for l in f:

                    if "logged in" in l:
                        l = clean_log_string = re.sub(remove_pattern, "", l)
                        match = re.search(join_pattern, l)
                        if match:
                            time_data = match.group(1)
                            username = match.group(2)
                            ip_addr = match.group(3)
                            add_list("joined", time_data,
                                     username, ip_addr[1:])
                        else:
                            print("時刻データとユーザー名が見つかりませんでした")
                            print(l)
                        ip = True

                    elif "left" in l:
                        l = clean_log_string = re.sub(remove_pattern, "", l)
                        match = re.search(left_pattern, l)

                        if match:
                            time_data = match.group(1)
                            username = match.group(2)
                            add_list("left", time_data, username)
                        else:
                            print("時刻データとユーザー名が見つかりませんでした")
                            print(l)
                        ip = True
                    if ip:
                        ip = False
                        ip_dict[file] = l

    count_home = []
    count_school = []
    for i in play_time.keys():
        d, e = calculate_time_diff(play_time[i])
        d = [int(i//1800) for i in d]
        e = [int(i//1800) for i in e]
        count_home += d
        count_school += e

    plot_time_diffs(count_home, count_school)


def add_list(status, time_data, username, ip=None):
    if status == "joined":
        if username not in play_time:
            play_time[username] = [["join", time_data, ip]]
        else:
            play_time[username].append(["join", time_data, ip])

    elif status == "left":
        if username not in play_time:
            play_time[username] = [["left", time_data]]
        else:
            play_time[username].append(["left", time_data])


def calculate_time_diff(data):
    join_time = None
    time_diffs_home = []
    time_diffs_school = []
    join_leave = True
    ip_home = False

    for d in data:
        time = datetime.strptime(d[1], "%H:%M:%S")

        if d[0] == 'join' and join_leave:
            if d[2] == "202.231.20.252" or d[2] == '153.231.86.118':
                ip_home = True
            join_leave = False
            join_time = time

        elif d[0] == 'left' and join_time and not join_leave:
            join_leave = True
            if time < join_time:
                time_diff = (time - join_time).total_seconds() + 86400
            else:
                time_diff = (time - join_time).total_seconds()

            if ip_home:
                time_diffs_school.append(time_diff)
                ip_home = False
            else:
                time_diffs_home.append(time_diff)

            join_time = None

    return time_diffs_home, time_diffs_school


def plot_time_diffs(time_diffs_home, time_diffs_school):
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))

    axes[0].hist(time_diffs_home, bins=48, color='blue',
                 alpha=0.7, log=True, range=(0, 48))
    axes[1].hist(time_diffs_school, bins=48, color='red',
                 alpha=0.7, log=True, range=(0, 48))

    axes[0].set_title('Other')
    axes[0].set_xlabel('Play Time')
    axes[0].set_ylabel('Frequency (log scale)')
    axes[0].grid(True)
    axes[0].set_xticks([i for i in range(0, 49, 2)])
    axes[0].set_xticklabels(
        [str(i//2) if i % 2 == 0 else "" for i in range(0, 49, 2)])

    axes[1].set_title('University')
    axes[1].set_xlabel('Play Time')
    axes[1].set_ylabel('Frequency (log scale)')
    axes[1].grid(True)
    axes[1].set_xticks([i for i in range(0, 49, 2)])
    axes[1].set_xticklabels(
        [str(i//2) if i % 2 == 0 else "" for i in range(0, 49, 2)])

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
