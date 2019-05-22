# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 10:50:38 2019

@author: Pierre
"""
#########################################################################
# Données : Issues de l'API de Google Analytics - 
# Comme illustration Nous allons travailler sur les données du site 
# https://www.networking-morbihan.com 
# Site de l'association Networking Morbihan. 
#################################################################
# Installation Google Analytics API :
# voir sur le site de Google Developers :
# https://developers.google.com/analytics/devguides/reporting/core/v4/quickstart/installed-py
###############################################################################
# Autoriser l'API - Pour utilsir l'API il vous faut créer un projet dans developers.
#####################################################################################
# Il faut aussi installer la bibliothèque spécifique d'accès aux api de Google :
# Ouvrir Anaconda Prompt en mode administrateur et taper :
# pip install --upgrade google-api-python-client
# et 
# pip install --upgrade oauth2client
########################################################################## 
#Code de Hello Analytics API VA fourni par Google qui va nous aider pour se connecter
#à l'API De Google Analytics
# infos sur le sujet 
#https://developers.google.com/analytics/devguides/reporting/core/v4/quickstart/installed-py

"""Hello Analytics Reporting API V4."""

import argparse

from apiclient.discovery import build
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
DISCOVERY_URI = ('https://analyticsreporting.googleapis.com/$discovery/rest')
#Ces codes sont faux mettre les votres
#Fichier json
#CLIENT_SECRETS_PATH = 'client_secret_3XXXXXXX-6mb7tvh1eh0mYYYYYYYYYuvpq8j.apps.googleusercontent.com.json' # Path to client_secrets.json file.
#VIEW_ID = 'XXXXXXXXX' #ID de Global View

#Les bons codes
CLIENT_SECRETS_PATH = 'client_secret_36489228467-6mb7tvh1eh0msnekhkeaeb01vtuvpq8j.apps.googleusercontent.com.json' # Path to client_secrets.json file.
VIEW_ID = '47922230' #ID de Global View


def initialize_analyticsreporting():
  """Initializes the analyticsreporting service object.

  Returns:
    analytics an authorized analyticsreporting service object.
  """
  # Parse command-line arguments.
  parser = argparse.ArgumentParser(
      formatter_class=argparse.RawDescriptionHelpFormatter,
      parents=[tools.argparser])
  flags = parser.parse_args([])

  # Set up a Flow object to be used if we need to authenticate.
  flow = client.flow_from_clientsecrets(
      CLIENT_SECRETS_PATH, scope=SCOPES,
      message=tools.message_if_missing(CLIENT_SECRETS_PATH))

  # Prepare credentials, and authorize HTTP object with them.
  # If the credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # credentials will get written back to a file.
  storage = file.Storage('analyticsreporting.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(flow, storage, flags)
  http = credentials.authorize(http=httplib2.Http())

  # Build the service object.
  analytics = build('analytics', 'v4', http=http, discoveryServiceUrl=DISCOVERY_URI)

  return analytics

#exemple d'appel Fourni par Google  que l'on n'utilisera pas pour notre projet
def get_report(analytics):
  # Use the Analytics Service Object to query the Analytics Reporting API V4.
  return analytics.reports().batchGet(
      body={
        'reportRequests': [
        {
          'viewId': VIEW_ID,
          'dateRanges': [{'startDate': '7daysAgo', 'endDate': 'today'}],
          'metrics': [{'expression': 'ga:sessions'}]
        }]
      }
  ).execute()

#affichage de la réponse : on n'utilsiera pas non plus on privilégiera 
#la transformation de la réponse en dataframe voir plus bas.
def print_response(response):
  """Parses and prints the Analytics Reporting API V4 response"""

  for report in response.get('reports', []):
    columnHeader = report.get('columnHeader', {})
    dimensionHeaders = columnHeader.get('dimensions', [])
    metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])
    rows = report.get('data', {}).get('rows', [])

    for row in rows:
      dimensions = row.get('dimensions', [])
      dateRangeValues = row.get('metrics', [])

      for header, dimension in zip(dimensionHeaders, dimensions):
        print (header + ': ' + dimension)

      for i, values in enumerate(dateRangeValues):
        print ('Date range (' + str(i) + ')')
        for metricHeader, value in zip(metricHeaders, values.get('values')):
          print (metricHeader.get('name') + ': ' + value)

####################### /Fourni par Google 

#######################################################################    
#Transformation de la réponse Google Analytics au format dataframe
#voir ici : 
#https://www.themarketingtechnologist.co/getting-started-with-the-google-analytics-reporting-api-in-python/
          
def dataframe_response(response):
  list = []
  # get report data
  for report in response.get('reports', []):
    # set column headers
    columnHeader = report.get('columnHeader', {})
    dimensionHeaders = columnHeader.get('dimensions', [])
    metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])
    rows = report.get('data', {}).get('rows', [])
    
    for row in rows:
        # create dict for each row
        dict = {}
        dimensions = row.get('dimensions', [])
        dateRangeValues = row.get('metrics', [])

        # fill dict with dimension header (key) and dimension value (value)
        for header, dimension in zip(dimensionHeaders, dimensions):
          dict[header] = dimension

        # fill dict with metric header (key) and metric value (value)
        for i, values in enumerate(dateRangeValues):
          for metric, value in zip(metricHeaders, values.get('values')):
            #set int as int, float a float
            if ',' in value or '.' in value:
              dict[metric.get('name')] = float(value)
            else:
              dict[metric.get('name')] = int(value)

        list.append(dict)
    
    df = pd.DataFrame(list)
    return df
######################################################################

#############################################################
# On démarre ici !!!!
#############################################################
#def main():   #on ne va pas utiliser le main car on reste dans Spyder
#Chargement des bibliothèques utiles
import numpy as np #pour les vecteurs et tableaux notamment
import matplotlib.pyplot as plt  #pour les graphiques
import scipy as sp  #pour l'analyse statistique
import pandas as pd  #pour les Dataframes ou tableaux de données
import seaborn as sns #graphiques étendues
import math #notamment pour sqrt()
from datetime import timedelta
from scipy import stats
#pip install scikit-misc  #pas d'install conda ???
from skmisc import loess  #pour methode Loess compatible avec stat_smooth
#conda install -c conda-forge plotnine
from plotnine import *  #pour ggplot like
#conda install -c conda-forge mizani 
from mizani.breaks import date_breaks  #pour personnaliser les dates affichées

#Changement du répertoire par défaut pour mettre les fichiers de sauvegarde
#dans le même répertoire que le script.
import os
print(os.getcwd())  #verif
#mon répertoire sur ma machine - nécessaire quand on fait tourner le programme 
#par morceaux dans Spyder.
#myPath = "C:/Users/Pierre/CHEMIN"
#os.chdir(myPath) #modification du path
#print(os.getcwd()) #verif

          
#initialisation de la connexion à Google Analytics      
analytics = initialize_analyticsreporting()




##########################################################################
# RECUPERATION DES DONNEES POUR FILTRAGE 
##########################################################################
#Pour mémoire Dimensions & Metrics Explorer 
#https://developers.google.com/analytics/devguides/reporting/core/dimsmets
#Attention le nombre de dimensions est limité à 9 et de Metrics à 10.
def get_gaPVAllYears(analytics):
  # Use the Analytics Service Object to query the Analytics Reporting API V4.
  return analytics.reports().batchGet(
      body={
        'reportRequests': [
        {
          'viewId': VIEW_ID,
           'pageSize': 100000,  #pour dépasser la limite de 1000
          'dateRanges': [{'startDate': "2011-07-01", 'endDate': "2018-12-31"}],
          'metrics': [{'expression': 'ga:pageviews'}],
          'dimensions': [{'name': 'ga:date'},
                         {'name': 'ga:hostname'},
                         {'name': 'ga:browser'},
                         {'name': 'ga:fullReferrer'},
                         {'name': 'ga:sourceMedium'},
                         {'name': 'ga:language'},
                         {'name': 'ga:landingPagePath'},
                         {'name': 'ga:pagePath'},
                         {'name': 'ga:keyword'}],
        }]
      }
  ).execute()
response = get_gaPVAllYears(analytics)
gaPVAllYears = dataframe_response(response)
gaPVAllYears.dtypes
gaPVAllYears.count()  #51717 enregistrements



###############################################################################
#Etape 1 préparation des données
#changement des noms de variables pour manipuler les colonnes.
gaPVAllYears = gaPVAllYears.rename(columns={'ga:browser': 'browser',
                                              'ga:date': 'date',
                                              'ga:fullReferrer': 'fullReferrer',
                                              'ga:hostname': 'hostname',
                                              'ga:keyword': 'keyword',
                                              'ga:landingPagePath': 'landingPagePath',
                                              'ga:language': 'language',
                                              'ga:pagePath': 'pagePath',
                                              'ga:pageviews': 'pageviews',
                                              'ga:sourceMedium': 'sourceMedium'})

#creation de la variable Année à partir de ga:date
gaPVAllYears['Année'] = gaPVAllYears['date'].astype(str).str[:4]

#separation de la variable sourceMedium en source et medium
gaPVAllYears['source'] = gaPVAllYears['sourceMedium'].str.split("/",1, expand = True)[0]
gaPVAllYears['medium'] = gaPVAllYears['sourceMedium'].str.split("/",1, expand = True)[1]

#transformation date string en datetime 
gaPVAllYears.date = pd.to_datetime(gaPVAllYears.date,  format="%Y%m%d")

#replication des lignes en fonction de la valeur de pageviews (dans R : uncount) 
#i.e. : une ligne par page vue
gaPVAllYears = gaPVAllYears.reindex(gaPVAllYears.index.repeat(gaPVAllYears.pageviews))
gaPVAllYears = gaPVAllYears.reset_index(drop=True) #reindexation
gaPVAllYears.pageviews = 1 #tous les pageviews à 1 maintenant

#### Verifs
gaPVAllYears[['date', 'pageviews']]
gaPVAllYears.dtypes
gaPVAllYears.count()  #82559 enregistrements !!!! au  31/12/2018 comme dans R


###############################################################################
# Sauvegarde en csv pour éviter de faire des appels à GA
gaPVAllYears.to_csv("gaPVAllYears.csv", sep=";", index=False)  #séparateur ; 
###############################################################################

#Relecture ############
myDateToParse = ['date']  #pour parser la variable date en datetime sinon object
gaPVAllYears = pd.read_csv("gaPVAllYears.csv", sep=";", dtype={'Année':object}, parse_dates=myDateToParse)
#verifs
gaPVAllYears.dtypes
gaPVAllYears.count()  #82559 enregistrements 
gaPVAllYears.head(20)
##############################################################################

##########################################################################
#Nettoyage des langues suspectes.
##########################################################################
pattern = "^[a-zA-Z]{2,3}([-/][a-zA-Z]{2,3})?$"
indexGoodlang = gaPVAllYears[(gaPVAllYears.language.str.contains(pat=pattern,regex=True)==True)].index
gaPVAllYearsCleanLanguage=gaPVAllYears.iloc[indexGoodlang]
gaPVAllYearsCleanLanguage.reset_index(inplace=True, drop=True)  #reindexation.
gaPVAllYearsCleanLanguage.dtypes
gaPVAllYearsCleanLanguage.count() #76733
gaPVAllYearsCleanLanguage[['date', 'pageviews']]

#creation de la dataframe daily_data par jour
dfDatePV = gaPVAllYearsCleanLanguage[['date', 'pageviews']].copy() #nouveau dataframe avec que la date et le nombre de pages vues
daily_data = dfDatePV.groupby(dfDatePV['date']).count() #
#dans l'opération précédente la date est partie dans l'index et pageviews a pris le décompte
daily_data['date'] = daily_data.index #
daily_data['cnt_ma30'] =  daily_data['pageviews'].rolling(window=30).mean()
daily_data['Année'] = daily_data['date'].astype(str).str[:4]


#Graphique pages vues par jour
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.lineplot(x='date', y='pageviews', hue='Année', data= daily_data,  
                  palette=sns.color_palette("husl",n_colors=8))
fig.suptitle("L'anomalie de fin 2016 a disparu ", fontsize=14, fontweight='bold')
ax.set(xlabel='Année', ylabel='Nbre pages vues / jour',
       title='suite au nettoyage des langues.')
fig.text(.9,-.05,"Nombre de pages vues par jour depuis 2011 \n Données nettoyées variable langue", 
         fontsize=9, ha="right")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#plt.show()
fig.savefig("PV-s2011-Clean-Lang.png", bbox_inches="tight", dpi=600)


#Graphique Moyenne Mobile 30 jours.
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.lineplot(x='date', y='cnt_ma30', hue='Année', data= daily_data,  
                  palette=sns.color_palette("husl",n_colors=8))
fig.suptitle("L'anomalie de fin 2016 a disparu ", fontsize=14, fontweight='bold')
ax.set(xlabel='Année', ylabel='Nbre pages vues / jour en moyenne mobile',
       title='suite au nettoyage des langues.')
fig.text(.9,-.05,"Nombre de pages vues par jour depuis 2011 en moy. mob. 30 j. \n Données nettoyées variable langue", 
         fontsize=9, ha="right")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#plt.show()
fig.savefig("PV-s2011-Clean-Lang-mm30.png", bbox_inches="tight", dpi=600)

###############################################################################
# Sauvegarde en csv 
gaPVAllYearsCleanLanguage.to_csv("gaPVAllYearsCL.csv", sep=";", index=False)  #séparateur ; 
###############################################################################

#Relecture ############
myDateToParse = ['date']  #pour parser la variable date en datetime sinon object
gaPVAllYearsCleanLanguage = pd.read_csv("gaPVAllYearsCL.csv", sep=";", dtype={'Année':object}, parse_dates=myDateToParse)
#verifs
gaPVAllYearsCleanLanguage.dtypes
gaPVAllYearsCleanLanguage.count()  #76733 enregistrements 
gaPVAllYearsCleanLanguage.head(20)
##############################################################################


##########################################################################
#nettoyage des hostnames.
##########################################################################
#Pour faciliter la lecture on va créer une liste de patterns 
#on garde ceux qui nous intéressent
patternGoodHostname = ["networking-morbihan\.com", "translate\.googleusercontent\.com", 
                         "webcache\.googleusercontent\.com", 
                         "networking-morbihan\.com\.googleweblight\.com", 
                         "web\.archive\.org"]

#on regroupe en une seule pattern
pattern = '|'.join(patternGoodHostname)
indexGoodHostname =  gaPVAllYearsCleanLanguage[(gaPVAllYearsCleanLanguage.hostname.str.contains(pat=pattern,regex=True)==True)].index

gaPVAllYearsCleanHost1 = gaPVAllYearsCleanLanguage.iloc[indexGoodHostname]
gaPVAllYearsCleanHost1.reset_index(inplace=True, drop=True)  #reindexation.
gaPVAllYearsCleanHost1.dtypes
gaPVAllYearsCleanHost1.count() #76170 

#on vire loc.networking-morbihan.com qui restait
patternBadHostname = "loc\.networking-morbihan\.com"
#on garde ceux qui ne correspondent pas à la pattern attention ici ==False
indexGoodHostname = gaPVAllYearsCleanHost1[(gaPVAllYearsCleanHost1.hostname.str.contains(pat=patternBadHostname,regex=True)==False)].index
gaPVAllYearsCleanHost = gaPVAllYearsCleanHost1.iloc[indexGoodHostname]
gaPVAllYearsCleanHost.reset_index(inplace=True, drop=True)  #reindexation.
gaPVAllYearsCleanHost.dtypes
gaPVAllYearsCleanHost.count() #76159

#creation de la dataframe daily_data par jour
dfDatePV = gaPVAllYearsCleanHost[['date', 'pageviews']].copy() #nouveau dataframe avec que la date et le nombre de pages vues
daily_data = dfDatePV.groupby(dfDatePV['date']).count() #
#dans l'opération précédente la date est partie dans l'index
daily_data['date'] = daily_data.index #
daily_data['cnt_ma30'] =  daily_data['pageviews'].rolling(window=30).mean()
daily_data['Année'] = daily_data['date'].astype(str).str[:4]


#Graphique pages vues par jour
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.lineplot(x='date', y='pageviews', hue='Année', data= daily_data,  
                  palette=sns.color_palette("husl",n_colors=8))
fig.suptitle("L'évolution du nombre de pages vues ne se voit pas à l'oeil nu ", fontsize=14, fontweight='bold')
ax.set(xlabel='Année', ylabel='Nbre pages vues / jour',
       title='suite au nettoyage des Hostnames par rapport au nettoyage des langues.')
fig.text(.9,-.05,"Nombre de pages vues par jour depuis 2011 \n Données nettoyées variable hostname", 
         fontsize=9, ha="right")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#plt.show()
fig.savefig("PV-s2011-Clean-Host.png", bbox_inches="tight", dpi=600)


#Graphique Moyenne Mobile 30 jours.
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.lineplot(x='date', y='cnt_ma30', hue='Année', data= daily_data,  
                  palette=sns.color_palette("husl",n_colors=8))
fig.suptitle("L'évolution du nombre de pages vues ne se voit pas à l'oeil nu ", fontsize=14, fontweight='bold')
ax.set(xlabel='Année', ylabel='Nbre pages vues / jour en moyenne mobile',
       title='suite au nettoyage des Hostnames par rapport au nettoyage des langues.')
fig.text(.9,-.05,"Nombre de pages vues par jour depuis 2011 en moy. mob. 30 j. \n Données nettoyées variable hostname", 
         fontsize=9, ha="right")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#plt.show()
fig.savefig("PV-s2011-Clean-Host-mm30.png", bbox_inches="tight", dpi=600)

###############################################################################
# Sauvegarde en csv 
gaPVAllYearsCleanHost.to_csv("gaPVAllYearsCH.csv", sep=";", index=False)  #séparateur ; 
###############################################################################

#Relecture ############
myDateToParse = ['date']  #pour parser la variable date en datetime sinon object
gaPVAllYearsCleanHost = pd.read_csv("gaPVAllYearsCH.csv", sep=";", dtype={'Année':object}, parse_dates=myDateToParse)
#verifs
gaPVAllYearsCleanHost.dtypes
gaPVAllYearsCleanHost.count()  #76159 enregistrements 
gaPVAllYearsCleanHost.head(20)
##############################################################################


##########################################################################
#nettoyage des browser suspects - peut contenir des robots crawlers
##########################################################################
#voyons ce qu'il y a dedans 
gaPVAllYearsCleanHost['browser'].value_counts()
#on vire les "curiosités" et les bots
patternBadBrowser = ["not set","Google\\.com", "en-us", 
                         "GOOG", "PagePeeker\\.com", 
                         "bot"]

#on regroupe en une seule pattern
pattern = '|'.join(patternBadBrowser)
#on garde ceux qui ne correspondent pas à la pattern attention ici ==False
indexGoodBrowser = gaPVAllYearsCleanHost[(gaPVAllYearsCleanHost.browser.str.contains(pat=pattern,regex=True)==False)].index
gaPVAllYearsCleanBrowser = gaPVAllYearsCleanHost.iloc[indexGoodBrowser]
gaPVAllYearsCleanBrowser.reset_index(inplace=True, drop=True)  #reindexation.
gaPVAllYearsCleanBrowser.dtypes
gaPVAllYearsCleanBrowser.count() #76126


#creation de la dataframe daily_data par jour
dfDatePV = gaPVAllYearsCleanBrowser[['date', 'pageviews']].copy() #nouveau dataframe avec que la date et le nombre de pages vues
daily_data = dfDatePV.groupby(dfDatePV['date']).count() #
#dans l'opération précédente la date est partie dans l'index
daily_data['date'] = daily_data.index #
daily_data['cnt_ma30'] =  daily_data['pageviews'].rolling(window=30).mean()
daily_data['Année'] = daily_data['date'].astype(str).str[:4]


#Graphique pages vues par jour
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.lineplot(x='date', y='pageviews', hue='Année', data= daily_data,  
                  palette=sns.color_palette("husl",n_colors=8))
fig.suptitle("L'évolution du nombre de pages vues ne se voit pas à l'oeil nu ", fontsize=14, fontweight='bold')
ax.set(xlabel='Année', ylabel='Nbre pages vues / jour',
       title='suite au nettoyage des browsers suspects par rapport aux nettoyages précédents.')
fig.text(.9,-.05,"Nombre de pages vues par jour depuis 2011 \n Données net. variable browser", 
         fontsize=9, ha="right")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#plt.show()
fig.savefig("PV-s2011-Clean-Browser.png", bbox_inches="tight", dpi=600)


#Graphique Moyenne Mobile 30 jours.
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.lineplot(x='date', y='cnt_ma30', hue='Année', data= daily_data,  
                  palette=sns.color_palette("husl",n_colors=8))
fig.suptitle("L'évolution du nombre de pages vues ne se voit pas à l'oeil nu ", fontsize=14, fontweight='bold')
ax.set(xlabel='Année', ylabel='Nbre pages vues / jour en moyenne mobile',
       title='suite au nettoyage des browsers suspects par rapport aux nettoyages précédents.')
fig.text(.9,-.05,"Nombre de pages vues par jour depuis 2011 en moy. mob. 30 j. \n Données net. variable browser", 
         fontsize=9, ha="right")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#plt.show()
fig.savefig("PV-s2011-Clean-Host-mm30.png", bbox_inches="tight", dpi=600)


###############################################################################
# Sauvegarde en csv 
gaPVAllYearsCleanBrowser.to_csv("gaPVAllYearsCB.csv", sep=";", index=False)  #séparateur ; 
###############################################################################

#Relecture ############
myDateToParse = ['date']  #pour parser la variable date en datetime sinon object
gaPVAllYearsCleanBrowser = pd.read_csv("gaPVAllYearsCB.csv", sep=";", dtype={'Année':object}, parse_dates=myDateToParse)
#verifs
gaPVAllYearsCleanBrowser.dtypes
gaPVAllYearsCleanBrowser.count()  #76126 enregistrements 
gaPVAllYearsCleanBrowser.head(20)
##############################################################################


##########################################################################
#nettoyage des Crawlers Spammers et autres sources de trafic non désirées 
#dans source
##########################################################################
gaPVAllYearsCleanBrowser['source'].value_counts()
gaPVAllYearsCleanSource = gaPVAllYearsCleanBrowser.copy() #=on fait une copie ici 
#la liste des sites et mots clés non désirés est dans un fichier que 
#nous avons créé.
dfBlacklistSites = pd.read_csv("blacklist-source-sites.csv", sep=";")
patternBadSource = dfBlacklistSites["blacksites"].tolist()

#ça plante si on le fait en une fois, on va devoir diviser en paquet
len(patternBadSource)
step = 500
steps = list(range(0, len(patternBadSource), step))
j=0
for i in steps:
    if (i+step < len(patternBadSource) ) :
        imax=i+step
    else :
        imax = len(patternBadSource)
    print("i=",i)
    print("imax=",imax)
    patternBadSourcePack = '|'.join(patternBadSource[i:imax])
    indexGoodSource = gaPVAllYearsCleanSource[(gaPVAllYearsCleanSource.source.str.contains(pat=patternBadSourcePack,regex=True)==False)].index
    print("indexGoodSource size =", indexGoodSource.size)
    gaPVAllYearsCleanSource = gaPVAllYearsCleanSource.iloc[indexGoodSource]
    gaPVAllYearsCleanSource.reset_index(inplace=True, drop=True)  #on reindexe 


gaPVAllYearsCleanSource.reset_index(inplace=True, drop=True)  #reindexation. pas sur que cela serve beaucoup ici 
###################!!!!!!!!!!!!!!!!!!!!!!!!!
gaPVAllYearsCleanSource.dtypes
gaPVAllYearsCleanSource.count() #74275 #même chose qu'avec R !!!!!! 74275 

#pour vérifier ce que l'on a dans la variable
gaPVAllYearsCleanSource['source'].value_counts()
# Sauvegarde en csv 
gaPVAllYearsCleanSource['source'].value_counts().to_csv("gaPVAllYearsCSSC.csv", sep=";")  #séparateur ; 
#########

#creation de la dataframe daily_data par jour
dfDatePV = gaPVAllYearsCleanSource[['date', 'pageviews']].copy() #nouveau dataframe avec que la date et le nombre de pages vues
daily_data = dfDatePV.groupby(dfDatePV['date']).count() #
#dans l'opération précédente la date est partie dans l'index
daily_data['date'] = daily_data.index #
daily_data['cnt_ma30'] =  daily_data['pageviews'].rolling(window=30).mean()
daily_data['Année'] = daily_data['date'].astype(str).str[:4]


#Graphique pages vues par jour
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.lineplot(x='date', y='pageviews', hue='Année', data= daily_data,  
                  palette=sns.color_palette("husl",n_colors=8))
fig.suptitle("L'évolution du nombre de pages vues ne se voit pas à l'oeil nu ", fontsize=14, fontweight='bold')
ax.set(xlabel='Année', ylabel='Nbre pages vues / jour',
       title='suite au nettoyage des referrers suspects par rapport aux nettoyages précédents.')
fig.text(.9,-.05,"Nombre de pages vues par jour depuis 2011 \n Données net. variable source", 
         fontsize=9, ha="right")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#plt.show()
fig.savefig("PV-s2011-Clean-Source.png", bbox_inches="tight", dpi=600)


#Graphique Moyenne Mobile 30 jours.
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.lineplot(x='date', y='cnt_ma30', hue='Année', data= daily_data,  
                  palette=sns.color_palette("husl",n_colors=8))
fig.suptitle("L'évolution du nombre de pages vues ne se voit pas à l'oeil nu ", fontsize=14, fontweight='bold')
ax.set(xlabel='Année', ylabel='Nbre pages vues / jour en moyenne mobile',
       title='suite au nettoyage des referrers suspects par rapport aux nettoyages précédents.')
fig.text(.9,-.05,"Nombre de pages vues par jour depuis 2011 en moy. mob. 30 j. \n Données net. variable source", 
         fontsize=9, ha="right")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#plt.show()
fig.savefig("PV-s2011-Clean-Source-mm30.png", bbox_inches="tight", dpi=600)

###############################################################################
# Sauvegarde en csv 
gaPVAllYearsCleanSource.to_csv("gaPVAllYearsCS.csv", sep=";", index=False)  #séparateur ; 
###############################################################################

#Relecture ############
myDateToParse = ['date']  #pour parser la variable date en datetime sinon object
gaPVAllYearsCleanSource = pd.read_csv("gaPVAllYearsCS.csv", sep=";", dtype={'Année':object}, parse_dates=myDateToParse)
#verifs
gaPVAllYearsCleanSource.dtypes
gaPVAllYearsCleanSource.count()  #74275 enregistrements 
gaPVAllYearsCleanSource.head(20)
##############################################################################


##########################################################################
#nettoyage des fausses pages référentes dans fullReferrer
##########################################################################
gaPVAllYearsCleanFullReferrer = gaPVAllYearsCleanSource.copy() #=on fait une copie ici 
#la liste des pages  non désirées est dans un fichier que 
#nous avons créé.
dfBlacklistFullReferrers = pd.read_csv("blacklist-fullReferrer-Page.csv", sep=";")
patternBadFullReferrer = dfBlacklistFullReferrers["Blackpages"].tolist()

pattern = '|'.join(patternBadFullReferrer)
indexGoodFullReferrer = gaPVAllYearsCleanFullReferrer[(gaPVAllYearsCleanFullReferrer.fullReferrer.str.contains(pat=pattern,regex=True)==False)].index

gaPVAllYearsCleanFullReferrer = gaPVAllYearsCleanFullReferrer.iloc[indexGoodFullReferrer]
gaPVAllYearsCleanFullReferrer.reset_index(inplace=True, drop=True)  #on reindexe 
gaPVAllYearsCleanFullReferrer.count() #73829 #même chose qu'avec R !!!!!! 

#creation de la dataframe daily_data par jour
dfDatePV = gaPVAllYearsCleanFullReferrer[['date', 'pageviews']].copy() #nouveau dataframe avec que la date et le nombre de pages vues
daily_data = dfDatePV.groupby(dfDatePV['date']).count() #
#dans l'opération précédente la date est partie dans l'index
daily_data['date'] = daily_data.index #
daily_data['cnt_ma30'] =  daily_data['pageviews'].rolling(window=30).mean()
daily_data['Année'] = daily_data['date'].astype(str).str[:4]


#Graphique pages vues par jour
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.lineplot(x='date', y='pageviews', hue='Année', data= daily_data,  
                  palette=sns.color_palette("husl",n_colors=8))
fig.suptitle("L'évolution du nombre de pages vues ne se voit pas à l'oeil nu ", fontsize=14, fontweight='bold')
ax.set(xlabel='Année', ylabel='Nbre pages vues / jour',
       title='suite au nettoyage des pages référentes suspectes par rapport aux nettoyages précédents.')
fig.text(.9,-.05,"Nombre de pages vues par jour depuis 2011 \n Données net. variable fullReferrer", 
         fontsize=9, ha="right")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#plt.show()
fig.savefig("PV-s2011-Clean-FullReferrer.png", bbox_inches="tight", dpi=600)


#Graphique Moyenne Mobile 30 jours.
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.lineplot(x='date', y='cnt_ma30', hue='Année', data= daily_data,  
                  palette=sns.color_palette("husl",n_colors=8))
fig.suptitle("L'évolution du nombre de pages vues ne se voit pas à l'oeil nu ", fontsize=14, fontweight='bold')
ax.set(xlabel='Année', ylabel='Nbre pages vues / jour en moyenne mobile',
       title='suite au nettoyage des pages référentes suspectes par rapport aux nettoyages précédents.')
fig.text(.9,-.05,"Nombre de pages vues par jour depuis 2011 en moy. mob. 30 j. \n Données net. variable fullReferrer", 
         fontsize=9, ha="right")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#plt.show()
fig.savefig("PV-s2011-Clean-FullReferrer-mm30.png", bbox_inches="tight", dpi=600)

###############################################################################
# Sauvegarde en csv 
gaPVAllYearsCleanFullReferrer.to_csv("gaPVAllYearsCFR.csv", sep=";", index=False)  #séparateur ; 
###############################################################################

#Relecture ############
myDateToParse = ['date']  #pour parser la variable date en datetime sinon object
gaPVAllYearsFullReferrer = pd.read_csv("gaPVAllYearsCFR.csv", sep=";", dtype={'Année':object}, parse_dates=myDateToParse)
#verifs
gaPVAllYearsCleanFullReferrer.dtypes
gaPVAllYearsCleanFullReferrer.count()  #73829 enregistrements 
gaPVAllYearsCleanFullReferrer.head(20)
##############################################################################

##########################################################################
#nettoyage des pages d'administration dans pagePath
##########################################################################
gaPVAllYearsCleanPagePath = gaPVAllYearsCleanFullReferrer.copy() #=on fait une copie ici 
#on vire les accès à l'administration et les pages vues depuis l'administration
patternBadPagePath = ["/wp-login\\.php", "/wp-admin/", "/cron/", "/?p=\\d", "/wp-admini", 
                     "wadmini", "admini"]

pattern = '|'.join(patternBadPagePath)
indexGoodPagePath  = gaPVAllYearsCleanPagePath[(gaPVAllYearsCleanPagePath.pagePath.str.contains(pat=pattern,regex=True)==False)].index
gaPVAllYearsCleanPagePath = gaPVAllYearsCleanPagePath.iloc[indexGoodPagePath]
gaPVAllYearsCleanPagePath.reset_index(inplace=True, drop=True)  #on reindexe 
gaPVAllYearsCleanPagePath.count() #73301 #même chose qu'avec R !!!!!! 

#creation de la dataframe daily_data par jour
dfDatePV = gaPVAllYearsCleanPagePath[['date', 'pageviews']].copy() #nouveau dataframe avec que la date et le nombre de pages vues
daily_data = dfDatePV.groupby(dfDatePV['date']).count() #
#dans l'opération précédente la date est partie dans l'index
daily_data['date'] = daily_data.index #
daily_data['cnt_ma30'] =  daily_data['pageviews'].rolling(window=30).mean()
daily_data['Année'] = daily_data['date'].astype(str).str[:4]


#Graphique pages vues par jour
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.lineplot(x='date', y='pageviews', hue='Année', data= daily_data,  
                  palette=sns.color_palette("husl",n_colors=8))
fig.suptitle("L'évolution du nombre de pages vues ne se voit pas à l'oeil nu ", fontsize=14, fontweight='bold')
ax.set(xlabel='Année', ylabel='Nbre pages vues / jour',
       title="suite au nettoyage des pages d'administration par rapport aux nettoyages précédents.")
fig.text(.9,-.05,"Nombre de pages vues par jour depuis 2011 \n Données net. variable pagePath", 
         fontsize=9, ha="right")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#plt.show()
fig.savefig("PV-s2011-Clean-PagePath.png", bbox_inches="tight", dpi=600)


#Graphique Moyenne Mobile 30 jours.
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.lineplot(x='date', y='cnt_ma30', hue='Année', data= daily_data,  
                  palette=sns.color_palette("husl",n_colors=8))
fig.suptitle("L'évolution du nombre de pages vues ne se voit pas à l'oeil nu ", fontsize=14, fontweight='bold')
ax.set(xlabel='Année', ylabel='Nbre pages vues / jour en moyenne mobile',
       title="suite au nettoyage des pages d'administration par rapport aux nettoyages précédents.")
fig.text(.9,-.05,"Nombre de pages vues par jour depuis 2011 en moy. mob. 30 j. \n Données net. variable pagePath", 
         fontsize=9, ha="right")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#plt.show()
fig.savefig("PV-s2011-Clean-PagePath-mm30.png", bbox_inches="tight", dpi=600)

###############################################################################
# Sauvegarde en csv 
gaPVAllYearsCleanPagePath.to_csv("gaPVAllYearsCPP.csv", sep=";", index=False)  #séparateur ; 
###############################################################################

#Relecture ############
myDateToParse = ['date']  #pour parser la variable date en datetime sinon object
gaPVAllYearsCleanPagePath = pd.read_csv("gaPVAllYearsCPP.csv", sep=";", dtype={'Année':object}, parse_dates=myDateToParse)
#verifs
gaPVAllYearsCleanPagePath.dtypes
gaPVAllYearsCleanPagePath.count()  #73301 enregistrements 
gaPVAllYearsCleanPagePath.head(20)
##############################################################################


##########################################################################
#nettoyage des pages dont l'entrée sur le site s'est faite 
#via l'administration, variable landingPagePath
##########################################################################
gaPVAllYearsCleanLandingPagePath  = gaPVAllYearsCleanPagePath.copy() #=on fait une copie ici 
patternBadLandingPagePath = ["/wp-login\\.php", "/wp-admin/", "/cron/", "/?p=\\d", "/wp-admini", 
                     "wadmini", "admini"]

pattern = '|'.join(patternBadLandingPagePath)
indexGoodLandingPagePath   = gaPVAllYearsCleanLandingPagePath[(gaPVAllYearsCleanLandingPagePath.landingPagePath.str.contains(pat=pattern,regex=True)==False)].index
gaPVAllYearsCleanLandingPagePath = gaPVAllYearsCleanLandingPagePath.iloc[indexGoodLandingPagePath]
gaPVAllYearsCleanLandingPagePath.reset_index(inplace=True, drop=True)  #on reindexe 
gaPVAllYearsCleanLandingPagePath.count() #72821  même chose qu'avec R !!!!!! 

#creation de la dataframe daily_data par jour
dfDatePV = gaPVAllYearsCleanLandingPagePath[['date', 'pageviews']].copy() #nouveau dataframe avec que la date et le nombre de pages vues
daily_data = dfDatePV.groupby(dfDatePV['date']).count() #
#dans l'opération précédente la date est partie dans l'index
daily_data['date'] = daily_data.index #recrée la colonne date.
daily_data['cnt_ma30'] =  daily_data['pageviews'].rolling(window=30).mean()
daily_data['Année'] = daily_data['date'].astype(str).str[:4]


#Graphique pages vues par jour
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.lineplot(x='date', y='pageviews', hue='Année', data= daily_data,  
                  palette=sns.color_palette("husl",n_colors=8))
fig.suptitle("L'évolution du nombre de pages vues ne se voit pas à l'oeil nu ", fontsize=14, fontweight='bold')
ax.set(xlabel='Année', ylabel='Nbre pages vues / jour',
       title="suite au nettoyage des pages d'administration référentes par rapport aux nettoyages précédents.")
fig.text(.9,-.05,"Nombre de pages vues par jour depuis 2011 \n Données net. variable landingPagePath", 
         fontsize=9, ha="right")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#plt.show()
fig.savefig("PV-s2011-Clean-LandingPagePath.png", bbox_inches="tight", dpi=600)


#Graphique Moyenne Mobile 30 jours.
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.lineplot(x='date', y='cnt_ma30', hue='Année', data= daily_data,  
                  palette=sns.color_palette("husl",n_colors=8))
fig.suptitle("L'évolution du nombre de pages vues ne se voit pas à l'oeil nu ", fontsize=14, fontweight='bold')
ax.set(xlabel='Année', ylabel='Nbre pages vues / jour en moyenne mobile',
       title="suite au nettoyage des pages d'administration référentes par rapport aux nettoyages précédents.")
fig.text(.9,-.05,"Nombre de pages vues par jour depuis 2011 en moy. mob. 30 j. \n Données net. variable landingPagePath", 
         fontsize=9, ha="right")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#plt.show()
fig.savefig("PV-s2011-Clean-LandingPagePath-mm30.png", bbox_inches="tight", dpi=600)

###############################################################################
# Sauvegarde en csv 
gaPVAllYearsCleanLandingPagePath.to_csv("gaPVAllYearsCLPP.csv", sep=";", index=False)  #séparateur ; 
###############################################################################

#Relecture ############
myDateToParse = ['date']  #pour parser la variable date en datetime sinon object
gaPVAllYearsCleanLandingPagePath = pd.read_csv("gaPVAllYearsCLPP.csv", sep=";", dtype={'Année':object}, parse_dates=myDateToParse)
#verifs
gaPVAllYearsCleanLandingPagePath.dtypes
gaPVAllYearsCleanLandingPagePath.count()  #72821 enregistrements 
gaPVAllYearsCleanLandingPagePath.head(20)
##############################################################################

##########################################################################
# Jeu de données nettoyé
##########################################################################
#nom de sauvegarde plus facile à retenir :
dfPageViews = gaPVAllYearsCleanLandingPagePath.copy() #=on fait une copie ici 
###############################################################################
# Sauvegarde en csv 
dfPageViews.to_csv("dfPageViews.csv", sep=";", index=False)  #séparateur ; 
###############################################################################

#Relecture ############
myDateToParse = ['date']  #pour parser la variable date en datetime sinon object
dfPageViews = pd.read_csv("dfPageViews.csv", sep=";", dtype={'Année':object}, parse_dates=myDateToParse)
#verifs
dfPageViews.dtypes
dfPageViews.count()  #72822 enregistrements 
dfPageViews.head(20)
##############################################################################
#creation de la dataframe daily_data par jour
dfDatePV = dfPageViews[['date', 'pageviews']].copy() #nouveau dataframe avec que la date et le nombre de pages vues
daily_data = dfDatePV.groupby(dfDatePV['date']).count() #
#dans l'opération précédente la date est partie dans l'index
daily_data['date'] = daily_data.index #recrée la colonne date.
daily_data['cnt_ma30'] =  daily_data['pageviews'].rolling(window=30).mean()
daily_data['Année'] = daily_data['date'].astype(str).str[:4]
daily_data['DayOfYear'] = daily_data['date'].dt.dayofyear #récupère la date du jour


#Graphique Moyenne Mobile 30 jours.
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.lineplot(x='DayOfYear', y='cnt_ma30', hue='Année', data= daily_data,  
                  palette=sns.color_palette("husl",n_colors=8))
fig.suptitle("Les données présentent une saisonnalité : ", fontsize=14, fontweight='bold')
ax.set(xlabel="Numéro de Jour dans l'année", ylabel='Nbre pages vues / jour en moyenne mobile',
       title="Le trafic baisse en général en été.")
fig.text(.9,-.05,"Comparatif Nbre pages vues par jour  par an moy. mob. 30 jours \n Données nettoyées", 
         fontsize=9, ha="right")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#plt.show()
fig.savefig("PV-Comparatif-mm30.png", bbox_inches="tight", dpi=600)

# Sauvegarde en csv 
daily_data.to_csv("DailyDataCleanPython.csv", sep=";", index=False)  #séparateur ; 


##########################################################################
# MERCI pour votre attention !
##########################################################################
#on reste dans l'IDE
#if __name__ == '__main__':
#  main()







