"""TwinMind 桌面客户端启动入口（打包用）— 启动服务 + 原生桌面窗口。"""
import sys


def main():
    from twinmind.server.app import run_server
    port = 8765
    # 打包后 --desktop 直接进窗口
    run_server(port=port, desktop=True)


if __name__ == "__main__":
    main()
