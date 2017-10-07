---
---
# Introduction
Here, you can access the datasets and source code used in our IMC'17 paper: [**An Empirical Characterization of IFTTT: Ecosystem, Usage, and Performance**](https://www.cs.indiana.edu/~fengqian/paper/ifttt_imc17.pdf). For details on those sourcec code and datasets, please read through this page. If you have any questions, please [contact me](mailto:xmi@indiana.edu). When you use our datasets or source code in any publications, please refer to our work.
```
Xianghang Mi, Feng Qian, Ying Zhang, and XiaoFeng Wang. 
An Empirical Characterization of IFTTT: Ecosystem, Usage, and Performance. 
In Proceedings of IMC ’17. ACM, New York, NY, USA, 7 pages. 
https://doi. org/10.1145/3131365.3131369
```

# Source Code
The source code consists of three parts.
- [**Data Crawling**](https://github.com/mixianghang/IFTTT_measurement/tree/master/datacrawling)
    
  Scripts to crawl IFTTT pages for Services and Applets.

- [**Testbed**](https://github.com/mixianghang/IFTTT_measurement/tree/master/testbed)

  The testbed to measure performance of applet execution. 

- [**Measurement**](https://github.com/mixianghang/IFTTT_measurement/tree/master/measurements)

  Scripts to measure IFTTT usage.

# Datasets

## Dataset List
We ran a weekly job to crawl IFTTT for Services and Applets from Nov 2016 to May 2017. Here, we provide one snaptshot for each month as shown bellow.

Date | Download | Download
:-----: | :---: | :---:
`Nov 2016` | [**TAR.GZ**]({{ "download/201611.tar.gz" }}) | [**7Z**]({{ "download/201611.7z" }})
`Dec 2016` | [**TAR.GZ**]({{ "download/201612.tar.gz" }}) | [**7Z**]({{ "download/201612.7z" }})
`Jan 2017` | [**TAR.GZ**]({{ "download/201701.tar.gz" }}) | [**7Z**]({{ "download/201701.7z" }})
`Feb 2017` | [**TAR.GZ**]({{ "download/201702.tar.gz" }}) | [**7Z**]({{ "download/201702.7z" }})
`Mar 2017` | [**TAR.GZ**]({{ "download/201703.tar.gz" }}) | [**7Z**]({{ "download/201703.7z" }})
`Apr 2017` | [**TAR.GZ**]({{ "download/201704.tar.gz" }}) | [**7Z**]({{ "download/201704.7z" }})
`May 2017` | [**TAR.GZ**]({{ "download/201705.tar.gz" }}) | [**7Z**]({{ "download/201705.7z" }})

## Dataset Descriptions
In each snapshot, you will find the following files.
- **channelList.json**

  Each line of this file is the json string of an IFTTT service(channel). The json format is shown as below.
  ```json
{
    "channelId": "1172726678",
    "channelImgUrl": "https://applets.imgix.net/https%3A%2F%2Fassets.ifttt.com%2Fimages%2Fchannels%2F1172726678%2Fi
cons%2Fon_color_large.png%3Fversion%3D0?ixlib=rails-2.1.3&w=240&h=240&auto=compress&s=beb5a3409a4687d2eda784478ff9b
6c7",
    "channelName": "Amazon Alexa (US only)",
    "channelUrl": "https://ifttt.com/amazon_alexa"
} 
  ```
- **triggerList.json**

  Each IFTTT service may consist of multiple triggers and actions. This file lists all the triggers captured in current snapshot.
  ```json
{
    "triggerChannelId": "1172726678",
    "triggerChannelName": "Amazon Alexa (US only)",
    "triggerChannelUrl": "https://ifttt.com/amazon_alexa",
    "triggerDesc": "This Trigger fires every time you say \"Alexa trigger\" + the phrase that you have defined. For
 instance, if you set \"find my phone\" as the phrase, you can say \"Alexa trigger find my phone\" to make your pho
ne ring. Please use lower-case only.",
    "triggerFieldList": [
        "What phrase?"
    ],   
    "triggerId": null,
    "triggerIngList": [],
    "triggerTitle": "Say a specific phrase",
    "triggerUrl": null
}
  ```
- **actionList.json**

  Each IFTTT service may consist of multiple triggers and actions. This file lists all actionss captured in current snapshot.
  ```json
{
    "actionChannelId": "71",
    "actionChannelName": "Philips Hue",
    "actionChannelUrl": "https://ifttt.com/hue",
    "actionDesc": "This Action will turn on your hue lights.",
    "actionFieldList": [
        "Which lights?"
    ],  
    "actionId": null,
    "actionTitle": "Turn on lights",
    "actionUrl": null
}

  ```
- **channelDetailList.json**

   This file simply combine the aforementioned 3 files with each line repsenting an IFTTT service and related triggers and actions.

- **recipes.json**

   This file stores all applets(recipes) crawled in current snapshots.

   ```json
{
    "actionChannelId": "71",
    "actionChannelTitle": "Philips Hue",
    "actionChannelUrl": "https://ifttt.com//hue",
    "actionDesc": null,
    "actionId": -1, 
    "actionTitle": "Turn on lights",
    "addCount": "71k",
    "creatorName": "bsaren",
    "creatorUrl": "https://ifttt.com//maker/bsaren",
    "desc": "Never be left in the dark. Whenever the sun starts to set, your Philips Hue bulbs will automatically t
urn on.",
    "favoritesCount": -1, 
    "isDoRecipe": false,
    "title": "Automatically turn your lights on at sunset",
    "triggerChannelId": "7",
    "triggerChannelTitle": "Weather Underground",
    "triggerChannelUrl": "https://ifttt.com//weather",
    "triggerDesc": null,
    "triggerId": -1, 
    "triggerTitle": "Sunset",
    "url": "https://ifttt.com/applets/94447p-automatically-turn-your-lights-on-at-sunset"
}
   ```

