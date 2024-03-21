from bs4 import BeautifulSoup
import requests
import pandas
import datetime
import time
#todo: make sense of the variables sent in the post request, make a post request customizer, allowing to get every potential timetable from the site, make a telegram bot, sending timetables a day before schedule, setup own query API for timetables
def log (message):
    f = open("lograspis.txt", "a")
    f.write(message)
    f.close()
def getheaders():
    return
def getraspis(type=0, studyyear=0, id=0, name=0):
    date = datetime.date.today()
    datef = datetime.date(date.year + int(date.month / 12), ((date.month % 12) + 1), date.day)
    return date, datef
def searchdict(substr, dict):
    for key, value in dict.items():
        if str(substr).lower() in str(key).lower():
            print(key, value)
    return
def getoptions():
    url = "https://raspis.rggu.ru/rasp/2.php"
    types= {'%D0%94','D0%92','D0%97','2''D0%9C','D0%90','D0%A3'}
    studyyears = {"1","2","3","4","5","6"}
    #due to the indexing of groups, a different dict is needed for each combination. todo: datadicts[yeartype] = datadict
    datadict = {}
    for type in types:
        for year in studyyears:
            #time.sleep(1)
            rdata = f'formob={type}&kyrs={year}'
            response = requests.post(url, headers=headers, data = rdata.encode())
            data = BeautifulSoup(response.text, features='lxml')
            for item in data.findAll('option'):
                datadict[item.text] = item.attrs['value']
                print(item.attrs['value'], item.text)
    return datadict
if __name__ == "__main__":
    f = open("lograspis.txt","w")
    f.close()
    url = "https://raspis.rggu.ru/rasp/3.php"
    rdata = f"formob=М&kyrs=2&srok=2024-03-21&caf=748&cafzn=ОИС_ИС+(Группа%3A+1)&sdate_year=2024&sdate_month=03&sdate_day=20&fdate_year=2024&fdate_month=04&fdate_day=20"
    headers = {
        'Accept':'*/*',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection':'keep-alive',
        'Content-Length':str(len(rdata)),
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
        'Host':'raspis.rggu.ru',
        'Origin':'https://raspis.rggu.ru',
        'Referer':'https://raspis.rggu.ru/?formob=%D0%9C&kyrs=2&srok=2024-03-21&caf=748&cafzn=%D0%9E%D0%98%D0%A1_%D0%98%D0%A1+(%D0%93%D1%80%D1%83%D0%BF%D0%BF%D0%B0%3A+1)&sdate_year=2024&sdate_month=03&sdate_day=20&fdate_year=2024&fdate_month=04&fdate_day=20',
        'Sec-Ch-Ua':'"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
        'Sec-Ch-Ua-Mobile':'?0',
        'Sec-Ch-Ua-Platform':'"macOS"',
        'Sec-Fetch-Dest':'empty',
        'Sec-Fetch-Mode':'cors',
        'Sec-Fetch-Site':'same-origin',
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'X-Requested-With':'XMLHttpRequest}',
    }
    response = requests.post(url, headers=headers, data=rdata.encode())
    data = BeautifulSoup(response.text, features='lxml')
    table = ""

    for item in data.findAll('tr'):
        tablerow = ""
        i = 0
        for td in item.findAll('td'):
            i+=1
            tablerow+=td.text+"&"
        if i == 7:
            tablerow = "&"+tablerow
        table+=tablerow+"\n"
    log(table)
    df = pandas.read_table("lograspis.txt", sep='&').iloc[:,:8].fillna(method='ffill')
    print(df)

    url = "https://raspis.rggu.ru/rasp/2.php"
    rdata = 'formob=%D0%94&kyrs=1'
    response = requests.post(url, headers=headers, data = rdata.encode())
    data = BeautifulSoup(response.text, features='lxml')
    #datadict = {}
    #for item in data.findAll('option'):
        #datadict[item.text] = item.attrs['value']
        #print(item.attrs['value'])
        #print(item.text)
    #print(getoptions())
    #print(getraspis())
    searchdict("оис",getoptions())