####################################
#
# 'getPrice' module for qqBot by Paszq
# 
# a tool generating an image with details regarding current and historical game pricing
# uses https://gg.deals to get pricing information
# uses https://static.nvidiagrid.net - to check for GeforceNOW support
# 
#   v1.0.0      2022-03-22      Paszq       first version, based on standalone script
#
#####################################
#Count execution time
from datetime import datetime
startTime = datetime.now()

#Imports
import requests #Downloading site
from bs4 import BeautifulSoup #Searching on site
import os #OS operations
import sys #OS operations
import subprocess #Running shell scripts
from difflib import SequenceMatcher #Comparing strings
from PIL import Image, ImageDraw, ImageFont, ImageFilter #Image generation
from io import BytesIO #Downloading an image from URL
import json #JSON read/write capability
from os.path import exists


#Read JSON config
if exists("../../config.json"):
    json_file = open("../../config.json")
elif exists("config.json"):
    json_file = open("config.json")
elif exists("/home/pi/qbot2/config.json"):#Custom path, ex. for crontab purposes
    json_file = open("/home/pi/qbot2/config.json")
else:
    print("No config.json found")
    exit(2)
config = json.load(json_file)

#Basic vars
pathToScript = os.path.dirname(os.path.realpath(__file__))
prettyName = ""

#Functions
def getElementFromSite(site, elementName, elementAttributeName, elementAttribute):
    print("Getting elements from the site...")
    r = requests.get(site, allow_redirects=True)
    f = open(pathToScript+'/temp/temp.html', 'w+')
    f.write(str(r.content))
    f.close()
    html = open(pathToScript+'/temp/temp.html', encoding="utf8", errors='ignore')
    soup = BeautifulSoup(html, 'html.parser')
    #print("Looking for "+elementName+" => "+elementAttributeName+" = "+elementAttribute)
    lines = soup.find_all(elementName, { elementAttributeName : elementAttribute}) + soup.find_all("a", { "class" : "score-grade"})
    #steam = 
    #print(str(steam))
    return lines

def getPrettyName(site):
    r = requests.get(site, allow_redirects=True)
    f = open(pathToScript+'/temp/prettyname.html','w+')
    f.write(str(r.content).replace("\\n","\n").replace("\\t",""))
    f.close()
    html = open(pathToScript+'/temp/prettyname.html', encoding="utf8", errors='ignore')
    soup = BeautifulSoup(html, 'html.parser')
    lines = soup.find_all("h1")
    for line in lines:
        return (str(line).replace("<h1>Buy ","").replace(" PC</h1>","").replace("\\",""))


def checkGamePass(inputLines):
    print("Checking XGP...")
    if len(inputLines) > 0:
        gamePass = 0
        for line in inputLines:
            if "PC Game Pass" in str(line):
                gamePass = 1
        if gamePass == 1:
            return "yes"
        else:
            return "no"
    else:
        return "no"

