import matplotlib.pyplot as plt
import pandas as pd
import tkinter as tk
import json
from datetime import datetime, timedelta
import pytz
from pytz import timezone
import os
from ctypes import windll

#APPLICATION WINDOW
windll.shcore.SetProcessDpiAwareness(True)
window = tk.Tk()
window.title("Frenchcoke's Discord Data Analyzer 1000")
window.geometry("750x500")
#window.tk.call("tk", "scaling", 0.75)

window.resizable(False,False)

#BODY
titleText = tk.Label(window, text = "Frenchcoke's Discord Data Analyzer 1000")
promptText = tk.Label(window, text = "Welcome! Running this will show some keypoints found from the data, a png of graphs,\nand a csv of the gathered data! \nPlease input the file path to the discord data which you requested from them!\n ex. C:Users/frenchcoke/Desktop/DiscordData")
filePathTextInput = tk.Entry(window, width = "60")
statusText = tk.Label(window)

resultsText = tk.Label(window)

def checkInput():
    filePath = filePathTextInput.get()
    try:
        #Compile all CSV from messages
        messageFilePath = filePath + "/messages"

        fillDataFrame = pd.DataFrame()

        tempMessageFilePath = messageFilePath + "/index.json"
        fileText = open(tempMessageFilePath, "r").read()
        IDdict = json.loads(fileText)

        for p1 in os.listdir(messageFilePath):
            if(p1 != "index.json"):
                tempMessageFilePath = messageFilePath + "/" + p1 + "/messages.csv"
                tempFile = pd.read_csv(tempMessageFilePath)
                
                tempMessageFilePath = messageFilePath + "/" + p1 + "/channel.json"
                tempFileText = open(tempMessageFilePath, "r").read()
                tempDict = json.loads(tempFileText)
                
                
                receiverName = IDdict.get(tempDict.get("id"))
                if (str(receiverName)[:20] == "Direct Message with "):
                    tempFile["ReceiverName"] = receiverName[20:]
                else:
                    tempFile["ReceiverName"] = receiverName
                
                #Type 0 = server, Type 1 = 1 on 1 dm, Type 2 = server?, Type 3 = multiple ppl Gc, type 11 = server?
                groupType = tempDict.get("type")
                if(groupType == 0):
                    tempFile["Type"] = "Server"
                elif(groupType == 1):
                    tempFile["Type"] = "Private DM"
                elif(groupType == 3):
                    tempFile["Type"] = "Group Chat"
                elif(groupType == 11):
                    tempFile["Type"] = "Server"
                elif(groupType == 2):
                    tempFile["Type"] = "Server"
                else:
                    tempFile["Type"] = "Unknown"
                
                fillDataFrame = pd.concat([fillDataFrame, tempFile])

        #print(pytz.all_timezones)

        def getYear(timeStamp):
            return timeStamp[:4]

        def getMonth(timeStamp):
            return timeStamp[5:7]

        def getDay(timeStamp):
            return timeStamp[8:10]

        def getTime(timeStamp):
            return timeStamp[11:16]

        def getConvertedTimestamp(timeStamp):
            unconvertedDate = timeStamp[:19]
            format = "%Y-%m-%d %H:%M:%S"
            gmtTimezone = pytz.timezone("GMT")
            unconvertedDate = datetime.strptime(unconvertedDate, format)
            unconvertedDateGMT = gmtTimezone.localize(unconvertedDate)
            
            correctedTime = unconvertedDateGMT.astimezone(timezone("Canada/Mountain"))
            
            correctedTime = (correctedTime.replace(second = 0, minute = 0, hour = correctedTime.hour) + timedelta(hours = correctedTime.minute//30))

            return correctedTime.strftime(format)

        def getNumberOfAttachments(attachmentString):
            return str(attachmentString).count("https:")

        fillDataFrame["New TimeStamp"] = fillDataFrame["Timestamp"].apply(getConvertedTimestamp)

        fillDataFrame["Year"] = fillDataFrame["New TimeStamp"].apply(getYear)
        fillDataFrame["Month"] = fillDataFrame["New TimeStamp"].apply(getMonth)
        fillDataFrame["Day"] = fillDataFrame["New TimeStamp"].apply(getDay)
        fillDataFrame["Time"] = fillDataFrame["New TimeStamp"].apply(getTime)
        fillDataFrame["NumberOfAttachments"] = fillDataFrame["Attachments"].apply(getNumberOfAttachments)
        
        fillDataFrame = fillDataFrame[["Contents", "Day", "Month", "Year", "Time", "Type", "ReceiverName", "NumberOfAttachments"]]
        
        
        
        resultsTextString = "Total messages: " + str(len(fillDataFrame.index)) + "\n"
        
        fig = plt.figure(figsize = (10,8))
        fig.set_tight_layout(True)
        
        ax1 = plt.subplot2grid((8,4) , (0,0), rowspan = 2, colspan = 2)
        ax2 = plt.subplot2grid((8,4) , (0,2), rowspan = 2, colspan = 2)
        ax3 = plt.subplot2grid((8,4) , (2,0), rowspan = 2, colspan = 4)
        ax4 = plt.subplot2grid((8,4) , (4,0), rowspan = 2, colspan = 4)
        ax5 = plt.subplot2grid((8,4) , (6,0), rowspan = 2, colspan = 2)
        ax6 = plt.subplot2grid((8,4) , (6,2), rowspan = 2, colspan = 2)
        #constrained_layout = True
        
        yearSeries = fillDataFrame["Year"].value_counts()
        yearNumbers = []
        yearCounts = []
        for string in yearSeries.index:
            yearNumbers.append(string + " (" + str(yearSeries[string]) + ")")
            yearCounts.append(yearSeries[string])
        ax1.pie(yearCounts,labels = yearNumbers)
        ax1.set(title = "Messages by Year")
        resultsTextString = resultsTextString + " Most messages sent in a year: " + str(yearSeries.iloc[0]) + " messages in " + str(yearSeries.index[0]) + "\n"
        
        receiverSeries = fillDataFrame["ReceiverName"].value_counts()
        receiverNames = []
        receiverCounts = []
        counter = 0
        for string in receiverSeries.index: 
            if(counter == 10):
                break
            receiverNames.append(string)
            receiverCounts.append(receiverSeries[string])
            counter = counter + 1
        ax3.barh(receiverNames, receiverCounts, align = "center")
        ax3.invert_yaxis()
        ax3.yaxis.set_tick_params(labelsize = 9)
        ax3.set(title = "Number of Messages Sent to Top 10 Receivers")
        for receiverName in receiverSeries.index:
            if (receiverName[-5] == "#" or receiverName[-2] == "#"):
                resultsTextString = resultsTextString + " Top user to receive messages: " + receiverName +  " with: " + str(receiverSeries[receiverName]) + " messages" + "\n"
                break
        
        
        timeSeries = fillDataFrame["Time"].value_counts()
        times = ["00:00", "01:00", "02:00", "03:00", "04:00", "05:00", "06:00", "07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00","18:00","19:00", "20:00", "21:00", "22:00", "23:00"]
        timeCounts = []
        for string in times:
            try:
                timeCounts.append(timeSeries[string])
            except: 
                timeCounts.append(0)    
        ax4.bar(times, timeCounts)
        ax4.set(title = "Messages by Time of Day")
        ax4.tick_params(axis="x", labelrotation = 90)
        resultsTextString = resultsTextString + "Most active hour: " + str(timeSeries.index[0]) + " with: " + str(timeSeries.iloc[0]) + " messages" + "\n"
        
        typeSeries = fillDataFrame["Type"].value_counts()
        typeNames = []
        typeCounts = []
        for string in typeSeries.index:
            typeNames.append(string + " (" + str(typeSeries[string]) + ")")
            typeCounts.append(typeSeries[string])
        ax2.pie(typeCounts, labels = typeNames)
        ax2.set(title = "Messages by Type")
        
        #CALCULATE HOW MANY SERVERS JOINED
        serversFilePath = filePath + "/servers/index.json"
        serverIndexFile = open(serversFilePath, "r").read()
        serversDict = json.loads(serverIndexFile)
    
        
        #CALCULATE MOST POPULAR WORDS AND FIND HOW MANY TIMES PINGED
        
        fillDataFrame["Contents"].fillna(value = "", inplace = True)
        wordCount = {}
        pingCounter = 0

        emoteCount = {}
        for phrase in fillDataFrame["Contents"]:
            if (phrase != ""):
                wordList = (str(phrase).lower()).split(" ")
                for word in wordList:
                    if("<@" == word[:2]):
                        pingCounter = pingCounter + 1
                    if("<:" == word[:2] and ">" == word[-1]):
                        emoteText = word.split(":")[1]
                        if ((emoteText in emoteCount) == False):
                            emoteCount[emoteText] = 1
                        else:
                            emoteCount[emoteText] = emoteCount[emoteText] + 1
                    if((str(word) in wordCount) == False):
                        wordCount[str(word)] = 1
                    else:
                        wordCount[str(word)] = wordCount[str(word)] + 1
            else:
                if(("EMPTY" in wordCount) == False):
                    wordCount["EMPTY"] = 1
                else:
                    wordCount["EMPTY"] = wordCount["EMPTY"] + 1

     
        #Make graph of most popular words
        wordCountCopy = wordCount.copy()
        
        loop = 10
        if(len(wordCountCopy) < 10):
            loop = len(wordCountCopy)
        wordNames = []
        wordNamesCount = []
        for _ in range(loop):
            currentMaxWord = max(wordCountCopy, key = wordCountCopy.get)
            wordNames.append(currentMaxWord)
            wordNamesCount.append(wordCountCopy[currentMaxWord])
            wordCountCopy.pop(currentMaxWord)
        
        ax5.barh(wordNames, wordNamesCount, align = "center")
        ax5.invert_yaxis()
        ax5.set_title("Most Used Words")
        ax5.yaxis.set_tick_params(labelsize = 9)
        
        #Make graph of emotes
        emoteCountCopy = emoteCount.copy()
        
        loop = 10
        if (len(emoteCountCopy) < 10):
            loop = len(emoteCountCopy)
        emoteNames = []
        emoteNamesCount = []
        for _ in range(loop):
            tempMaxEmote = max(emoteCountCopy, key = emoteCountCopy.get)
            emoteNames.append(tempMaxEmote)
            emoteNamesCount.append(emoteCountCopy[tempMaxEmote])
            emoteCountCopy.pop(tempMaxEmote)
        
        ax6.barh(emoteNames, emoteNamesCount, align = "center")
        ax6.invert_yaxis()
        ax6.set_title("Most Used Emotes")
        ax6.yaxis.set_tick_params(labelsize = 9)
        
        
        maxKey = max(wordCount, key = wordCount.get)
        resultsTextString = resultsTextString + "Highest message type: " + str(typeSeries.index[0]) + "\n"
        resultsTextString = resultsTextString + "Most used word: \"" + maxKey + "\" used " + str(wordCount[maxKey]) + " times" + "\n"
        
        resultsTextString = resultsTextString + "Times you pinged someone: " + str(pingCounter) + "\n"
        resultsTextString = resultsTextString + "Servers Joined: " + str(len(serversDict)) + "\n"
        #ATTACHMENTS CALCULATION
        resultsTextString = resultsTextString + "Attachments Sent: " + str(fillDataFrame["NumberOfAttachments"].sum()) + "\n"
        
        statusText.config(text = "Success! Created a csv of the data and a png of some graphs!")
        fillDataFrame.to_csv("compiledData.csv")
        fig.savefig("results.png")
        
        resultsText.config(text = resultsTextString)
    except Exception as e:
        print(e)
        statusText.config(text = "Failed!")
        resultsText.config(text = "")

submitButton = tk.Button(window, text = "Submit", command = checkInput)    

titleText.pack()
promptText.pack()
filePathTextInput.pack()
statusText.pack()
submitButton.pack()
resultsText.pack()
window.mainloop()
