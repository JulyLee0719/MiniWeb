#   代码实现:
import multiprocessing
import re
import socket
import sys

from dynamic import WebFrame


class WEBServer(object):
    def __init__(self, port):
        """用来完成整体的控制"""
        # 1. 创建套接字
        self.__tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 用来重新启用占用的端口
        self.__tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # 2. 绑定IP和端口号
        self.__tcp_server_socket.bind(("", port))

        # 3. 设置套接字监听连接数(最大连接数)
        self.__tcp_server_socket.listen(128)

    def __service_client(self, new_socket,frame_module):
        """为这个客户端返回数据"""

        # 1. 接收浏览器发送过来的请求 ，即http请求相关信息
        # GET / HTTP/1.1
        # .....
        request = new_socket.recv(1024).decode("utf-8")
        # 将请求头信息进行按行分解存到列表中
        request_lines = request.splitlines()
        # GET /index.html HTTP/1.1
        # get post put del
        file_name = ""
        # 正则:  [^/]+ 不以/开头的至少一个字符 匹配到/之前
        #      (/[^ ]*) 以分组来匹配第一个字符是/,然后不以空格开始的0到多个字符,也就是空格之前
        #      最后通过匹配可以拿到 请求的路径名  比如:index.html
        ret = re.match(r"[^/]+(/[^ ]*)", request_lines[0])
        # 如果匹配结果 不为none,说明请求地址正确
        if ret:
            # 利用分组得到请求地址的文件名,正则的分组从索引1开始
            file_name = ret.group(1)
            print('FileName:  ' + file_name)
            # 如果请求地址为 / 将文件名设置为index.html,也就是默认访问首页
            if file_name == "/":
                file_name = "/index.html"

        response = "HTTP/1.1 200 OK\r\n"
        response += "\r\n"
        if file_name.endswith('.html'):
            #要先调用这个函数,如果不调用,那么回调函数不能执行,下面拼接数据就会出错
            #根本不同的文件名来向数据处理文件获取对应的数据
            #并将回调函数传入进去
            env = {'PATH_INFO':file_name}
            # 通过传入的框架模块对象调用 application 函数
            body = frame_module.application(env, self.start_response)

            #拼接返回的状态信息
            header = "HTTP/1.1 %s\r\n"%self.status  # 响应头
            #拼接返回的响应头信息
            #因是返回是以列表装元组的形式返回,所以遍历列表,然后拼接元组里的信息
            for t in self.params:
                header += '%s:%s\r\n'%t

            data = header + '\r\n' + body  # 拼接响应信息
            new_socket.send(data.encode('utf-8'))  # 返回响应信息
        else:

            # 2. 返回http格式的数据，给浏览器
            try:
                # 拼接路径,在当前的html目录下找访问的路径对应的文件进行读取
                f = open("./static" + file_name, "rb")
            except:
                # 如果没找到,拼接响应信息并返回信息
                response = "HTTP/1.1 404 NOT FOUND\r\n"
                response += "\r\n"
                response += "------file not found-----"
                new_socket.send(response.encode("utf-8"))
            else:
                # 如果找到对应文件就读取并返回内容
                html_content = f.read()
                f.close()
                # 2.1 准备发送给浏览器的数据---header
                response = "HTTP/1.1 200 OK\r\n"
                response += "\r\n"
                # 如果想在响应体中直接发送文件内的信息,那么在上面读取文件时就不能用rb模式,只能使用r模式,所以下面将响应头和响应体分开发送
                # response += html_content
                # 2.2 准备发送给浏览器的数据
                # 将response header发送给浏览器
                new_socket.send(response.encode("utf-8"))
                # 将response body发送给浏览器
                new_socket.send(html_content)

        # 关闭套接
        new_socket.close()

    # 定义一个成员函数 ,用来回调保存数据使用
    def start_response(self, status, params):
        # 保存返回回来的响应状态和其它响应信息
        self.status = status
        self.params = params

    def run(self,frame_module):
        while True:
            # 4. 等待新客户端的链接
            new_socket, client_addr = self.__tcp_server_socket.accept()

            # 5. 为这个客户端服务
            p = multiprocessing.Process(target=self.__service_client, args=(new_socket,frame_module))
            p.start()
            # 因为新线程在创建过程中会完全复制父线程的运行环境,所以父线程中关闭的只是自己环境中的套接字对象
            # 而新线程中因为被复制的环境中是独立存在的,所以不会受到影响
            new_socket.close()

        # 关闭监听套接字
        self.__tcp_server_socket.close()


def main():
    with open('Server.conf','r') as f:
        conf_str = f.read()
    dict = eval(conf_str)
    port = dict['port']
    module_str = dict['module']
    sys.path.append('dynamic')
    frame_module = __import__(module_str)
    print('----',port,frame_module)
    webServer = WEBServer(port)
    webServer.run(frame_module)


if __name__ == "__main__":
    main()