def checkGeforceNow(gameName):
    print("Checking GFNow...")
    gameName = str(gameName).lower().replace(":","").replace("-"," ").replace("'","")
    #Old source - incomplete, doesn't include EA games
    #inputLines=str(subprocess.check_output("curl -s https://static.nvidiagrid.net/supported-public-game-list/locales/gfnpc-en-US.json|jq '.[] .title'|tr -d '\"' ", shell=True)).split("\\n")
    inputLines=str(subprocess.check_output("curl -s https://www.nvidia.com//content/dam/en-zz/Solutions/geforce/GeForce-experience/games/gamesdata.js| grep \"title:\"| awk -F'title: \"' '{print substr($2, 1, length($2)-3) }'", shell=True)).split("\\n")
    
    bestMatch = ""
    bestRatio = 0
    for line in inputLines:
        line = line.replace("\\xc2","").replace("\\x84","").replace("\\xa2","").replace("\\xe2","").replace("\\xae","").replace("\\x80","").replace("\\x99","").replace("'","").lower()
        s1 = SequenceMatcher(None, gameName, line)
        if s1.ratio() > bestRatio:
            bestMatch = line
            bestRatio = s1.ratio()
    #print(str(bestRatio)+" ==> "+str(bestMatch))
    inputLines=str(subprocess.check_output("curl -s https://static.nvidiagrid.net/supported-public-game-list/locales/gfnpc-en-US.json|jq '.[] .title'|tr -d '\"' ", shell=True)).split("\\n")
    for line in inputLines:
        line = line.replace("\\xc2","").replace("\\x84","").replace("\\xa2","").replace("\\xe2","").replace("\\xae","").replace("\\x80","").replace("\\x99","").replace("'","").lower()
        s1 = SequenceMatcher(None, gameName, line)
        if s1.ratio() > bestRatio:
            bestMatch = line
            bestRatio = s1.ratio()
    #print(str(bestRatio)+" ==> "+str(bestMatch))
    if bestRatio > 0.93:
        return "yes"
    else:
        return "no"

def check_early_access(soup):
    try:
        early_access_header = soup.find('h1', class_='inset')
        if early_access_header and "Early Access Game" in early_access_header.get_text(strip=True):
            return True
        return False
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def check_tag(soup, tag_to_check):
    try:
        tags = soup.find_all('a', class_='app_tag')
        for tag in tags:
            tag_text = tag.get_text(strip=True)
            if tag_text.lower() == tag_to_check:
                return True
        return False
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


        
def get_game_details(appid):
    print("Getting game details...")
    url = f'https://store.steampowered.com/api/appdetails?appids={appid}&l=english'
    reviewurl = f'https://store.steampowered.com/appreviews/{appid}?json=1&l=english'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        #print(str(data))
        if str(appid) in data and data[str(appid)]['success']:
            game_data = data[str(appid)]['data']
            release_date = game_data.get('release_date', {}).get('date', 'N/A')
            #print("!!!!!!!!"+str(release_date))
            total_reviews = game_data.get('recommendations', {}).get('total', 'N/A')
            metacritic_score = game_data.get('metacritic', {}).get('score', 'N/A')
            
        else:
            print("1 Game not found.")
            return "N/A"
        
        response = requests.get(reviewurl)
        response.raise_for_status()
        data = response.json()
        if data['success']:
            game_data = data
            reviews_info = game_data.get('query_summary', {})
            print(str(reviews_info))
            review_score_desc = reviews_info.get('review_score_desc', 'N/A')
            total_positive = reviews_info.get('total_positive', 'N/A')
            total_negative = reviews_info.get('total_negative', 'N/A')
            total_number_of_reviews = total_positive + total_negative
            percent_positive = int((total_positive / max(total_number_of_reviews,1)) * 100)
            #user_review_score = f"{review_score_desc} ({total_positive}:{total_negative})"
            user_review_score = f"{percent_positive}%"
            #return (str(user_review_score))
        else:
            print("2 Game not found.")
            return "N/A"
        return total_reviews, metacritic_score, user_review_score, release_date, total_number_of_reviews
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return "N/A"


