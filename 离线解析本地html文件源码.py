#-*- codeing = utf-8 -*-
#@Time : 2021/1/20 0020 14:23
#@Author : dongbowen
#@File: 001.py
#@Software:PyCharm
'''
爬取整个静态页面,然后去解析
'''
import  requests
import  re
from bs4 import BeautifulSoup
import  sqlite3
import  xlwt

file = open('index.html','rb')
html = file.read()
soup = BeautifulSoup(html,'html.parser')
datalist = []
baseurl = 'https://movie.douban.com/top250?start='

savepath = '豆瓣电影Top250离线版.xls'
dbpath = 'movieoffline.db'

findLink = re.compile(r'<a href="(.*?)"')  # 创建正则表达式对象，表示规则（字符串模式）,影片详情链接
# 图片链接
findImgSrc = re.compile(r'<img.*src="(.*?)"',re.S)
# 标题
findtitle = re.compile(r'<span class="title">(.*)</span>')
#评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
# 评价人数
findJudge  =re.compile(r'<span>(\d*)人评价</span>')
# 找到概况
findInq = re.compile(r'<span class="inq">(.*)</span>')
# 找到影片相关内容
findBd = re.compile(r'<p class="">(.*?)</p>',re.S)

def askURL(url):
    '''
    请求url，保存html到html文件
    '''
    head={
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36"
    }
    #request = requests.get(url=url,headers=head)
    html = ''
    try:
        res = requests.get(url=url, headers=head)
        #print(res.text)
        html = res.text
        #print(html)
        with open('index.html','a',encoding='utf-8') as f:
            f.write(html)
    except Exception as result:
       print("发生错误了")
       print(result)
    return  html

def  savehtmlall(baseurl):
    '''
    请求所有页面, 并且保存下来，换一种方式，这样我们去读这个文件来提取我们需要的数据，这样是不是就知道
    '''
    for i in range(0,10):
        url = baseurl+str(i*25)
        askURL(url)

def getData():
    for item in soup.find_all('div', class_='item'):  # 匹配到所有的，这里会得到一个列表。['<>','<>'....],一条列表就是包含了所有信息，一共有250个 item
        #print(item)
        data = []  # 保存一部电影的所有信息
        item = str(item)  #
        # print(item)
        # break
        link = re.findall(findLink, item)[0]  # 获取到影片详情链接，这里是250条
        data.append(link)
        #print(link)
        #print(data)

        imgSrc = re.findall(findImgSrc, item)[0]
        data.append(imgSrc)

        titles = re.findall(findtitle, item)
        # print(titles)
        if (len(titles) == 2):
            ctitle = titles[0]
            data.append(ctitle)
            otitle = titles[1].replace("/", " ")
            data.append(otitle)
        else:
            data.append(titles[0])
            data.append(' ')

        rating = re.findall(findRating, item)[0]
        data.append(rating)

        judgeNum = re.findall(findJudge, item)[0]
        data.append(judgeNum)

        inq = re.findall(findInq, item)
        if len(inq) != 0:
            inq = inq[0].replace('。', '')
            data.append(inq)
        else:
            data.append(' ')

        bd = re.findall(findBd, item)[0]
        bd = re.sub('<br(\s+)?/>(\s+)?', " ", bd)
        bd = re.sub('/', " ", bd)
        data.append(bd.strip())
        #print(data)
        datalist.append(data)
        #print(data)
    print(datalist)
    return datalist

# 保存数据
def saveData(datalist,savepath):
    print("save....")
    book = xlwt.Workbook(encoding='utf-8',style_compression=0)
    sheet = book.add_sheet("豆瓣电影Top250",cell_overwrite_ok=True)
    col = ("电影详情链接",'图片链接','影片中文名','影片外国名','评分','评价数','概况','相关信息')
    for i in range(0,8):
        sheet.write(0,i,col[i])
    for i in range(0,250):
        print("第%d条"% (i+1))
        data = datalist[i]
        for j in range(0,8):
            sheet.write(i+1,j,data[j])
    book.save(savepath)

def saveData2(datalist,dbpath):
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()

    for data in datalist:
        for index in range(len(data)):
            if index == 4 or index ==5:
                continue
            data[index] = '"'+data[index]+'"'
        sql = '''
                    insert into movie250(
                    info_link, pic_link, cname, ename, score, rated, instroduction, info)
                    values(%s)'''%",".join(data)
        print(sql)
        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()

def init_db(dbpath):
    sql = '''
      create table movie250
      ( 
      id integer primary key autoincrement,
      info_link text,
      pic_link text,
      cname varchar ,
      ename varchar ,
      score numeric ,
      rated numeric ,
      instroduction text,
      info text
      )   
    '''   # 创建数据报表
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    # savehtmlall(baseurl)
    getData()
    saveData(datalist,savepath)
    #saveData2(datalist,dbpath)