from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
import time
import json
#todo: make sense of the variables sent in the post request, make a post request customizer, allowing to get every potential timetable from the site, make a telegram bot, sending timetables a day before schedule, setup own query API for timetables
def log (message):
    f = open("lograspis.txt", "a")
    f.write(message)
    f.close()
def getheaders():
    return
def getdate(datenum): # 9 -> 09; 3->03
    if datenum < 10:
        return '0'+str(datenum)
    return str(datenum)
def updateRaspis(type, studyyear, id, name): #type=D0%97 studyyear=2, id=748, name=ОИС_ИС+(Группа%3A+1)
    date = datetime.date.today()
    datef = datetime.date(date.year + int(date.month / 12), ((date.month % 12) + 1), date.day)
    url = "https://raspis.rggu.ru/rasp/3.php" #{str(datef.year) + '-' + getdate(datef.month) + '-' + getdate(datef.day)}
    rdata = f"formob={type}&kyrs={studyyear}&srok=sem&caf={id}&cafzn={name}&sdate_year={date.year}&sdate_month={getdate(date.month)}&sdate_day={getdate(date.day)}&fdate_year={datef.year}&fdate_month={getdate(datef.month)}&fdate_day={getdate(datef.month)}"
    headers = {
        'Accept':'*/*',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection':'keep-alive',
        'Content-Length':str(len(rdata)),
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
        'Host':'raspis.rggu.ru',
        'Origin':'https://raspis.rggu.ru',
        'Referer':'https://raspis.rggu.ru/',
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
    df_list = pd.read_html(response.text, header=0)
    df = df_list[0]
    df['ID'] = id
    #print(df.to_string())
    #df.to_csv("lograspis.csv")
    return df
def searchdict(substr, dict):
    i=0
    result = {}
    for key, value in dict.items():
        if str(substr).lower() in str(key).lower():
            print(key, value)
            result[key] = value
            i+=1
    if i == 0:
        print('no group contains "'+substr+'"')
    return result
def updateOptions():
    url = "https://raspis.rggu.ru/rasp/2.php"
    types= {'%D0%94','%D0%92','%D0%97','2','%D0%9C','%D0%90','%D0%A3'}
    studyyears = {"1","2","3","4","5","6"}
    #due to the indexing of groups, a different dict is needed for each combination. todo: datadicts[yeartype] = datadict
    datadictstype = {}
    for type in types:
        datadictsyear = {}
        for year in studyyears:
            datadict = {}
            time.sleep(1)
            rdata = f'formob={type}&kyrs={year}'
            headers = {
                        'Accept':'*/*',
                        'Accept-Encoding':'gzip, deflate, br',
                        'Accept-Language':'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                        'Connection':'keep-alive',
                        'Content-Length':str(len(rdata)),
                        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                        'Host':'raspis.rggu.ru',
                        'Origin':'https://raspis.rggu.ru',
                        'Referer':'https://raspis.rggu.ru/',
                        'Sec-Ch-Ua':'"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
                        'Sec-Ch-Ua-Mobile':'?0',
                        'Sec-Ch-Ua-Platform':'"macOS"',
                        'Sec-Fetch-Dest':'empty',
                        'Sec-Fetch-Mode':'cors',
                        'Sec-Fetch-Site':'same-origin',
                        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
                        'X-Requested-With':'XMLHttpRequest}',
                    }
            response = requests.post(url, headers=headers, data = rdata.encode())
            data = BeautifulSoup(response.text, features='lxml')
            for item in data.findAll('option'):
                datadict[item.text] = item.attrs['value']
                #print(datadict)
            #print(datadict)
            datadictsyear.update({f'{year}': datadict})
        #print(datadictsyear)
        datadictstype[type] = [datadictsyear]
    export_options(datadictstype)
def export_options(dict):
    with open("logoptions.json","w") as f:
        json.dump(dict,f)
def getcachedoptions():
    with open("logoptions.json","r") as f:
        data = json.load(f)
        #print(data['%D0%97'][0]['2'])   // data[type][0][year] to get data
    return data
def updateAllTimeTables():
    optionsdict = getcachedoptions()
    types= {'%D0%94','%D0%92','%D0%97','2','%D0%9C','%D0%90','%D0%A3'} # Д, В, З, 2, М, А, У
    studyyears = {"1","2","3","4","5","6"}
    d = {'День':[],'Пара':[],'Дата':[],'П\гр':[],'Аудит':[],'Предмет':[],'Тип':[],'Лектор':[],'ID':[]}
    df = pd.DataFrame(data=d)
    for type in types:
        for year in studyyears:
            for itemname, itemID in optionsdict[type][0][year].items():
                time.sleep(1)
                dfnew = updateRaspis(type,year,itemID,itemname)
                df = pd.concat([df,dfnew])
    df.to_csv("lograspis.csv")
def searchForTimetable(type,year,substr):
    optionsdict = getcachedoptions()
    result = searchdict(substr, optionsdict[type][0][year])
    #loadTimetable
    #loadTimetable.loc(ID == ??)
    return result
def loadTimetable():
    return

if __name__ == "__main__":
    #updateRaspis('','','748','') #type=D0%97 studyyear=2, id=748, name=ОИС_ИС+(Группа%3A+1)
    updateOptions()
    updateAllTimeTables()
    #print(searchForTimetable("%D0%9C", '2', 'оис'))
