from threading import Thread

from server import run_mcp
from visual import visual


def main():
    t = Thread(target=run_mcp)
    t.start()
    visual.run()


if __name__ == "__main__":
    main()