def get_latest_game_news(appid):
    print("Getting latest game news...")
    url = f'http://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid={appid}&count=10&maxlength=300&l=english'
    try:
        #print("ABCCCCCC2222")
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        news_data = response.json()
        if 'appnews' in news_data and 'newsitems' in news_data['appnews']:
            news_items = news_data['appnews']['newsitems']
            formatted_news = []
            for news in news_items:
                #print("NEWS!")
                if news.get('feed_type') == 1:
                    title = news.get('title', 'No title available')
                    date = datetime.utcfromtimestamp(news.get('date')).strftime('%Y-%m')
                    formatted_news.append(f"{title} ({date})")
                    if len(formatted_news) == 5:
                        break
                
            if formatted_news:
                return str(', '.join(formatted_news))
            else:
                for news in news_items:
                    #print("NEWS!")
                    if news.get('feed_type') == 0:
                        title = news.get('title', 'No title available')
                        date = datetime.utcfromtimestamp(news.get('date')).strftime('%Y-%m')
                        formatted_news.append(f"{title} ({date})")
                        if len(formatted_news) == 5:
                            break
                if formatted_news:
                    return str(', '.join(formatted_news))
                else:
                    print("No relevant news items found.")
        else:
            print("Invalid response structure.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def printPrices(currentName, inputLines, siteurl):
    print("Printing prices... currentName:"+currentName+"")
    #print("inputLines:"+str(inputLines))
    print("len input lines:"+str(len(inputLines)))
    #print("siteurl:"+siteurl)
    if len(inputLines) > 0:
        inputLines = str(inputLines[:10]).replace('</a>','\n')
        inputLines = inputLines.split("\n")
        #Get official price
        officialPrice = "-"
        foundOfficial = 0
        keyshopPrice = "-"
        gamePass = 0
        historicalLow = "1000000000"
        steamLink = "-"
        #Find first line with price
        x=0
        ofiNotFound = 1
        keyNotFound = 1
        hisNotFound = 2
        steamId = ""
        early = "no"
        single = "no"
        multi = "no"
        coop = "no"
        shooter = "no"
        rpg = "no"
        puzzle = "no"
        platformer = "no"
        driving = "no"
        simulation = "no"
        sports = "no"
        rhythm = "no"
        action = "no"
        survival = "no"
        adventure = "no"
        openworld = "no"
        storyrich = "no"
        adult = "no"
        for line in inputLines:
            #print("LINE! "+str(line))
            if "empty" in str(line) and "official" in str(line) and ofiNotFound == 1:
                officialPrice = "Unavailable"
                ofiNotFound = 0
            elif "store.steampowered.com" in str(line):
                #print("--------1---")
                #print(line)
                #print("-------2----")
                steamId = str(line).split('store.steampowered.com/app/')[1].split('/')[0]
                #NEWS EMPTY, NOT NEEDED
                newsList = " " #get_latest_game_news(steamId)
                details = get_game_details(steamId)
                
                #Get the site once to run rest of commands on results..
                print("Getting the site to check for EA and tags...")
                url = f'https://store.steampowered.com/app/'+steamId+'/'
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                except requests.exceptions.RequestException as e:
                    print(f"An error occurred: {e}")
                if check_early_access(soup):
                    early = "EA"
                if check_tag(soup, "singleplayer"):
                    single = "SP"
                if check_tag(soup, "multiplayer") or check_tag(soup, "multiplayer"):
                    multi = "MP"
                if check_tag(soup, "co-op"):
                    coop = "co-op"
                # GENRE SCAN
                if check_tag(soup, "shooter"):
                    shooter = "shooter"
                if check_tag(soup, "rpg"):
                    rpg = "rpg"
                if check_tag(soup, "puzzle"):
                    puzzle = "puzzle"
                if check_tag(soup, "platformer"):
                    platformer = "platformer"
                if check_tag(soup, "driving"):
                    driving = "driving"
                if check_tag(soup, "simulation"):
                    simulation = "simulation"
                if check_tag(soup, "sports"):
                    sports = "sports"
                if check_tag(soup, "rhythm"):
                    rhythm = "rhythm"
                if check_tag(soup, "action"):
                    action = "action"
                if check_tag(soup, "survival"):
                    survival = "survival"
                if check_tag(soup, "adventure"):
                    adventure = "adventure"
                if check_tag(soup, "open world"):
                    openworld = "openworld"
                if check_tag(soup, "story rich"):
                    storyrich = "story rich"
                if check_tag(soup, "sexual content"):
                    adult = "adult"
                total_reviews = details[0]
                metacritic = details[1]
                user_reviews = details[2]
                #print("USER REVIEWS: "+user_reviews)
                release_date = details[3]
                total_number_of_reviews = details[4]
                #print(details[2])
            elif "empty" in str(line) and "keyshop" in str(line) and keyNotFound == 1:
                keyshopPrice = "Unavailable"
                keyNotFound = 0
                #print(details[2])
            elif "empty" in str(line) and "histor" in str(line) and hisNotFound == 1:
                historicalLow = "Unavailable"
            elif "official" in str(line) and "numeric" in str(line) and ofiNotFound == 1:
                #Cut off everything before 'numerical' and after next SLASH
                if "Free" in str(line):
                    officialPrice = "Free"
                else:
                    officialPrice = str(line).split('<span class="price-inner numeric">')[1].split("\\")[0]
                ofiNotFound = 0
            elif "keyshop" in str(line) and "numeric" in str(line) and keyNotFound == 1:
                keyshopPrice = str(line).split('<span class="price-inner numeric">')[1].split("\\")[0]
                keyNotFound = 0
            elif "histor" in str(line) and "numeric" in str(line) and hisNotFound != 0:
                newCandidate = str(line).split('<span class="price-inner numeric">')[1].split("\\")[0]
                if "Free" not in str(newCandidate) and "Free" not in str(historicalLow):
                    if historicalLow != "Unavailable":
                        if float(newCandidate.replace(",",".").replace("~","")) < float(historicalLow.replace(",",".").replace("~","")):
                            historicalLow = newCandidate
                else:
                    historicalLow = "Free"
                hisNotFound -= 1
            x+=1
        #-----------FINAL PRINT PART 1----------------
        csv = open(pathToScript+"/output/result.csv",'w+')
        getPrettyName(siteurl)
        csv.write(currentName+"\n")
        csv.write(""+siteurl+"\n")
        if officialPrice != "Unavailable" and "Free" not in str(officialPrice):
            officialPrice += "€"
        if keyshopPrice != "Unavailable":
            keyshopPrice += "€"
        if historicalLow != "Unavailable":
            if "Free" not in str(historicalLow):
                if float(historicalLow.replace(",",".").replace("~","")) > 10000:
                    historicalLow = "Unavailable"
            else:
                historicalLow = "Free"
        if historicalLow != "Unavailable" and "Free" not in str(historicalLow):
            historicalLow += "€"
        #-----------FINAL PRINT PART 2--------------
        csv.write(str(officialPrice)+"\n")
        csv.write(str(keyshopPrice)+"\n")
        csv.write(str(historicalLow)+"\n")
        csv.write(checkGamePass(getElementFromSite(siteurl, "span", "class", "game-info-title title no-icons"))+"\n")
        csv.write(str(checkGeforceNow(currentName))+"\n")
        if steamId != "":
            #print("Steamid: "+steamId)
            csv.write("https://store.steampowered.com/app/"+str(steamId)+"/\n")
            #print("Steamid 2")
            csv.write(str(newsList)+"\n") #News
            csv.write(str(user_reviews)+"\n") #Reviews
            csv.write(str(total_number_of_reviews)+"\n") #Reviews
            csv.write(str(release_date)+"\n")
        else:
            csv.write("no link\n")
            csv.write("no news\n")
            csv.write("no reviews\n")
            csv.write("no reviews\n")
            csv.write("no release\n")
        #static.nvidiagrid.net/supported-public-game-list/locales/gfnpc-en-US.json", "span", "class", "game-name"))
        imageurl = " "
        #imageurl = getImageUrl(siteurl)
        if imageurl != None and imageurl != "":
            csv.write(imageurl+"\n")
        else:
            csv.write("no image\n")
        csv.write(early+"\n")
        csv.write(single+"\n")
        csv.write(multi+"\n")
        csv.write(coop+"\n")
        csv.write(shooter+"\n")
        csv.write(rpg+"\n")
        csv.write(puzzle+"\n")
        csv.write(platformer+"\n")
        csv.write(driving+"\n")
        csv.write(simulation+"\n")
        csv.write(sports+"\n")
        csv.write(rhythm+"\n")
        csv.write(action+"\n")
        csv.write(survival+"\n")
        csv.write(adventure+"\n")
        csv.write(openworld+"\n")
        csv.write(storyrich+"\n")
        csv.write(adult)
        print("Returning 0...")
        return 0
    else:
        return 1

def getSimilarName(inputName):
    print("Get similar name...")
    gameName=fixName(inputName)
    gameName = inputName.replace(" - ","-").replace("---","-").replace("-","+")
    siteurl='https://gg.deals/games/?title='+gameName
    r = requests.get(siteurl, allow_redirects=True)
    f = open(pathToScript+'/temp/temp.html', 'w+')
    f.write(str(r.content))
    f.close()
    html = open(pathToScript+'/temp/temp.html', encoding="utf8", errors='ignore')
    soup = BeautifulSoup(html, 'html.parser')
    lines = soup.find_all("a", {"class" : "game-info-title title"})
    #"title-inner"})
    lines = str(lines).replace("<div","\n")
    lines = lines.split(">")[1].split("<")[0]
    returnArray = []
    returnArray.append(lines)
    lines = soup.find_all("a", {"class" : "full-link"})
    lines = str(lines).replace("</a>","\n").replace('<a class="full-link" href="','').split("\n")[0].split("/")[2]
    returnArray.append(lines)
    return returnArray

def buildSiteUrl(inputName):
    gameName=fixName(inputName)
    siteurl='https://gg.deals/eu/region/switch/?return=%2Fgame%2F'+str(gameName)+'%2F&showKeyshops=1'
    return siteurl

def fixName(inputName):

    gameName=str(inputName).replace(" - ","-")
    gameName=gameName.replace(" and ","")
    gameName=gameName.replace("&amp;","").replace("  "," ")
    gameName=gameName.replace("&","").replace("  "," ")
    gameName=str(gameName).replace('\'','-')
    gameName=str(gameName).replace(" ","-").replace("---","-").replace("   "," ").replace("  "," ").replace("  "," ")
    gameName=str(gameName).replace(":","").replace("/","").replace("+","")
    gameName=gameName.replace("&&amp;","").replace("  "," ")

    return gameName

def getImageUrl(siteurl):
    r = requests.get(siteurl, allow_redirects=True)
    lines = str(r.content).split("<")
    for line in lines:
        if "image-game" in str(line):
            return (str(line).split("src=")[1].split(" alt=")[0].replace('"',''))
            break;
        if "game-link-widget" in str(line):
            redirectLink = str(line).split('href="')[1].replace('">','')
            redirectRequest = requests.get(redirectLink, allow_redirects=True)
            targetUrl = str(redirectRequest.url)
            if "steampowered" in targetUrl:
                appId = str(targetUrl).split("/")[-2]
                return "https://steamcdn-a.akamaihd.net/steam/apps/"+appId+"/capsule_231x87.jpg"
                break;
        if "store.steampowered.com/app" in str(line):
            appId= str(line).split("/")[-2]
            return "https://steamcdn-a.akamaihd.net/steam/apps/"+appId+"/capsule_231x87.jpg"
            break;

#Run the script
inputName = str(sys.argv[1])
inputLink = str(sys.argv[2])
#print("inputName: "+inputName)
siteurl = buildSiteUrl(str(inputLink.split("/")[2]))
if printPrices(str(inputName), getElementFromSite(siteurl, "div", "id", "page"), siteurl) == 1:
    #print("---------the other way-----------")
    prettyName = getSimilarName(str(inputName))[0]
    newName = getSimilarName(str(inputName))[1]
    siteurl = buildSiteUrl(newName)
    print("\nSecond run?\n\n")
    printPrices(prettyName, getElementFromSite(siteurl, "div", "id", "game-card"), siteurl)
