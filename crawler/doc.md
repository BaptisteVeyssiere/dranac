## Crawler
The aim goal of the crawler is to help the user to find a string in the twitters API. In this case the string correspond to a hashatg and it will look for with default parameters or those gave by the user/WebUI.  
In order to communicate with the rest of the infrastructure this program takes the form of a REST API which is accessible thanks to the Flask library.  
The crawler is divided into three parts:  
* The first one is responsible for the skeleton of the program. It will launch flask with the good parameter, authenticate the crawler to the twitter API, and the SQL server and load the configuration file. This part will also list the different hashtag search the different user. (*Crawler* class on the file entities.py)  
* The second part will lead the communication between the twitter API and the crawler. Each Hashtag which will be searched by the crawler will be associated with a class and special methods in order to manage them. (*Hashtag* class on the file entities.py)  
* The last one manage the communication with the SQL server, each tweet will be associated with a class then a diagram and push into the SQL server. (*Tweet* class on the file entities.py)

### Arborescence
``` bash
.
|-- app.yaml
|-- crawler.json
|-- entities.py
|-- env.sh
|-- main.py
`-- requirements.txt
```
The crawler is developed in python, easy to use and deploy both for Google App Engine (prod) and for localhost (dev).  
The skeleton is located in the file *entities.py* which contain all the class and methods relative to.  
the file *main.py* will define all the routes use by the API and use all the class define in *entities.py*.  
The requirements.txt is responsible of the package use by the application in order to run and app.yaml is used to deploy in the Google App Engine.  
In order to test the API in localhost, it is recommended to use `source env.sh` which will create a virtual environment with python 3, install all the packages required and deployed the crawler.  
This is to check the whole program with an empty environment in order to avoid problems during the deployment of the application and its fonctioning.  
The configuration file *crawler.json* contains all the arguments use by the API, like the url to communicate with the database (for debug or production) or the deadline which corresponds to the time to live of the hashtag in the database.

### Library
The API is defined with the micro-framework *Flask*, the communication with the database is made by *SQLAlchemy* and the crawler use the library *tweepy* to call the Twitter's API
