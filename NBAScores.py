import re
import time
import datetime
import requests
import pandas as pd
from bs4 import BeautifulSoup

startDay = datetime.date(year=2023,month=10,day=24) #NBA SEASON START
today = datetime.date.today()
dayDiff = ((today-startDay).days) #Difference in days from today to season start
dateObjs = [startDay + datetime.timedelta(x) for x in range(dayDiff)] #days in between season start and today - 1 (today won't have scores)

#URL to query scores - might timeout if too many requests - use time.sleep maybe - BASKETBALLREFERENCE - YOU GET A QUERY LIMIT ON THIS
base = r"https://www.basketball-reference.com/boxscores/?month={}&day={}&year={}"

def getTeamScore(teamRes): #needs the result of the the winner/loser table within the "game_summary expanded nohover" table
    tab = teamRes.find_all("td")
    teamName = tab[0].text
    teamScore = int(tab[1].text)
    return teamName,teamScore

data = []
for d in dateObjs:
    url = base.format(d.month,d.day,d.year)
    req = requests.get(url).text
    soup = BeautifulSoup(req)
    gameSumms = soup.find_all("div", {"class": "game_summary expanded nohover"})
    for gs in gameSumms:
        loser,winner = gs.find_all("tr",["winner","loser"])
        winName,winScore = getTeamScore(winner)
        loseTeam,loseScore = getTeamScore(loser)
        totScore = winScore+loseScore
        data.append({"DATE":d.strftime("%Y/%m/%d"),"WINNER":winName,"WIN_SCORE":winScore,"LOSER":loseTeam,"LOSE_SCORE":loseScore,"TOTAL_SCORE":totScore})
    time.sleep(3)

# Scores from Yahoo Sports - didn't get limited here
base = r"https://sports.yahoo.com/nba/scoreboard/?confId=&schedState=2&dateRange={}-{:0>2}-{:0>2}"

outData = []
for d in dateObjs:
    url = base.format(d.year,d.month,d.day)
    req = requests.get(url).text
    soup = BeautifulSoup(req)
    
    scores = soup.find_all("div",{"class":"Whs(nw) D(tbc) Va(m) Fw(b) Fz(27px)"})
    teams = soup.find_all("span",{"data-tst":"first-name"})
    zips = list(zip(teams,scores))
    
    for i in range(0,len(zips),2):
        t1 = zips[i]
        t2 = zips[i+1]
        t1Name,t1Score = t1[0].text,t1[1].text
        t2Name,t2Score = t2[0].text,t2[1].text
        outData.append({"GAME_DATE":d.strftime("%Y%m%d"),"T1_NAME":t1Name,"T1_SCORE":t1Score,"T2_NAME":t2Name,"T2_SCORE":t2Score})
    
    time.sleep(3)
    
df = pd.DataFrame(outData)
