## The Architecture
the project is divided into three main parts/program which correspond to three roles the project needs.  
The architecture corresponds to a micro-service project, it allows a more flexible development environment.  
The three parts are the crawler which will communicate with the twitters API and "feed" the database with pre-sorted tweets.  
The second one, the mapreduce, is responsible to compute statistics based on tweets get by the crawler.  
Finally, the medium between the project and the client is the UI program.  
UI program is also the orchestrator of the dranac project. Indeed, it is that part which will request the other services.  
As described before dranac could be defined as micro-services project working in order to deliver a full service for all the client.  
The main purpose of this architecture is threefold:
* First each part is responsible for one task and doesn't prevent other services from working. The upgrade of the platform could be performing service by service without changing the whole project.
* When the platform is up and meet a huge amount of request. Thanks to the kubernetes used by Google App Engin only the services with the most difficulties will be duplicate and not a whole monolithic program. This allows companies to pay less and deploy as they want, where they want. For example: one UI, two crawler and three mapreduce per country which use the service .
* It brings more flexibility in the project. Indeed, for now dranac only use python with Flask to create api, but for other future feature another programming language could be used. Developer are not bound to the same language, same technology and the same way to code.

[diagram]


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
