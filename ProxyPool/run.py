from scheduler import Scheduler
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8') #改变标准输出的默认编码为 utf-8

def main():
    try:
        s = Scheduler()
        s.run()
    except:
        main()

if __name__ == "__main__":
    main()