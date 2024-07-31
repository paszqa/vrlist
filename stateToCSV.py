import subprocess
import json
from os.path import exists
import os
import time

def main_script():
    pathToScript = os.path.dirname(os.path.realpath(__file__))
    startline = 0

    with open(pathToScript + '/temp/lastline', 'r') as lastlinefile:
        for llf in lastlinefile:
            startline = int(llf)
            lastlinefile.close()
            break

    print("[INFO] Startline:" + str(startline) + "\n")

    if startline < 2:
        listresult = open(pathToScript + '/output/listresult', 'w')
    else:
        listresult = open(pathToScript + '/output/listresult', 'a')

    # Open the 'list' file and iterate over each line
    linecounter = startline
    with open(pathToScript + '/gglist', 'r') as file:
        # Skip the first two lines
        if startline > 1:
            for _ in range(startline):
                next(file)
        for line in file:
            lastlinewrite = open(pathToScript + '/temp/lastline', 'w')
            lastlinewrite.write(str(linecounter))
            lastlinewrite.close()
            print("==========" + line.strip() + "=========")
            # Remove leading and trailing whitespaces from each line
            game = line.split(";")[0]
            link = line.split(";")[1]

            # Run the printPrice.py script with the current line as an argument
            print("Running subprocess: python3 " + pathToScript + "/printPrice.py '" + game + "' '" + link + "'\n")
            subprocess.run(['python3', pathToScript + '/printPrice.py', game, link])

            # Print the content of the output/result.csv file
            with open('output/result.csv', 'r') as result_file:
                result_lines = result_file.readlines()
                gameName = result_lines[0].strip()
                ggLink = result_lines[1].strip()
                ofiPrice = result_lines[2].strip()
                keyPrice = result_lines[3].strip()
                hisPrice = result_lines[4].strip()
                xgp = result_lines[5].strip()
                gfn = result_lines[6].strip()
                steamlink = result_lines[7].strip()
                news = result_lines[8].strip()
                reviews = result_lines[9].strip()
                total_number_of_reviews = result_lines[10].strip()
                release_date = result_lines[11].strip()
                early = result_lines[13].strip()
                single = result_lines[14].strip()
                multi = result_lines[15].strip()
                coop = result_lines[16].strip()
                shooter = result_lines[17].strip()
                rpg = result_lines[18].strip()
                puzzle = result_lines[19].strip()
                platformer = result_lines[20].strip()
                driving = result_lines[21].strip()
                simulation = result_lines[22].strip()
                sports = result_lines[23].strip()
                rhythm = result_lines[24].strip()
                action = result_lines[25].strip()
                survival = result_lines[26].strip()
                adventure = result_lines[27].strip()
                openworld = result_lines[28].strip()
                storyrich = result_lines[29].strip()
                adult = result_lines[30].strip()
                sandbox = result_lines[31].strip()
                exploration = result_lines[32].strip()
                relaxing = result_lines[33].strip()
                strategy = result_lines[34].strip()
                towerdefense = result_lines[35].strip()
                print("game:" + gameName)
                print("ggLink:" + ggLink)
                print("ofiPrice:" + ofiPrice)
                print("keyPrice:" + keyPrice)
                print("hisPrice:" + hisPrice)
                print("xgp:" + xgp)
                print("gfn:" + gfn)
                print("steamlink:" + steamlink)
                print("news:" + news)
                print("reviews:" + reviews)
                print("review count:" + total_number_of_reviews)
                print("release:" + release_date)
                print("early:" + early)
                print("GENRES: "+single + ";" + multi + ";" + coop + ";" + shooter + ";" + rpg + ";" + puzzle + ";" + platformer + ";" + driving + ";" + simulation + ";" + sports + ";" + rhythm + ";" + action + ";" + survival + ";" + adventure + ";" + openworld + ";" + storyrich + ";" + adult + ";" + sandbox + ";" + exploration + ";" + relaxing + ";" + strategy + ";" + towerdefense) 
                if len(news) > 115:
                    news = news[:112] + "..."
                listresult.write(gameName + ";" + ggLink + ";" + ofiPrice + ";" + keyPrice + ";" + hisPrice + ";" + xgp + ";" + gfn + ";" + steamlink + ";" + news[:115] + ";" + reviews + ";" + total_number_of_reviews + ";" + release_date + ";" + early + ";" + single + ";" + multi + ";" + coop + ";" + shooter + ";" + rpg + ";" + puzzle + ";" + platformer + ";" + driving + ";" + simulation + ";" + sports + ";" + rhythm + ";" + action + ";" + survival + ";" + adventure + ";" + openworld + ";" + storyrich + ";" + adult + ";" + sandbox + ";" + exploration + ";" + relaxing + ";" + strategy + ";" + towerdefense + "\n")
            linecounter += 1

# Retry mechanism
if __name__ == "__main__":
    while True:
        try:
            main_script()
            print("[SUCCESS] Script completed successfully.")
            break  # Exit the loop if the script completes successfully
        except Exception as e:
            print(f"[ERROR] An error occurred: {e}")
            print("[INFO] Restarting script in 10 seconds...")
            time.sleep(10)
