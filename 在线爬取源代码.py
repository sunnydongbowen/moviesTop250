#-*- codeing = utf-8 -*-
#@Time : 2021/1/15 0015 11:08
#@Author : dongbowen
#@File: test_001.py
#@Software:PyCharm

from bs4 import BeautifulSoup
import  xlwt
import  re
import  sqlite3
import  urllib.request,urllib.error
import  requests
import time

def main():
    baseurl = 'https://movie.douban.com/top250?start='
    # 1、爬取网页
    datalist = getData(baseurl)
    # for i in datalist:
    #     print(i)
    # 3、保存数据
    #savepath = '豆瓣电影Top250.xls'
    dbpath = 'movie.db'
    saveData2(datalist,dbpath)
    #saveData(datalist,savepath)
# 爬取解析,一共是七项记录，但是每条是8个，名称里区分了中文名和英文名
# 详情链接
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


def getData(baseurl):
    datalist=[]
    for i in range(0,10):                    # 一共10页数据。每一页25条。这里一开始写了25,为什么这样结果能对？
        url = baseurl + str(i*25)
        #time.sleep(3)
        html = askURL(url)    # 保存获取到的网页源码
        #2、解析数据
        soup = BeautifulSoup(html,'html.parser')
        #print(len(soup.find_all('div',class_ ='item')))  25条记录
        for item in soup.find_all('div',class_ ='item'):   # 查询到所有符合条的记录
            #print(item)
            data = [] # 保存一部电影的所有信息
            item = str(item)      #
            #print(item)
            # break
            link = re.findall(findLink,item)[0] # 获取到影片详情链接
            data.append(link)
            #print(link)
            #print(link)
            imgSrc = re.findall(findImgSrc,item)[0]
            data.append(imgSrc)

            titles = re.findall(findtitle,item)
            #print(titles)
            if(len(titles)==2):
                ctitle = titles[0]
                data.append(ctitle)
                otitle = titles[1].replace("/"," ")
                data.append(otitle)
            else:
                data.append(titles[0])
                data.append(' ')

            rating = re.findall(findRating,item)[0]
            data.append(rating)

            judgeNum = re.findall(findJudge,item)[0]
            data.append(judgeNum)

            inq = re.findall(findInq,item)
            if len(inq) !=0:
                inq = inq[0].replace('。','')
                data.append(inq)
            else:
                data.append(' ')

            bd = re.findall(findBd,item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?'," ",bd)
            bd = re.sub('/'," ", bd)
            data.append(bd.strip())
            print(data)
            datalist.append(data)
            #print(datalist)
    return  datalist

# 专门得到指定一个url网页的内容，自己可以看一下爬取下的html文件是什么样子的， 其实每一页都是一个
def askURL(url):
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
    except Exception as result:
       print("发生错误了")
       print(result)
    return  html

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

#askURL('http://www.baidu.com')
if __name__ == '__main__':
    #init_db('movietest.db')
    main()
    print('爬取完成')
