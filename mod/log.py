import threading

# 创建锁
lock = threading.Lock()


def write(message):
    # 获取锁
    lock.acquire()
    try:
        # 打开文件并以追加模式写入日志
        with open("log.txt", "a") as file:
            file.write(message + "\n")
    finally:
        # 释放锁
        lock.release()
