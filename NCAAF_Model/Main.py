import pandas as pd
from sklearn import linear_model
import numpy as np
import json
from fuzzywuzzy import process, fuzz
import os
import sys
import time
from bs4 import BeautifulSoup
import requests
from datetime import date
from datetime import timedelta

def CreateDirs():
    try:
        os.mkdir('Data')
    except:
        pass

def FetchStats(year, week):
    try:
        os.mkdir("Data/{}".format(year))
    except:
        pass
    url = 'https://www.sports-reference.com/cfb/years/{}-ratings.html'.format(year)
    FilePath = 'Data/{}/Week{}Ratings.csv'.format(year, week)

    response = requests.get(url)
    html = response.content
    soup = BeautifulSoup(html, features='html.parser')

    soup = soup.find('div', attrs={'id': 'all_ratings'})
    soup = soup.find('table', attrs={'id':'ratings'})
    Headers = soup.find('thead')
    Headers = Headers.find_all('tr')[1]
    Headers = Headers.find_all('th')
    for i in range(len(Headers)):
        Headers[i] = Headers[i].getText()
    Headers[11], Headers[12], Headers[13], Headers[14],Headers[15],Headers[16] = 'PYdPer', 'OPYdPer', 'RYdPer', 'ORYdPer','YdPer', 'OYdPer'
    Stats = soup.find('tbody')
    Stats = Stats.find_all('tr')
    newStats = []
    for i in Stats:
        if not i.has_attr('class'):
            newStats.append(i)
    StatArray = []
    for i in newStats:
        tempList = []
        h = i.find('th').getText()
        tempList.append(h)
        j = i.find_all('td')
        for k in j:
            tempList.append(k.getText())
        StatArray.append(tempList)

    StatDict = {}
    d = 0
    for i in Headers:
        D = []
        for j in StatArray:
            D.append(j[d])
        StatDict[i] = D
        d += 1

    df = pd.DataFrame(StatDict)
    df.to_csv(FilePath)
    print ("Done grabbing stats for Week {} of the {} season!".format(week,year))

def FetchScores(year, week):
    startdates = ['2014-08-28', '2015-09-03', '2016-09-02', '2017-08-31', '2018-08-31', '2019-08-30']
    startdate = startdates[int(year)-2014]
    scrapeDates = []
    for i in range(week):
        newdate = str(date.fromisoformat(startdate) + timedelta(weeks=i))
        scrapeDates.append(newdate)

    scoreJSON = {}
    for i in scrapeDates:
        url = 'https://www.covers.com/sports/ncaaf/matchups?selectedDate={}'.format(i)
        response = requests.get(url)
        html = response.content
        soup = BeautifulSoup(html, features='html.parser')

        soup = soup.find('div', attrs={'id': 'content'})
        soup = soup.find_all('div')
        newsoup = []
        for i in soup:
            if i.has_attr('data-todays-date'):
                newsoup.append(i)

        newsoup = newsoup[0]
        newsoup = newsoup.find_all('div', attrs={'class': 'cmg_matchup_group'})
        newnewsoup = []
        clk = 0
        for i in newsoup:
            h = i.find_all('div')
            for j in h:
                if j.has_attr('data-home-score'):
                    newnewsoup.append(j)

        gJSON = {}
        for i in newnewsoup:
            HTeam, ATeam = i.get('data-home-team-fullname-search'), i.get('data-away-team-fullname-search')
            HScore, AScore = i.get('data-home-score'), i.get('data-away-score')
            HSpread, OU = i.get('data-game-odd'), i.get('data-game-total')
            games = {}
            if HSpread != '':
                clk += 1
                games['HTeam'], games['ATeam'] = HTeam, ATeam
                games['HScore'], games['AScore'] = HScore, AScore
                games['HSpread'], games['OU'] = HSpread, OU
            if len(games) > 0:
                gJSON[clk] = games
                # print (games)

        scoreJSON[str(i)] = gJSON
        print("Odds provided for {} games on {}".format(clk, i))

    print(scoreJSON)
    print(len(scoreJSON))

    new = json.dumps(scoreJSON)
    with open("Data/{}/ScrapeScores.json".format(year), 'w') as file:
        file.write(new)

############################## ACTIONABLE CODE BELOW ######################################################
years = [2014,2015,2016,2017,2018,2019]
FetchScores(2019,14)
#for year in years:
#    FetchScores(year,14)