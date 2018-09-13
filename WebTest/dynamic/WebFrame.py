# 因为要使用正则替换模板文件中的内容，所以先导入模块
import re
# 需要使用数据库操作了，导入数据库模块
from pymysql import Connect
from urllib.parse import unquote
# 实现 WSGI 协议中的 application 接口方法

# 创建一个空字典
router_dict = {}

def application(environ, start_response):
    # 从服务器传过来的字典中将访问路径取出来
    url_path = environ['PATH_INFO']
    # 因为add方法使用了正则,所以在存到字典中的时候实际的值是这样的  {"r'/add/(\d+)\.html'":FunctionName}
    # 利用传进来的访问路径名来找到对应的函数,所以需要使用正则来匹配页面的访问地址
    for path, function in router_dict.items():
        # 通过正则来匹配 path 和传入的访问页面地址
        match = re.match(path,url_path)
        # 判断如果匹配到了页面就调用相应的函数
        if match:
            # 将执行函数得到数据并将返回值赋给 file_content，返回使用
            file_content = function(match)

    # 回调 start_response 函数，将响应状态信息回传给服务器
    start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])
    # 返回响应数据内容
    return file_content


# 实现一个带参的装饰器
def router(url_path):
    print('router')
    def set_func(func):
        print('setfunc')
        def wrapper(*args,**kwargs):
            print('wrapper')
            return func(*args,**kwargs)
        router_dict[url_path] = wrapper
        return wrapper
    return set_func


#首页响应的函数
@router('/index.html')
def index(match):
    # 接着模板文件地址
    path = './templates/index.html'
    # 读取模板文件
    with open(path, 'r') as f:
        content = f.read()
    # 设置显示的数据,将原来的固定数据替换成占位符
    row_str = """ <tr>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>
                        <input type="button" value="添加" id="toAdd" name="toAdd" systemidvaule="%s">
                    </td>
                    </tr>  """
    # 连接数据库
    # 1.连接数据
    # 创建Connection连接
    conn = Connect(host='localhost', port=3306, database='stock_db', user='root', password='123123', charset='utf8')

    # 获得Cursor对象
    cur = conn.cursor()

    # 2 准备执行的 sql 语句字符串
    sql_str = """ select * from info;"""

    # 执行sql
    cur.execute(sql_str)
    # 获取所有的结果
    sql_relust = cur.fetchall()
    # 遍历结果并拼接数据
    all_data = ""
    for t in sql_relust:
        #根据格式字符串中的每项空白,将数据从元组中取出并添加到格式字符串中
        all_data += row_str % (t[0],t[1], t[2], t[3], t[4], t[5], t[6], t[7],t[1])

    # 3. 关闭游标和数据库
    cur.close()
    conn.close()

    # 替换模板中的占位符
    content = re.sub(r'\{%content%\}', all_data, content)
    return content


# 个人中心页面响应的函数
@router('/center.html')
def center(match):
    # 接着模板文件地址
    path = './templates/center.html'
    # 读取模板文件
    with open(path, 'r') as f:
        content = f.read()
    # 设置显示的数据,将原来的固定数据替换成占位符
    row_str = """ <tr>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>
                            <a type="button" class="btn btn-default btn-xs" href="/update/%s.html"> <span class="glyphicon glyphicon-star" aria-hidden="true"></span> 修改 </a>
                        </td>
                        <td>
                            <input type="button" value="删除" id="toDel" name="toDel" systemidvaule="%s">
                        </td>
                    </tr> """
    # 连接数据库
    # 1.连接数据
    # 创建Connection连接
    conn = Connect(host='localhost', port=3306, database='stock_db', user='root', password='123123', charset='utf8')

    # 获得Cursor对象
    cur = conn.cursor()

    # 2 准备执行的 sql 语句字符串
    sql_str = """ select info.code,info.short,info.chg,info.turnover,info.price,info.highs,focus.note_info from info inner join focus where info.id = focus.info_id;"""

    # 执行sql
    cur.execute(sql_str)
    # 获取所有的结果
    sql_relust = cur.fetchall()
    # 遍历结果并拼接数据
    all_data = ""
    for t in sql_relust:
        #根据格式字符串中的每项空白,将数据从元组中取出并添加到格式字符串中
        all_data += row_str % (t[0], t[1], t[2], t[3], t[4], t[5], t[6], t[0],t[0])

    # 3. 关闭游标和数据库
    cur.close()
    conn.close()

    # 替换模板中的占位符
    content = re.sub(r'\{%content%\}', all_data, content)
    return content




@router(r'/add/(\d+).html')
def add(match):
    code = match.group(1)
    print('code:',code)
    conn = Connect(host='localhost',port=3306,database='stock_db',user='root',password='123123',charset='utf8')
    cur = conn.cursor()
    sql_str = ''' select * from focus where info_id in (select id from info where code = %s); '''
    cur.execute(sql_str,(code,))
    ret = cur.fetchone()
    print('ret:',ret)
    if ret:
        body = '添加过'
    else:
        sql_str = '''insert into focus (info_id) select id from info where code = %s; '''
        cur.execute(sql_str,(code,))
        conn.commit()
        body = '成功'

    cur.connection
    conn.close()
    return body


# 删除函数
@router(r'/del/(\d+).html')
def delete(match):
    code = match.group(1)
    conn = Connect(host='localhost',port=3306,database='stock_db',user='root',password='123123',charset='utf8')
    cur = conn.cursor()
    sql_str = ''' delete from focus where info_id = (select id from info where code = %s)'''
    cur.execute(sql_str, (code,))
    conn.commit()
    cur.close()
    conn.close()
    return 'OK'


# 修改页面显示
@router(r'/update/(\d+).html')
def update(match):
    path = './templates/update.html'
    code = match.group(1)
    with open(path,'r') as f:
        file_content = f.read()

    conn = Connect(host='localhost', port=3306, database='stock_db', user='root', password='123123', charset='utf8')
    cur = conn.cursor()
    sql_str = '''select note_info from focus where info_id = (select id from info where code = %s); '''
    cur.execute(sql_str,(code,))
    sql_result = cur.fetchone()
    file_content = re.sub(r'\{%code%\}',code,file_content)
    file_content = re.sub(r'\{%note_info%\}',sql_result[0],file_content)
    return file_content


# 修改提交

@router(r'/update/(\d+)/(.*).html')
def update_commit(match):

    code = match.group(1)
    note_info = match.group(2)
    note_info = unquote(note_info)
    conn = Connect(host='localhost', port=3306, database='stock_db', user='root', password='123123', charset='utf8')
    cur = conn.cursor()
    sql_str = ''' update focus set note_info = %s where info_id = (select id from info where code = %s);'''
    cur.execute(sql_str,(note_info,code))
    conn.commit()
    cur.close()
    conn.close()

    return 'OK'
# 其它页面响应的函数

def other():
    return 'Other Page ...'