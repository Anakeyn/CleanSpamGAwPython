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
dfBlacklistFullReferrers = pd.read_csv("blacklist-fullRefferer-Page.csv", sep=";")
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
patternBadLandingPagePath = ["/wp-login\\.php", "/wp-admin/", "/cron/", "/?p=\\d", "admini"]

pattern = '|'.join(patternBadLandingPagePath)
indexGoodLandingPagePath   = gaPVAllYearsCleanLandingPagePath[(gaPVAllYearsCleanLandingPagePath.landingPagePath.str.contains(pat=pattern,regex=True)==False)].index
gaPVAllYearsCleanLandingPagePath = gaPVAllYearsCleanLandingPagePath.iloc[indexGoodLandingPagePath]
gaPVAllYearsCleanLandingPagePath.reset_index(inplace=True, drop=True)  #on reindexe 
gaPVAllYearsCleanLandingPagePath.count() #72822  #même chose qu'avec R !!!!!! 

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
gaPVAllYearsCleanLandingPagePath.count()  #72908 enregistrements 
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
# Détections des événements significatifs - Anomaly Detection
#on utilise une fonction outlier avec comme seuil 2.29 pour trouver
#à peu près le même nombre d'ouliers que dans R.
##########################################################################
daily_data.reset_index(inplace=True, drop=True)  #on reindexe 
#ici z_score = (daily_data['pageviews'] - mean)/std donné par zcore de scipy.stats
#mais que l'on aurait pu calculer.
from  scipy.stats import zscore
daily_data['pageviews_zscore'] = zscore(daily_data['pageviews'])
seuil=2.29  #seuil pour avoir environ 98 outliers
myOutliers = daily_data[daily_data['pageviews_zscore'] > seuil]
len(myOutliers) #pas tout à fait : c'est 97 !!!!

#Graphique Pages vues
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.lineplot(x='date', y='pageviews', data= daily_data)
sns.scatterplot(x='date', y='pageviews', data= myOutliers, color='red')
fig.suptitle( str(len(myOutliers)) + " événements ont été détectés :  ", fontsize=14, fontweight='bold')
ax.set(xlabel="Date", ylabel='Nbre pages vues / jour',
       title="Il y a moins d'événements significatifs les dernières années")
fig.text(.9,-.05,"Evénements significatifs depuis 2011 détectés par calcul des valeurs aberrantes", 
         fontsize=9, ha="right")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#plt.show()
fig.savefig("Anoms-Pageviews-s2011.png", bbox_inches="tight", dpi=600)

#Affichage sur la courbe des moyennes mobiles sur 30 jours
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.lineplot(x='date', y='cnt_ma30', data= daily_data)
sns.scatterplot(x='date', y='cnt_ma30', data= myOutliers, color='red')
fig.suptitle( str(len(myOutliers)) + " événements ont été détectés :  ", fontsize=14, fontweight='bold')
ax.set(xlabel="Date", ylabel='Nbre pages vues en moyenne mobile / jour',
       title="Il y a moins d'événements significatifs les dernières années")
fig.text(.9,-.05,"Evénements significatifs depuis 2011 détectés par calcul des valeurs aberrantes\n moyenne mobile 30 jours", 
         fontsize=9, ha="right")
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#plt.show()
fig.savefig("Anoms-Pageviews-s2011-mm30.png", bbox_inches="tight", dpi=600)

################################################################################
# Récupération des Articles par categories. Les catégories qui nous intéressent 
# sont celles pour lesquelles les administrateurs ont créé des articles qu'ils 
# souhaitaient mettre en avant :   
# "A la une", 
# "Actualités", 
# "Les Autres Rendez-vous",
# "Networking Apéro", 
# "Networking Conseil"
# "Networking Cotravail", 
# L'export de WordPress ne permet pas d'exporter un choix de catégories, on est 
# obligé de faire catégorie par catégorie
################################################################################
#bibliothèque pour fichier xml #conda install -c anaconda lxml
from lxml import etree
#Categorie A La une
xmlNW56Articles = etree.parse("NW56.WP.ALaUne.xml")
links  = [node.text.strip() for node in xmlNW56Articles.xpath("//item//link")]
pubDates = [node.text.strip() for node in xmlNW56Articles.xpath("//item//pubDate")]
dfNW56AlaUne = pd.DataFrame({'links':links,'pubDates':pubDates})
#Categorie "Actualités",
xmlNW56Articles = etree.parse("NW56.WP.Actualites.xml")
links  = [node.text.strip() for node in xmlNW56Articles.xpath("//item//link")]
pubDates = [node.text.strip() for node in xmlNW56Articles.xpath("//item//pubDate")]
dfNW56Actualites = pd.DataFrame({'links':links,'pubDates':pubDates})
#Categorie ""Les Autres Rendez-vous",
xmlNW56Articles = etree.parse("NW56.WP.LesAutresRDV.xml")
links  = [node.text.strip() for node in xmlNW56Articles.xpath("//item//link")]
pubDates = [node.text.strip() for node in xmlNW56Articles.xpath("//item//pubDate")]
dfNW56LesAutresRDV = pd.DataFrame({'links':links,'pubDates':pubDates})
#Categorie "Networking Apéro",
xmlNW56Articles = etree.parse("NW56.WP.NetworkingApero.xml")
links  = [node.text.strip() for node in xmlNW56Articles.xpath("//item//link")]
pubDates = [node.text.strip() for node in xmlNW56Articles.xpath("//item//pubDate")]
dfNW56NetworkingApero = pd.DataFrame({'links':links,'pubDates':pubDates})
#Categorie "Networking Conseil",
xmlNW56Articles = etree.parse("NW56.WP.NetworkingConseil.xml")
links  = [node.text.strip() for node in xmlNW56Articles.xpath("//item//link")]
pubDates = [node.text.strip() for node in xmlNW56Articles.xpath("//item//pubDate")]
dfNW56NetworkingConseil = pd.DataFrame({'links':links,'pubDates':pubDates})
#Categorie "Networking Cotravail",
xmlNW56Articles = etree.parse("NW56.WP.NetworkingCotravail.xml")
links  = [node.text.strip() for node in xmlNW56Articles.xpath("//item//link")]
pubDates = [node.text.strip() for node in xmlNW56Articles.xpath("//item//pubDate")]
dfNW56NetworkingCotravail = pd.DataFrame({'links':links,'pubDates':pubDates})

dfNW56Articles = pd.concat([dfNW56AlaUne, dfNW56Actualites, dfNW56LesAutresRDV, 
                            dfNW56NetworkingApero, dfNW56NetworkingConseil, 
                            dfNW56NetworkingCotravail])

dfNW56Articles.count() #152
dfNW56Articles = dfNW56Articles.drop_duplicates(subset=['links'])
dfNW56Articles.count() #verif - 104 Articles 
dfNW56Articles.dtypes
#création d'une date équivalente à celle dans daily data
dfNW56Articles['date'] = dfNW56Articles.pubDates.str[:16].astype('datetime64[ns]')
dfNW56Articles.dtypes
dfNW56Articles.sort_values(by='date')
daily_data.dtypes
dfNW56Articles.reset_index(inplace=True, drop=True) #reset index

#merge 
myArticles = pd.merge(dfNW56Articles, daily_data, on='date', sort=True)
myArticles.describe()  #95 articles au final.

##########################################################################
# Graphiques des anomalies et événements  
##########################################################################
#sur toute la période
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.lineplot(x='date', y='pageviews', data= daily_data, color='grey', alpha=0.2)
sns.scatterplot(x='date', y='pageviews', data= myOutliers, color='red', alpha=0.5)
sns.scatterplot(x='date', y='pageviews', data= myArticles, color='blue',  marker="+")
fig.suptitle( str(len(myOutliers)) + " événements (ronds rouges) pour " + str(len(myArticles)) + " articles (croix bleues) : ", fontsize=14, fontweight='bold')
ax.set(xlabel="Date", ylabel='Nbre pages vues / jour',
       title="Les articles des dernières années ne semblent pas suivis d'effets.")
fig.text(.9,-.05,"Evénements significatifs et publications des articles depuis 2011", 
         fontsize=9, ha="right")
#plt.show()
fig.savefig("Events-Articles-s2011.png", bbox_inches="tight", dpi=600)

#Plots par années
def plotEventsByYEar(myYear="2011") :
    sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
    fig, ax = plt.subplots()  #un seul plot 
    sns.lineplot(x='date', y='pageviews', data= daily_data[daily_data.Année==myYear], color='grey', alpha=0.2)
    sns.scatterplot(x='date', y='pageviews', data= myOutliers[myOutliers.Année==myYear], color='red', alpha=0.5)
    sns.scatterplot(x='date', y='pageviews', data= myArticles[myArticles.Année==myYear], color='blue',  marker="+")
    fig.suptitle( "Evénements (ronds rouges) et publications des articles (croix bleues) en " + myYear , fontsize=10, fontweight='bold')
    ax.set(xlabel="Date", ylabel='Nbre pages vues / jour')
    fig.text(.9,-.05,"Evénements significatifs et publications des articles en "  + myYear, 
         fontsize=9, ha="right")
    #plt.show()
    fig.savefig("Events-Articles-"+myYear+".png", bbox_inches="tight", dpi=600)

for myYear in ("2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018") :
    plotEventsByYEar(myYear=myYear)



##########################################################################
# Calcul du trafic hors "articles marketing" ie "trafic de base"
# On va supprimer toutes les pages vues correspondantes aux articles 
# "Marketing" ainsi que toutes les pages vues dont l'entrée s'est faite 
# par un article "Marketing". on compare ensuite au traffic global.
##########################################################################
dfPageViews.count()  #72822 ok
dfPageViews.dtypes
#on va créer une colonne "origin_index" qui va servir par la suite
dfPageViews['origin_index'] = np.arange(len(dfPageViews))
myArticles['pagePath']=myArticles['links'].str.replace('https://www.networking-morbihan.com', '')
pattern = '|'.join(myArticles['pagePath'])
#on enlève les pagePath
indexPagePathToKeep   = dfPageViews[(dfPageViews.pagePath.str.contains(pat=pattern,regex=True)==False)].index
dfBasePageViews = dfPageViews.iloc[indexPagePathToKeep]
dfBasePageViews.reset_index(inplace=True, drop=True)  #on reindexe 
dfBasePageViews.count() #43634  
#puis on enlève les landingPagePath
indexLandingPagePathToKeep   = dfBasePageViews[(dfBasePageViews.landingPagePath.str.contains(pat=pattern,regex=True)==False)].index
dfBasePageViews = dfBasePageViews.iloc[indexLandingPagePathToKeep]
dfBasePageViews.reset_index(inplace=True, drop=True)  #on reindexe 
dfBasePageViews.count() #37615 idem que dans R  

###############################################################################
# Sauvegardes en csv 
dfBasePageViews.to_csv("dfBasePageViews.csv", sep=";", index=False)  #séparateur ; 
myArticles.to_csv("myArticles.csv", sep=";", index=False)  #on sauvegarde pour plus tard
##################################################################


###########################################################################
# Calcul du trafic "articles marketing" par "anti join" du  "trafic de base"
#les pages avec nos articles sont les autres 
#############################################################################
dfAMPageViews = dfPageViews.drop(dfPageViews.merge(dfBasePageViews).origin_index)
dfAMPageViews.count() #35207 observations idem que dans R
len(dfAMPageViews.index)

###############################################################################
# Sauvegarde en csv 
dfAMPageViews.to_csv("dfAMPageViews.csv", sep=";", index=False)  #séparateur ; 
###############################################################################


############################################################################
# Significativité du trafic « articles marketing » dans les mois suivants 
# la publication.
# il s'agit des pages visitées suite à une entrée sur une page 
# "Marketing"  OU une page "Marketing"  elle même : AM
############################################################################

############################################################################
# Fonction pour récupérer les distributions sur un numéro de période et 
# un nombre de jour 
############################################################################




def getMyDistribution(myPageViews, myArticles, myNumPeriode,  myLastDate, myNbrOfDays=30, myTestType="AM"):
    '''
    En ENTREE :
    myPageViews = une dataframe de Pages vues à tester avec les variables au minimum :
        -date : date YYYY-MM-DD - date de la visite sur la page"
        -landingPagePath : chr path de la page d'entrée sur le site ex '/rentree-2011'"
        -PagePath : chr path de la page visitée sur le site site ex '/rentree-2011'"
    myArticles = une dataframe de Pages vues que l'on souhaite investiguer et qui sont  parmi les précédentes avec les variables au minimum  
        -date : date YYYY-MM-DD - date de la visite sur la page
        -PagePath : chr - path de la page visitée sur le site site ex '/rentree-2011'"
    myNumPeriode : integer Numéro de période par exemple 1 si c'est la première période
    myNbrOfDays : int - nombre de jours pour la période 30 par défaut
    myLastDate : date YYYY-MM-DD - date limite à investiguer.
    myTestType='AM' : chr -  'AM'  test du landingPagePath ou pagePath sinon test du pagePath seul. 
    EN SORTIE 
    ThisPeriodPV : np.array des pages vues pour chaque page pour la période interrogée.'''

    #ThisPeriodPV = np.empty([len(myArticles.index),1])  #np.array pour sauvegarder la distribution #
    #ThisPeriodPV = np.empty([len(myArticles.index)])
    #90
    #pd.DataFrame(columns= ['ThisPeriodPV'], index=range(len(myArticles.index)), dtype='float')
     
    dfThisPeriodPV  = pd.DataFrame(columns= ['ThisPeriodPV'], index=range(len(myArticles.index)), dtype='float')
    for i in range(0,len(myArticles.index)-1) :
        Link = myArticles.iloc[i]["pagePath"] #lien i /
        Date1 = myArticles.iloc[i]["date"]+ timedelta(days=(myNumPeriode-1)*myNbrOfDays)
        Date2 = Date1+timedelta(days=myNbrOfDays)
        if (myTestType == "AM") :
            myPV = myPageViews.loc[(myPageViews.pagePath == Link) | (myPageViews.landingPagePath == Link)]
        else :
            myPV = myPageViews.loc[(myPageViews.pagePath == Link)]

        #Marketing
        myPVPeriode = myPV.loc[(myPV['date'] >= Date1) & (myPV['date'] <= Date2)]
        myPVPeriodeLength = len(myPVPeriode)
    
        if Date1 > myLastDate :
            break #on arrête
            #myPVPeriodeLength = np.nan  #pour éviter d'avoir des 0 nous avions oublié cet aspect là précédemment
       
        # dfThisPeriodPV = dfThisPeriodPV.append({'ThisPeriodPV':myPVPeriodeLength}, ignore_index=True)
        dfThisPeriodPV.loc[i, 'ThisPeriodPV'] = myPVPeriodeLength
       
    return dfThisPeriodPV  #ThisPeriodPV, 

#/getMyDistribution
help(getMyDistribution) #test du help

lastDate = dfPageViews.iloc[len(dfPageViews.index)-1]['date']


############################################################################
# Pour le mois 1
############################################################################
myMonthNumber = 1
dfAMThisMonthPV  = getMyDistribution(myPageViews=dfAMPageViews, 
                                       myArticles=myArticles, 
                                       myNumPeriode=myMonthNumber, 
                                       myNbrOfDays=30,
                                       myLastDate=lastDate,
                                       myTestType="AM")

#test de normalité shapiro wilk
dfAMThisMonthPVDropNa = dfAMThisMonthPV.dropna() #
myW, myPValeur = stats.shapiro(dfAMThisMonthPVDropNa['ThisPeriodPV'].values)
myPValeur #0.0007478381157852709 normalité rejeté

sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.distplot(dfAMThisMonthPVDropNa['ThisPeriodPV'].values, bins=30, kde=False, rug=True)
ax.set(xlabel="Nombre de vues", ylabel='Décompte',
       title="la distribution est très étirée et ne présente pas de normalité.\n p Valeur =" + str(round(myPValeur,5)) +
       "<<0.05 \n le décompte le plus important se fait pour les pages à 0 vues \n mais il y a aussi des pages avec plus de 600 vues.")
fig.text(.9,-.05,"Distribution du nombre de pages vues Articles Marketing "  + str(myMonthNumber) + "mois après la parution", 
fontsize=9, ha="right")
#plt.show()
fig.savefig("Dist-PV-AM-Mois-"+str(myMonthNumber)+".png", bbox_inches="tight", dpi=600)


############################################################################
# Pour le mois 2
############################################################################
myMonthNumber = 2
dfAMThisMonthPV = getMyDistribution(myPageViews=dfAMPageViews, 
                                       myArticles=myArticles, 
                                       myNumPeriode=myMonthNumber, 
                                       myNbrOfDays=30,
                                       myLastDate=lastDate,
                                       myTestType="AM")

#test de normalité shapiro wilk
dfAMThisMonthPVDropNa = dfAMThisMonthPV.dropna() #
myW, myPValeur = stats.shapiro(dfAMThisMonthPVDropNa['ThisPeriodPV'].values)
myPValeur #normalité rejeté

sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.distplot(dfAMThisMonthPVDropNa['ThisPeriodPV'].values, bins=30, kde=False, rug=True)

ax.set(xlabel="Nombre de vues", ylabel='Décompte',
       title="Le deuxième mois la distribution s'est resserrée.\n p Valeur =" + str(round(myPValeur,12)) +
       "<<0.05 \n Il n'y a pas de pages au delà de 200 vues.")
fig.text(.9,-.05,"Distribution du nombre de pages vues Articles Marketing "  + str(myMonthNumber) + "mois après la parution", 
fontsize=9, ha="right")
#plt.show()
fig.savefig("Dist-PV-AM-Mois-"+str(myMonthNumber)+".png", bbox_inches="tight", dpi=600)

############################################################################
# Pour le mois 10
############################################################################
myMonthNumber = 10
dfAMThisMonthPV = getMyDistribution(myPageViews=dfAMPageViews, 
                                       myArticles=myArticles, 
                                       myNumPeriode=myMonthNumber, 
                                       myNbrOfDays=30,
                                       myLastDate=lastDate,
                                       myTestType="AM")

#test de normalité shapiro wilk
dfAMThisMonthPVDropNa = dfAMThisMonthPV.dropna() #
myW, myPValeur = stats.shapiro(dfAMThisMonthPVDropNa['ThisPeriodPV'].values)
myPValeur #normalité rejeté

sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.distplot(dfAMThisMonthPVDropNa['ThisPeriodPV'].values, bins=30, kde=False, rug=True)
ax.set(xlabel="Nombre de vues", ylabel='Décompte',
       title="Dès le dixième mois on s'approche d'un équilibre.\n p Valeur =" + str(round(myPValeur,16)) +
       "<<0.05 \n Les pages à 0 vues sont pratiquement aussi nombreuses que celles \n à plusieurs vues.")
fig.text(.9,-.05,"Distribution du nombre de pages vues Articles Marketing "  + str(myMonthNumber) + "mois après la parution", 
fontsize=9, ha="right")
#plt.show()
fig.savefig("Dist-PV-AM-Mois-"+str(myMonthNumber)+".png", bbox_inches="tight", dpi=600)


############################################################################
# Pour le mois 40
############################################################################
myMonthNumber = 40
dfAMThisMonthPV = getMyDistribution(myPageViews=dfAMPageViews, 
                                       myArticles=myArticles, 
                                       myNumPeriode=myMonthNumber, 
                                       myNbrOfDays=30,
                                       myLastDate=lastDate,
                                       myTestType="AM")

#test de normalité shapiro wilk
dfAMThisMonthPVDropNa = dfAMThisMonthPV.dropna() #
myW, myPValeur = stats.shapiro(dfAMThisMonthPVDropNa['ThisPeriodPV'].values)
myPValeur #normalité rejeté

sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.distplot(dfAMThisMonthPVDropNa['ThisPeriodPV'].values, bins=30, kde=False, rug=True)
ax.set(xlabel="Nombre de vues", ylabel='Décompte',
       title="A 40 mois la distribution est très resserrée. \n p Valeur =" + str(round(myPValeur,17)) +
       "<<0.05 \n Les pages à 0 vues sont majoritaires.")
fig.text(.9,-.05,"Distribution du nombre de pages vues Articles Marketing "  + str(myMonthNumber) + "mois après la parution", 
fontsize=9, ha="right")
#plt.show()
fig.savefig("Dist-PV-AM-Mois-"+str(myMonthNumber)+".png", bbox_inches="tight", dpi=600)

#############################################################################################
# Utilisation du SIGN.test pour tester la significativité des distributions.
#############################################################################################
#initialisation :
#Pour enregistrer les données du test pour toutes les distributions

dfAMPValue = pd.DataFrame(columns= ['pvalue', 'statistic',
                                     'myNotNas', 'myNotNull','myMedian']) 
    
    
 
myAMMd = 0.01 #médiane de l'hypothèse nulle : 0 ne marche pas avec R
#-> à mon avis le test est que la médiane soit inférieure 
#à cette valeur donc < 0 ne donne rien alors que < 0.01
#détecte les 0.
#Rem cela fonctionne pareil avec SAS on fait un test avec 
#mu0=0.01
#il semble que cela soit pareil avec python
                
myAMCl = 0.95  #niveau de confiance souhaité. non utilisé ici 
myLastMonth = 90 #dernier mois à investiguer 7,5 années
lastDate = dfPageViews.iloc[len(dfPageViews.index)-1]['date']
#x=1
for x in range(1,myLastMonth):
    dfAMThisMonthPV = getMyDistribution(myPageViews=dfAMPageViews, 
                                       myArticles=myArticles, 
                                       myNumPeriode=x, 
                                       myNbrOfDays=30,
                                       myLastDate=lastDate,
                                       myTestType="AM")
    
    dfAMThisMonthPVDropNa = dfAMThisMonthPV.dropna()
    #on compare par rapport à une distribution presque à zéro : 0.01
    zeroData = pd.DataFrame(myAMMd, index=np.arange(len(dfAMThisMonthPVDropNa)), columns=['ThisPeriodPV'])
    ##### Différents essai de stats
    #statistic, pvalue = sp.stats.wilcoxon(x=dfAMThisMonthPVDropNa['ThisPeriodPV'].values, y=None, zero_method='wilcox', correction=False)
    #statistic, pvalue = sp.stats.ranksums(x=dfAMThisMonthPVDropNa['ThisPeriodPV'].values, y=zeroData['ThisPeriodPV'].values)
    #mannwhitneyu permet d'avoir une alternative "Greater"
    statistic, pvalue = sp.stats.mannwhitneyu(x=dfAMThisMonthPVDropNa['ThisPeriodPV'].values, y=zeroData['ThisPeriodPV'].values, alternative='greater')
    #statistic est *100 ne sais pas pourquoi
    statistic = statistic/100

    myNotNas = len(dfAMThisMonthPVDropNa)  #nombre d'observations non NaN
    myNotNull = (dfAMThisMonthPVDropNa['ThisPeriodPV']>0).sum() #nombre d'observations non nulle
    dfAMPValue = dfAMPValue.append({'pvalue': pvalue, 'statistic':statistic, 'myNotNas':myNotNas
                                    , 'myNotNull':myNotNull}, ignore_index=True)



dfAMPValue.index  #pour l'axe des x.
myfirstMonthPValueUpper = dfAMPValue.index.get_loc(dfAMPValue.index[dfAMPValue['pvalue'] > 0.05][0]) + 1


#graphique 
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot
sns.lineplot(x=dfAMPValue.index.values+1, y=dfAMPValue.pvalue)
plt.vlines(x = myfirstMonthPValueUpper, ymin = 0, ymax = 1, color = 'green', linewidth=0.5)
plt.hlines(y = 0.05, xmin = 0, xmax = 90, color = 'red', linewidth=0.5)
fig.suptitle("L'hypothèse nulle est vérifiée dès le mois "+ str(myfirstMonthPValueUpper) + " (ligne verte)", fontsize=14, fontweight='bold')
ax.set(xlabel='Nombre de mois', ylabel='P-Valeur',
       title='La ligne rouge indique la p Valeur à 0.05.')
fig.text(.3,-.03,"P.valeur SIGN.test Mann Withney pour les Articles Marketing", 
         fontsize=9)
#plt.show()
fig.savefig("AM-SIGN-Test-P-Value.png", bbox_inches="tight", dpi=600)


#comparons la statistique càd ici les pages avec vues > 0
#vs la taille de l'échantillon donnés par myNotNas, et la moitié de ce dernier
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot
sns.lineplot(x=dfAMPValue.index.values+1, y=dfAMPValue.statistic, color="blue")
sns.lineplot(x=dfAMPValue.index.values+1, y=dfAMPValue.myNotNas, color="red")
sns.lineplot(x=dfAMPValue.index.values+1, y=dfAMPValue.myNotNas/2, color="black")
fig.suptitle("Le nombre de pages avec vues > 0 baisse plus vite que la taille de l'échantillon.\n La courbe bleu s'approche rapidement de la ligne noire \n qui représente la moitié de l'échantillon.", fontsize=10, fontweight='bold')
ax.set(xlabel="Nombre de mois", ylabel="Pages Vues > 0 (bleu) / Taille échantillon (rouge)",
       title="")
fig.text(.2,-.03,"Evolution mensuelle du Nbr de pages vues > 0 vs Taille échantillon", fontsize=9)
#plt.show()
fig.savefig("AM-sup0-SampleSize.png", bbox_inches="tight", dpi=600)




##################################################################################
# vérifions en calculant l'intervalle de confiance à 95% sur une loi binomiale 
# avec les données observées.
dfAMPValue['prop'] = dfAMPValue.apply(lambda row: row.myNotNull / row.myNotNas, axis=1)  #proportion 
#Intervalle de confiance binomial à 95%
dfAMPValue['confIntBinomial'] = dfAMPValue.apply(lambda row: 1.96 * math.sqrt((row.prop*(1-row.prop))/row.myNotNas) , axis=1) 
#borne inférieure 
dfAMPValue['propCIBinf'] = dfAMPValue.apply(lambda row: row.prop - row.confIntBinomial, axis=1) 
#borne superieure 
dfAMPValue['propCIBsup'] = dfAMPValue.apply(lambda row: row.prop + row.confIntBinomial, axis=1)
#Première valeur dela borne inférieure  sous 0.5
firstPropCIBinfUnder = dfAMPValue.index.get_loc(dfAMPValue.index[dfAMPValue['propCIBinf'] <= 0.5][0]) + 1

###################################################################################
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot
sns.lineplot(x=dfAMPValue.index.values+1, y=dfAMPValue.prop, color="black")
sns.lineplot(x=dfAMPValue.index.values+1, y=dfAMPValue.propCIBsup, color="blue")
sns.lineplot(x=dfAMPValue.index.values+1, y=dfAMPValue.propCIBinf, color="blue")
plt.vlines(x = firstPropCIBinfUnder, ymin = 0, ymax = 1, color = 'green', linewidth=0.5)
plt.hlines(y = 0.5, xmin = 0, xmax = 90, color = 'red', linewidth=0.5)

fig.suptitle("L'hypothèse nulle est vérifiée dès le mois " + str(firstPropCIBinfUnder) , fontsize=14, fontweight='bold')
ax.set(xlabel="Nombre de mois", ylabel="proportion avec intervalle de confiance (bleu) ",
       title="La valeur inférieure de l'IC passe sous la barre des 0.5")
fig.text(.2,-.03,"Proportion de pages vues > 0 pour chaque distribution mensuelle ", fontsize=9)
#plt.show()
fig.savefig("AM-PropPVsup1.png", bbox_inches="tight", dpi=600)

###################################################################################
#en Lissage Loess 
#Calcul Valeurs lissées
###################################################################
# Méthode Loess récupérée sur le Net :
# http://www.jtrive.com/loess-nonparametric-scatterplot-smoothing-in-python.html
####################################################################################
"""
Local Regression (LOESS) estimation routine.
"""
import numpy as np
import pandas as pd
import scipy


def loc_eval(x, b):
    """
    Evaluate `x` using locally-weighted regression parameters.
    Degree of polynomial used in loess is inferred from b. `x`
    is assumed to be a scalar.
    """
    loc_est = 0
    for i in enumerate(b): loc_est+=i[1]*(x**i[0])
    return(loc_est)



def loess(xvals, yvals, alpha, poly_degree=1):
    """
    Perform locally-weighted regression on xvals & yvals.
    Variables used inside `loess` function:

        n         => number of data points in xvals
        m         => nbr of LOESS evaluation points
        q         => number of data points used for each
                     locally-weighted regression
        v         => x-value locations for evaluating LOESS
        locsDF    => contains local regression details for each
                     location v
        evalDF    => contains actual LOESS output for each v
        X         => n-by-(poly_degree+1) design matrix
        W         => n-by-n diagonal weight matrix for each
                     local regression
        y         => yvals
        b         => local regression coefficient estimates.
                     b = `(X^T*W*X)^-1*X^T*W*y`. Note that `@`
                     replaces `np.dot` in recent numpy versions.
        local_est => response for local regression
    """
    # Sort dataset by xvals.
    all_data = sorted(zip(xvals, yvals), key=lambda x: x[0])
    xvals, yvals = zip(*all_data)

    locsDF = pd.DataFrame(
                columns=[
                  'loc','x','weights','v','y','raw_dists',
                  'scale_factor','scaled_dists'
                  ])
    evalDF = pd.DataFrame(
                columns=[
                  'loc','est','b','v','g'
                  ])

    n = len(xvals)
    m = n + 1
    q = int(np.floor(n * alpha) if alpha <= 1.0 else n)
    avg_interval = ((max(xvals)-min(xvals))/len(xvals))
    v_lb = max(0,min(xvals)-(.5*avg_interval))
    v_ub = (max(xvals)+(.5*avg_interval))
    v = enumerate(np.linspace(start=v_lb, stop=v_ub, num=m), start=1)
    #print('liste v=', list(v))
    # Generate design matrix based on poly_degree.
    xcols = [np.ones_like(xvals)]
    for j in range(1, (poly_degree + 1)):
        xcols.append([i ** j for i in xvals])
    X = np.vstack(xcols).T


    for i in v:

        print('i=', i) #pour voir à quelle vitesse cela défile.
        iterpos = i[0]
        iterval = i[1]

        # Determine q-nearest xvals to iterval.
        iterdists = sorted([(j, np.abs(j-iterval)) \
                           for j in xvals], key=lambda x: x[1])

        _, raw_dists = zip(*iterdists)

        # Scale local observations by qth-nearest raw_dist.
        scale_fact = raw_dists[q-1]
        scaled_dists = [(j[0],(j[1]/scale_fact)) for j in iterdists]
        weights = [(j[0],((1-np.abs(j[1]**3))**3 \
                      if j[1]<=1 else 0)) for j in scaled_dists]

        # Remove xvals from each tuple:
        _, weights      = zip(*sorted(weights,     key=lambda x: x[0]))
        _, raw_dists    = zip(*sorted(iterdists,   key=lambda x: x[0]))
        _, scaled_dists = zip(*sorted(scaled_dists,key=lambda x: x[0]))

        iterDF1 = pd.DataFrame({
                    'loc'         :iterpos,
                    'x'           :xvals,
                    'v'           :iterval,
                    'weights'     :weights,
                    'y'           :yvals,
                    'raw_dists'   :raw_dists,
                    'scale_fact'  :scale_fact,
                    'scaled_dists':scaled_dists
                    })

        locsDF    = pd.concat([locsDF, iterDF1])
        W         = np.diag(weights)
        y         = yvals
        b         = np.linalg.inv(X.T @ W @ X) @ (X.T @ W @ y)
        local_est = loc_eval(iterval, b)
        iterDF2   = pd.DataFrame({
                       'loc':[iterpos],
                       'b'  :[b],
                       'v'  :[iterval],
                       'g'  :[local_est]
                       })

        evalDF = pd.concat([evalDF, iterDF2])

    # Reset indicies for returned DataFrames.
    locsDF.reset_index(inplace=True)
    locsDF.drop('index', axis=1, inplace=True)
    locsDF['est'] = 0; evalDF['est'] = 0
    locsDF = locsDF[['loc','est','v','x','y','raw_dists',
                     'scale_fact','scaled_dists','weights']]

    # Reset index for evalDF.
    evalDF.reset_index(inplace=True)
    evalDF.drop('index', axis=1, inplace=True)
    evalDF = evalDF[['loc','est', 'v', 'b', 'g']]

    return(locsDF, evalDF)
######################################################################"

#Calculs

regsDF, myAMLoess = loess(dfAMPValue.index.values,dfAMPValue.prop.values, alpha=.34, poly_degree=1)
myAMLoess.g #<- valeurs lissées.
# valeurs lissées inférieures :
myAMLoess['conf.int.inf'] = myAMLoess.apply(lambda row: row.g - 1.96*stats.sem(myAMLoess.g) , axis=1)
#Première valeur de la borne inférieure de l'IC lissée sous la barre des 0.5 i.e mediane = 0
firstAMLoessCIFUnder =  myAMLoess.index.get_loc(myAMLoess.index[myAMLoess['conf.int.inf'] <= 0.5][0]) + 1
# valeurs lissées supérieures :
myAMLoess['conf.int.sup'] = myAMLoess.apply(lambda row: row.g + 1.96*stats.sem(myAMLoess.g) , axis=1)


###################################################################################
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot
sns.lineplot(x=dfAMPValue.index.values+1, y=dfAMPValue.prop, color="black")
sns.lineplot(x=myAMLoess.index.values+1, y=myAMLoess["conf.int.sup"], color="grey", alpha=0.5)
sns.lineplot(x=myAMLoess.index.values+1, y=myAMLoess.g, color="blue")
sns.lineplot(x=myAMLoess.index.values+1, y=myAMLoess["conf.int.inf"], color="grey", alpha=0.5)

plt.vlines(x = firstAMLoessCIFUnder, ymin = 0, ymax = 1, color = 'green', linewidth=0.5)
plt.hlines(y = 0.5, xmin = 0, xmax = 90, color = 'red', linewidth=0.5)

fig.suptitle("L'hypothèse nulle est vérifiée au mois " + str(firstAMLoessCIFUnder) , fontsize=14, fontweight='bold')
ax.set(xlabel="Nombre de mois", ylabel="proportion lissée (bleu)",
       title="La valeur inférieure de l'IC passe sous la barre des 0.5 (rouge)")
fig.text(.2,-.03,"Proportion lissée de pages vues > 0 pour chaque distribution mensuelle", fontsize=9)
#plt.show()
fig.savefig("AM-PropPVsup1-Loess.png", bbox_inches="tight", dpi=600)


##########################################################################
# Restreignons l'investigation aux pages "Marketing" visitées uniquement 
# suite à une entrée sur une page "Marketing" (la même ou une autre)
##########################################################################

#Verifs ############
dfPageViews.info()
myArticles.info()
pattern = '|'.join(myArticles['pagePath'])
#on enlève les pagePath
indexLandingPagePathToKeep = dfPageViews[(dfPageViews.landingPagePath.str.contains(pat=pattern,regex=True)==True)].index
dfDMPageViews  = dfPageViews.iloc[indexLandingPagePathToKeep]
dfDMPageViews.reset_index(inplace=True, drop=True)  #on reindexe 
dfDMPageViews.count() #28553 obs.

###############################################################################
# Sauvegarde en csv 
dfDMPageViews.to_csv("dfDMPageViews.csv", sep=";", index=False)  #séparateur ; 
###############################################################################


#Preparation des données pour graphique de pvalue
dfDMPValue = pd.DataFrame(columns= ['pvalue', 'statistic',
                                     'myNotNas', 'myNotNull','myMedian']) 
    
    
 
myDMMd = 0.01 #médiane de l'hypothèse nulle : 0 ne marche pas avec R
myLastMonth = 90 #dernier mois à investiguer 7,5 années
lastDate = dfDMPageViews.iloc[len(dfDMPageViews.index)-1]['date']
#x=1
for x in range(1,myLastMonth):
    dfDMThisMonthPV = getMyDistribution(myPageViews=dfDMPageViews, 
                                       myArticles=myArticles, 
                                       myNumPeriode=x, 
                                       myNbrOfDays=30,
                                       myLastDate=lastDate,
                                       myTestType="AM")
    
    dfDMThisMonthPVDropNa = dfDMThisMonthPV.dropna()
    #on compare par rapport à une distribution presque à zéro : 0.01
    zeroData = pd.DataFrame(myDMMd, index=np.arange(len(dfDMThisMonthPVDropNa)), columns=['ThisPeriodPV'])
    #mannwhitneyu permet d'avoir une alternative "Greater"
    statistic, pvalue = sp.stats.mannwhitneyu(x=dfDMThisMonthPVDropNa['ThisPeriodPV'].values, y=zeroData['ThisPeriodPV'].values, alternative='greater')
    #statistic est *100 ne sais pas pourquoi
    statistic = statistic/100

    myNotNas = len(dfDMThisMonthPVDropNa)  #nombre d'observations non NaN
    myNotNull = (dfDMThisMonthPVDropNa['ThisPeriodPV']>0).sum() #nombre d'observations non nulle
    dfDMPValue = dfDMPValue.append({'pvalue': pvalue, 'statistic':statistic, 'myNotNas':myNotNas
                                    , 'myNotNull':myNotNull}, ignore_index=True)



dfDMPValue.index  #pour l'axe des x.
myfirstMonthPValueUpper = dfDMPValue.index.get_loc(dfDMPValue.index[dfDMPValue['pvalue'] > 0.05][0]) + 1

#graphique 
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot
sns.lineplot(x=dfDMPValue.index.values+1, y=dfDMPValue.pvalue)
plt.vlines(x = myfirstMonthPValueUpper, ymin = 0, ymax = 1, color = 'green', linewidth=0.5)
plt.hlines(y = 0.05, xmin = 0, xmax = 90, color = 'red', linewidth=0.5)
fig.suptitle("L'hypothèse nulle est vérifiée dès le mois "+ str(myfirstMonthPValueUpper) + " (ligne verte)", fontsize=14, fontweight='bold')
ax.set(xlabel='Nombre de mois', ylabel='P-Valeur',
       title='La ligne rouge indique la p Valeur à 0.05.')
fig.text(.2,-.03,"P.valeur SIGN.test Mann Withney pour les Articles Direct Marketing", 
         fontsize=9)
#plt.show()
fig.savefig("DM-SIGN-Test-P-Value.png", bbox_inches="tight", dpi=600)

#########################################################
##  Comparatifs AM MD lissés
#on aura besoin de la proportion ensuite
dfDMPValue['prop'] = dfDMPValue.apply(lambda row: row.myNotNull / row.myNotNas, axis=1)  #proportion
#Calcul Valeurs lissées pour Direct Marketing
regsDF, myDMLoess = loess(dfDMPValue.index.values,dfDMPValue.prop.values, alpha=.34, poly_degree=1)
myDMLoess.g #<- valeurs lissées.
# valeurs lissées inférieures :
myDMLoess['conf.int.inf'] = myDMLoess.apply(lambda row: row.g - 1.96*stats.sem(myDMLoess.g) , axis=1)
#Première valeur de la borne inférieure de l'IC lissée sous la barre des 0.5 i.e mediane = 0
firstDMLoessCIFUnder =  myDMLoess.index.get_loc(myDMLoess.index[myDMLoess['conf.int.inf'] <= 0.5][0]) + 1
# valeurs lissées supérieures :
myDMLoess['conf.int.sup'] = myDMLoess.apply(lambda row: row.g + 1.96*stats.sem(myDMLoess.g) , axis=1)


###################################################################################
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot

sns.lineplot(x=dfAMPValue.index.values+1, y=dfAMPValue.prop, color="blue")
sns.lineplot(x=myAMLoess.index.values+1, y=myAMLoess["conf.int.sup"], color="grey", alpha=0.5)
sns.lineplot(x=myAMLoess.index.values+1, y=myAMLoess.g, color="blue")
sns.lineplot(x=myAMLoess.index.values+1, y=myAMLoess["conf.int.inf"], color="grey", alpha=0.5)

sns.lineplot(x=dfDMPValue.index.values+1, y=dfDMPValue.prop, color="red")
sns.lineplot(x=myDMLoess.index.values+1, y=myDMLoess["conf.int.sup"], color="grey", alpha=0.5)
sns.lineplot(x=myDMLoess.index.values+1, y=myDMLoess.g, color="red")
sns.lineplot(x=myDMLoess.index.values+1, y=myDMLoess["conf.int.inf"], color="grey", alpha=0.5)

plt.vlines(x = firstDMLoessCIFUnder, ymin = 0, ymax = 1, color = 'green', linewidth=0.5)
plt.hlines(y = 0.5, xmin = 0, xmax = 90, color = 'red', linewidth=0.5)

fig.suptitle("L'hypothèse nulle pour Direct Marketing est vérifiée au mois " + str(firstDMLoessCIFUnder) , fontsize=14, fontweight='bold')
ax.set(xlabel="Nombre de mois", ylabel="proportion lissée - AM: bleu, DM : rouge ",
       title="La valeur inférieure DM de l'IC passe sous la barre des 0.5 (rouge)")
fig.text(.2,-.05,"Proportion lissée Articles Marketing et Direct Marketing de pages vues > 0 \n pour chaque distribution mensuelle", fontsize=9)
#plt.show()
fig.savefig("DM-AM-PropPVsup1-Loess.png", bbox_inches="tight", dpi=600)

#################################################################
# Restreignons encore l'investigation aux pages visités 
# uniquement suite à une entrée sur la même page  "Marketing"  
# UM : Unique Marketing
#################################################################
#on garde uniquement les landingPagePath = pagePath
dfUMPageViews  = dfDMPageViews[(dfDMPageViews.landingPagePath == dfDMPageViews.pagePath)]
dfUMPageViews.reset_index(inplace=True, drop=True)  #on reindexe 
dfUMPageViews.count() #21214 obs.

#Preparation des données pour graphique de pvalue
dfUMPValue = pd.DataFrame(columns= ['pvalue', 'statistic',
                                     'myNotNas', 'myNotNull']) 
    
    
 
myUMMd = 0.01 #médiane de l'hypothèse nulle : 0 ne marche pas avec R
myLastMonth = 90 #dernier mois à investiguer 7,5 années
lastDate = dfUMPageViews.iloc[len(dfUMPageViews.index)-1]['date']
#x=1
for x in range(1,myLastMonth):
    dfUMThisMonthPV = getMyDistribution(myPageViews=dfUMPageViews, 
                                       myArticles=myArticles, 
                                       myNumPeriode=x, 
                                       myNbrOfDays=30,
                                       myLastDate=lastDate,
                                       myTestType="AM")
    
    dfUMThisMonthPVDropNa = dfUMThisMonthPV.dropna()
    #on compare par rapport à une distribution presque à zéro : 0.01
    zeroData = pd.DataFrame(myUMMd, index=np.arange(len(dfUMThisMonthPVDropNa)), columns=['ThisPeriodPV'])
    #mannwhitneyu permet d'avoir une alternative "Greater"
    statistic, pvalue = sp.stats.mannwhitneyu(x=dfUMThisMonthPVDropNa['ThisPeriodPV'].values, y=zeroData['ThisPeriodPV'].values, alternative='greater')
    #statistic est *100 ne sais pas pourquoi
    statistic = statistic/100

    myNotNas = len(dfUMThisMonthPVDropNa)  #nombre d'observations non NaN
    myNotNull = (dfUMThisMonthPVDropNa['ThisPeriodPV']>0).sum() #nombre d'observations non nulle
    dfUMPValue = dfUMPValue.append({'pvalue': pvalue, 'statistic':statistic, 'myNotNas':myNotNas
                                    , 'myNotNull':myNotNull}, ignore_index=True)



dfUMPValue.index  #pour l'axe des x.
myfirstMonthPValueUpper = dfUMPValue.index.get_loc(dfUMPValue.index[dfUMPValue['pvalue'] > 0.05][0]) + 1

#graphique 
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot
sns.lineplot(x=dfUMPValue.index.values+1, y=dfUMPValue.pvalue)
plt.vlines(x = myfirstMonthPValueUpper, ymin = 0, ymax = 1, color = 'green', linewidth=0.5)
plt.hlines(y = 0.05, xmin = 0, xmax = 90, color = 'red', linewidth=0.5)
fig.suptitle("L'hypothèse nulle est vérifiée dès le mois "+ str(myfirstMonthPValueUpper) + " (ligne verte)", fontsize=14, fontweight='bold')
ax.set(xlabel='Nombre de mois', ylabel='P-Valeur',
       title='La ligne rouge indique la p Valeur à 0.05.')
fig.text(.2,-.03,"P.valeur SIGN.test Mann Withney pour les Articles Unique Marketing", 
         fontsize=9)
#plt.show()
fig.savefig("UM-SIGN-Test-P-Value.png", bbox_inches="tight", dpi=600)

#################################################################
##  Comparatifs AM DM UM 
#################################################################
#Calcul Valeurs lissées pour Unique Marketing

#on aura besoin de la proportion ensuite
dfUMPValue['prop'] = dfUMPValue.apply(lambda row: row.myNotNull / row.myNotNas, axis=1)  #proportion
#Calcul Valeurs lissées pour Direct Marketing
regsDF, myUMLoess = loess(dfUMPValue.index.values,dfUMPValue.prop.values, alpha=.34, poly_degree=1)
myUMLoess.g #<- valeurs lissées.
# valeurs lissées inférieures :
myUMLoess['conf.int.inf'] = myUMLoess.apply(lambda row: row.g - 1.96*stats.sem(myUMLoess.g) , axis=1)
#Première valeur de la borne inférieure de l'IC lissée sous la barre des 0.5 i.e mediane = 0
firstUMLoessCIFUnder =  myUMLoess.index.get_loc(myUMLoess.index[myUMLoess['conf.int.inf'] <= 0.5][0]) + 1
# valeurs lissées supérieures :
myUMLoess['conf.int.sup'] = myUMLoess.apply(lambda row: row.g + 1.96*stats.sem(myUMLoess.g) , axis=1)


###################################################################################
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot

sns.lineplot(x=dfAMPValue.index.values+1, y=dfAMPValue.prop, color="blue")
sns.lineplot(x=myAMLoess.index.values+1, y=myAMLoess["conf.int.sup"], color="grey", alpha=0.5)
sns.lineplot(x=myAMLoess.index.values+1, y=myAMLoess.g, color="blue")
sns.lineplot(x=myAMLoess.index.values+1, y=myAMLoess["conf.int.inf"], color="grey", alpha=0.5)

sns.lineplot(x=dfDMPValue.index.values+1, y=dfDMPValue.prop, color="red")
sns.lineplot(x=myDMLoess.index.values+1, y=myDMLoess["conf.int.sup"], color="grey", alpha=0.5)
sns.lineplot(x=myDMLoess.index.values+1, y=myDMLoess.g, color="red")
sns.lineplot(x=myDMLoess.index.values+1, y=myDMLoess["conf.int.inf"], color="grey", alpha=0.5)

sns.lineplot(x=dfUMPValue.index.values+1, y=dfUMPValue.prop, color="black")
sns.lineplot(x=myUMLoess.index.values+1, y=myUMLoess["conf.int.sup"], color="grey", alpha=0.5)
sns.lineplot(x=myUMLoess.index.values+1, y=myUMLoess.g, color="black")
sns.lineplot(x=myUMLoess.index.values+1, y=myUMLoess["conf.int.inf"], color="grey", alpha=0.5)

plt.vlines(x = firstUMLoessCIFUnder, ymin = 0, ymax = 1, color = 'green', linewidth=0.5)
plt.hlines(y = 0.5, xmin = 0, xmax = 90, color = 'red', linewidth=0.5)

fig.suptitle("L'hypothèse nulle pour Unique Marketing est vérifiée au mois " + str(firstUMLoessCIFUnder) , fontsize=14, fontweight='bold')
ax.set(xlabel="Nombre de mois", ylabel="prop. lissée : AM bleu, DM rouge, UM noir ",
       title="La valeur inférieure UM de l'IC passe sous la barre des 0.5 (rouge)")
fig.text(.2,-.05,"Proportion lissée Articles Marketing, Direct Marketing et unique Marketing \n de pages vues > 0 pour chaque distribution mensuelle", fontsize=9)
#plt.show()
fig.savefig("UM-DM-AM-PropPVsup1-Loess.png", bbox_inches="tight", dpi=600)


############################################################
# Typologie du trafic entrant 
############################################################
#Revenons au Dataframe des pages vues dfPageViews
#Relecture ############
myDateToParse = ['date']  #pour parser la variable date en datetime sinon object
dfPageViews = pd.read_csv("dfPageViews.csv", sep=";", dtype={'Année':object}, parse_dates=myDateToParse)
#verifs
dfPageViews.info()  #72822 enregistrements 
#regardons ce que l'on a dans la variable medium.
dfPageViews['medium'].value_counts()
#La variable medium ne nous donne pas une information fiable.
#Remarque "(none)" devrait indiquer du trafic direct i.e 
#la personne a indiqué l'url dans la barre de menu de son 
# navigateur (ce qui arrive pratiquement jamais aujourd'hui). 
# Dans les faits il s'agit de sources non repérées par Google 
#et le plus souvent des clients emails ou des robots (encore !!)

#il serait intéressant de dissocier les canaux :
# - le trafic suite à un email  :  email en fait nous ne pouvons 
#   repérer que le Webmail dans source
# - le trafic via un site quelqonque : referral
# - le trafic via les réseaux sociaux : social
# - le trafic via des moteurs de recherche. : search
# - le trafic direct : direct (un peu fourre tout et contient de 
#   l'email aussi ... :-( )

#regardons les différentes sources
mySources =  dfPageViews['source'].value_counts().to_frame()
mySources.info()
mySources.rename(columns = {'source':'freq'}, inplace = True)
mySources['source']=mySources.index

mySources = pd.DataFrame(data=dfPageViews['source'].value_counts(), columns=['freq'])
# Sauvegarde en csv 
mySources.to_csv("mySources.csv", sep=";", index=False)  #séparateur ; 
#.... traitement manuel externe .... 
mySourcesChannel = pd.read_csv("mySourcesChannel.csv", sep=";")
mySourcesChannel.info()
dfPageViews.info()
#On vire les blancs pour faire  le merge on
dfPageViews['source'] = dfPageViews['source'].str.strip()
mySourcesChannel['source'] = mySourcesChannel['source'].str.strip()

dfPVChannel = pd.merge(dfPageViews, mySourcesChannel, on='source', how='left')
dfPVChannel.info()
#voyons ce que l'on a comme valeurs.
dfPVChannel['channel'].value_counts()
sorted(dfPVChannel['channel'].unique())


#creation de la dataframe dateChannel_data  par jour et canal
dfDatePVChannel = dfPVChannel[['date', 'channel', 'pageviews']].copy() #nouveau dataframe avec que la date et les canaux
dfDatePVChannel.info()
dateChannel_data = dfDatePVChannel.groupby(['date', 'channel']).count() #
#dans l'opération précédente la date et le channel sont partis dans l'index
dateChannel_data = dateChannel_data.reset_index() #recrée les colonnes date et channel
dateChannel_data['Année'] = dateChannel_data['date'].astype(str).str[:4] #ajoute l'année
dateChannel_data.info()
dateChannel_data.sort_values(by=['date', 'channel'])
dateChannel_data.head(20)
##########################################################################
# Graphique en barre général Répartition du trafic selon les canaux.
##########################################################################
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot
sns.barplot(x='channel', y='pageviews', data=dateChannel_data, estimator=sum, order=sorted(dfPVChannel['channel'].unique()))                
fig.suptitle("Le canal 'search' est le premier contributeur en termes de trafic.", fontsize=14, fontweight='bold')
ax.set(xlabel="Canal", ylabel="Pages vues",
       title="Le canal 'direct' (fourre tout) est malheureusement important aussi.")
fig.text(.35,-.03,"Trafic Global - Pages vues selon les canaux depuis 2011", fontsize=9)
#plt.show()
fig.savefig("PV-Channel-bar.png", bbox_inches="tight", dpi=600)

##########################################################################
#Graphique en barre par année
#Répartition du trafic selon les canaux.
##########################################################################
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
g=sns.FacetGrid(dateChannel_data, col="Année", col_wrap=3) 
g.map(sns.barplot, 'channel', 'pageviews', palette="deep",  estimator=sum, order=sorted(dfPVChannel['channel'].unique()))
plt.subplots_adjust(top=0.9)
g.fig.suptitle("Le canal 'social' avait une forte contribution relative en 2011. \n La répartition des autres canaux est restée relativement stable.", fontsize=14, fontweight='bold')
g.set(xlabel="Canal", ylabel="Pages vues")
g.set_xticklabels(fontsize=9)
g.fig.text(.35,-.00,"Trafic Global - Pages vues selon les années et les canaux depuis 2011", fontsize=9)
#plt.show()
g.savefig("PV-Channel-bar-an.jpeg.png", bbox_inches="tight", dpi=600)

####################################################################
#evolution des pages vues selon les canaux (lissée)
####################################################################
#Essai en calculant les loess pour un channel
theDays = dfDatePVChannel.groupby(['date']).count()
theDays = theDays.reset_index()
theDays.drop(['channel',  'pageviews'], axis = 1, inplace = True)
dateChannel_dataDirect = dateChannel_data[dateChannel_data.channel == 'direct']
#on met toutes les dates possibles
dfDCDDirect = pd.merge(dateChannel_dataDirect, theDays, on='date', how='right')
#si nouvelles date pageviews à 0
dfDCDDirect['pageviews'].fillna(0, inplace=True)
dfDCDDirect = dfDCDDirect.sort_values(by='date') #pour être bien sûr d'être dans le bon ordre
dfDCDDirect.reset_index(inplace=True) #reindexation dans le bon ordre des dates.


#Moyennement Rapide mais très moche.
#on utilise la méthode loess de Michele Cappellari
#https://pypi.org/project/loess/  #très moche
from loess.loess_1d import loess_1d
xout, yout, weigts = loess_1d(dfDCDDirect.index.values, dfDCDDirect.pageviews.values, frac=0.75)
yout.size
dfDCDDirect['loess']=pd.DataFrame(yout)[0]
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot
sns.lineplot(x=dfDCDDirect.index.values, y=dfDCDDirect.loess, color="blue")

 
#autre Méthode Loess plus élégante mais très lente à calculer
regsDF, dfDCDDirectLoess = loess(dfDCDDirect.index.values,dfDCDDirect.pageviews.values, alpha=.75, poly_degree=1)
dfDCDDirecttLoess.g #<- valeurs lissées.
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot
sns.lineplot(x=dfDCDDirecttLoess.index.values, y=dfDCDDirecttLoess.g, color="blue")
###les 2 méthodes précédentes ne sont pas utilisées. on préfèrera Plotnine


###################################################################################
###### Essayons Plotline : implémentation de ggplot dans Python ########
#https://plotnine.readthedocs.io/en/stable/generated/plotnine.stats.stat_smooth.html#plotnine.stats.stat_smooth
# conda install -c conda-forge plotnine  #pour ggplot
#pip install scikit-misc  #pour loess #conda non disponible
from skmisc import loess  #pour methode Loess compatible avec stat_smooth
from plotnine import *  #pour ggplot
from mizani.breaks import date_breaks  #pour mettre une date tous les 2 ans./

p = (ggplot(dateChannel_data) +
 stat_smooth(aes('date', 'pageviews', color='channel'), method='loess', span=0.4) +
 ylab("Pages vues") +
 scale_x_datetime(breaks=date_breaks('2 years')) +       # new
 ggtitle("Le canal 'search' a augmenté jusqu'en 2015 puis a baissé fortement. \nLes autres canaux ont régulièrement baissé") +
 xlab("Date\nTrafic Global - Evolution lissée des pages vues selon les canaux depuis 2011")
 ) 

p.save("PV-Channel-smooth.png", bbox_inches="tight", dpi=600)

##Remarque : certains paramètres d'affichage ne sont pas implémentés comme
##par exemple caption.
#sauvegarde de dateChannel_data
dateChannel_data.to_csv("dateChannel_data.csv", sep=";", index=False) 


##########################################################################
# Pour le traffic de base
##########################################################################
#Relecture ############
myDateToParse = ['date']  #pour parser la variable date en datetime sinon object
dfBasePageViews = pd.read_csv("dfBasePageViews.csv", sep=";", dtype={'Année':object}, parse_dates=myDateToParse)
#verifs
dfBasePageViews.dtypes
dfBasePageViews.count()  #37615
dfBasePageViews.head(20)

#On vire les blancs pour faire  le merge on
dfBasePageViews['source'] = dfBasePageViews['source'].str.strip()
mySourcesChannel['source'] = mySourcesChannel['source'].str.strip()

#récuperation de la variable channel dans la dataframe principale par un left join.
dfBasePVChannel = pd.merge(dfBasePageViews, mySourcesChannel, on='source', how='left')
dfBasePVChannel.info()
#voyons ce que l'on a comme valeurs.
dfBasePVChannel['channel'].value_counts()
sorted(dfBasePVChannel['channel'].unique())

#création de la dataframe dateChannel_BaseData  par jour et canal
dfDateBasePVChannel = dfBasePVChannel[['date', 'channel', 'pageviews']].copy() #nouveau dataframe avec que la date et les canaux
dfDateBasePVChannel.info()
dateChannel_baseData = dfDateBasePVChannel.groupby(['date', 'channel']).count() #
#dans l'opération précédente la date et le channel sont partis dans l'index
dateChannel_baseData = dateChannel_baseData.reset_index() #recrée les colonnes date et channel
dateChannel_baseData['Année'] = dateChannel_baseData['date'].astype(str).str[:4] #ajoute l'année
dateChannel_baseData.info()
dateChannel_baseData.sort_values(by=['date', 'channel'])
dateChannel_baseData.head(20)
##########################################################################
# Graphique en barre général Répartition du trafic selon les canaux.
##########################################################################
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot
sns.barplot(x='channel', y='pageviews', data=dateChannel_baseData, estimator=sum, order=sorted(dfBasePVChannel['channel'].unique()))                
fig.suptitle("Le canal 'search' est le premier contributeur en termes de trafic.", fontsize=14, fontweight='bold')
ax.set(xlabel="Canal", ylabel="Pages vues",
       title="Le canal 'direct' (fourre tout) est malheureusement important aussi ici.")
fig.text(.35,-.03,"Trafic de Base - Pages vues selon les canaux depuis 2011", fontsize=9)
#plt.show()
fig.savefig("Base-PV-Channel-bar.png", bbox_inches="tight", dpi=600)

##########################################################################
#Graphique en barre par année
#Répartition du trafic selon les canaux.
##########################################################################
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
g=sns.FacetGrid(dateChannel_baseData, col="Année", col_wrap=3) 
g.map(sns.barplot, 'channel', 'pageviews', palette="deep",  estimator=sum, order=sorted(dfBasePVChannel['channel'].unique()))
plt.subplots_adjust(top=0.9)
g.fig.suptitle("La contribution relative du canal 'search' reste forte tous les ans.\n mais varie fortement en valeur absolue", fontsize=14, fontweight='bold')
g.set(xlabel="Canal", ylabel="Pages vues")
g.set_xticklabels(fontsize=9)
g.fig.text(.35,-.00,"Trafic de Base - Pages vues selon les années et les canaux depuis 2011", fontsize=9)
#plt.show()
g.savefig("Base-PV-Channel-bar-an.jpeg.png", bbox_inches="tight", dpi=600)


###################################################################################
###### Avec  Plotline 
p = (ggplot(dateChannel_baseData) +
 stat_smooth(aes('date', 'pageviews', color='channel'), method='loess', span=0.4) +
 ylab("Pages vues") +
 scale_x_datetime(breaks=date_breaks('2 years')) +       # new
 ggtitle("Comme précédemment, Le canal 'search' a augmenté jusqu'en 2015 \n puis a baissé fortement.\nLes autres canaux ont régulièrement baissé, avec une légère reprise en 2018") +
 xlab("Date\nTrafic de Base - Evolution lissée des pages vues selon les canaux depuis 2011")
 ) 

p.save("Base-PV-Channel-smooth.png", bbox_inches="tight", dpi=600)


##########################################################################
#regardons pour le trafic Direct  Marketing uniquement i.e le traffic dont
# la source a dirigé vers une page Articles Marketing 
##########################################################################
#Relecture ############
myDateToParse = ['date']  #pour parser la variable date en datetime sinon object
dfDMPageViews = pd.read_csv("dfDMPageViews.csv", sep=";", dtype={'Année':object}, parse_dates=myDateToParse)
#verifs
dfDMPageViews.dtypes
dfDMPageViews.count()  #28553
dfDMPageViews.head(20)

#On vire les blancs pour faire  le merge on
dfDMPageViews['source'] = dfDMPageViews['source'].str.strip()
mySourcesChannel['source'] = mySourcesChannel['source'].str.strip()
#recuperation de la variable channel dans la dataframe principale par un left join.
dfDMPVChannel = pd.merge(dfDMPageViews, mySourcesChannel, on='source', how='left')
dfDMPVChannel.info()
#voyons ce que l'on a comme valeurs.
dfDMPVChannel['channel'].value_counts()
sorted(dfDMPVChannel['channel'].unique())

#creation de la dataframe dateChannel_DMData  par jour et canal
dfDateDMPVChannel = dfDMPVChannel[['date', 'channel', 'pageviews']].copy() #nouveau dataframe avec que la date et les canaux
dfDateDMPVChannel.info()
dateChannel_DMData = dfDateDMPVChannel.groupby(['date', 'channel']).count() #
#dans l'opération précédente la date et le channel sont partis dans l'index
dateChannel_DMData = dateChannel_DMData.reset_index() #recrée les colonnes date et channel
dateChannel_DMData['Année'] = dateChannel_DMData['date'].astype(str).str[:4] #ajoute l'année
dateChannel_DMData.info()
dateChannel_DMData.sort_values(by=['date', 'channel'])
dateChannel_DMData.head(20)
##########################################################################
# Graphique en barre général Répartition du trafic selon
#les canaux pour le trafic Direct Marketing
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot
sns.barplot(x='channel', y='pageviews', data=dateChannel_DMData, estimator=sum, order=sorted(dfDMPVChannel['channel'].unique()))                
fig.suptitle("Comme précédemment, le canal Search est le premier contributeur en termes de trafic.", fontsize=12, fontweight='bold')
ax.set(xlabel="Canal", ylabel="Pages vues",
       title="Le canal 'direct' (fourre tout) est malheureusement important aussi.")
fig.text(.35,-.03,"Direct Marketing - Pages vues selon les canaux depuis 2011", fontsize=9)
#plt.show()
fig.savefig("DM-PV-Channel-bar.png", bbox_inches="tight", dpi=600)

##########################################################################
#Graphique en barre par année
#Répartition du trafic direct marketing selon les sources.

sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
g=sns.FacetGrid(dateChannel_DMData, col="Année", col_wrap=3) 
g.map(sns.barplot, 'channel', 'pageviews', palette="deep",  estimator=sum, order=sorted(dfDMPVChannel['channel'].unique()))
plt.subplots_adjust(top=0.9)
g.fig.suptitle("La contribution relative du canal 'search' a augmenté de 2011 à 2013.\n puis s'est stabilisée.", fontsize=12, fontweight='bold')
g.set(xlabel="Canal", ylabel="Pages vues")
g.set_xticklabels(fontsize=9)
g.fig.text(.35,-.00,"Direct Marketing - Pages vues selon les années et les canaux depuis 2011", fontsize=9)
#plt.show()
g.savefig("DM-PV-Channel-bar-an.jpeg.png", bbox_inches="tight", dpi=600)


###################################################################################
###### Avec  Plotline 
#evolution des pages vues selon les canaux pour le trafic direct marketing

p = (ggplot(dateChannel_DMData) +
 stat_smooth(aes('date', 'pageviews', color='channel'), method='loess', span=0.4) +
 ylab("Pages vues") +
 scale_x_datetime(breaks=date_breaks('2 years')) +       # new
 ggtitle("Ici les canaux 'direct' et 'social' étaient plus important que le 'search' \n dans les premières années.\nLa forme de la courbe du canal search' ne semble pas avoir beaucoup varié \n par rapport au trafic de base ou global.") +
 xlab("Date\nDirect Marketing - Evolution lissée des pages vues selon les canaux depuis 2011")
 ) 

p.save("DM-PV-Channel-smooth.png", bbox_inches="tight", dpi=600)


##########################################################################
#  Comparatif DM vs Base
#evolution des pages vues selon les canaux pour le trafic direct marketing vs Base
############################################################################
p = (ggplot() + 
 stat_smooth(aes('date', 'pageviews', color='channel'), data=dateChannel_baseData, method='loess', span=0.4, se = False) +
 stat_smooth(aes('date', 'pageviews', color='channel'), data=dateChannel_DMData, method='loess', span=0.4, se = False, linetype='dashed') +
 ylab("Pages vues") +
 scale_x_datetime(breaks=date_breaks('2 years')) +       # new
 ggtitle("Le canal 'search' évolue de façon équivalente selon le type de pages \n mais avec beaucoup moins de trafic pour les pages Marketing. \nLes formes des courbes 'social' et 'direct' diffèrent.") +
 xlab("Date\nBase (lignes pleines) vs Direct Marketing (pointillés)  - Evolution lissée des pages vues selon les canaux depuis 2011")
 ) 

p.save("Base-DM-PV-Channel-smooth.png", bbox_inches="tight", dpi=600)


#Comparatif des proportions
#proportions des différents trafics 
propDMBase = len(dfDMPVChannel.index) / len(dfBasePVChannel.index)  #0.76
myPropDMBase = pd.DataFrame(data={'channel' : ["direct", "referral", "search", "social", "webmail"], 
                                  'proportion' : [0,0,0,0,0]})
myPropDMBase.loc[0, "proportion"] = sum(dfDMPVChannel.channel=="direct") / sum(dfBasePVChannel.channel=="direct") #0.81
myPropDMBase.loc[1, "proportion"] = sum(dfDMPVChannel.channel=="referral") / sum(dfBasePVChannel.channel=="referral")  #0.29
myPropDMBase.loc[2, "proportion"] = sum(dfDMPVChannel.channel=="search") / sum(dfBasePVChannel.channel=="search") #0.66
myPropDMBase.loc[3, "proportion"] = sum(dfDMPVChannel.channel=="social") / sum(dfBasePVChannel.channel=="social") #1.25
myPropDMBase.loc[4, "proportion"] = sum(dfDMPVChannel.channel=="webmail") / sum(dfBasePVChannel.channel=="webmail") #1.26

p = (ggplot(myPropDMBase) + 
 geom_point(aes('channel', 'proportion', color='channel'), size=5) +
 geom_hline(yintercept = propDMBase, color= "red" ) +
 ylab("Proportion Direct Marketing / Base") +
 ggtitle("Le traffic Direct Marketing est composé en proportion plus importante \n de trafic direct, social et webmail.\nLe trafic de base de referral et de search.") +
 xlab("Date\nProportions Direct Marketing / Base selon les canaux - Total depuis 2011")
 ) 
p.save("Base-DM-PV-Channel-prop.png", bbox_inches="tight", dpi=600)


#verification que les proportions sont statistiquement valides.
from statsmodels.stats.proportion import proportions_ztest
#trafic direct 
#H0 prop direct/total DM <= direct/total base,  
#H1 : prop direct/total DM > direct/total base, (p.value << 0.05)
#2-sample test
myNobs = np.array([sum(dfBasePVChannel.channel=="direct"), len(dfBasePVChannel.index)])
myCount = np.array([sum(dfDMPVChannel.channel=="direct"), len(dfDMPVChannel.index) ]) 
stat, pval = proportions_ztest(nobs=myNobs, count=myCount, alternative='larger') 
print('{0:0.3f}'.format(pval)) #0.000
#trafic referral
#H0 prop referral/total DM >= referral/total base,  
#H1 : prop referral/total DM < referral/total base, (p.value << 0.05)
#2-sample test
myNobs = np.array([sum(dfBasePVChannel.channel=="referral"), len(dfBasePVChannel.index)])
myCount = np.array([sum(dfDMPVChannel.channel=="referral"), len(dfDMPVChannel.index) ]) 
stat, pval = proportions_ztest(nobs=myNobs, count=myCount, alternative='smaller') 
print('{0:0.3f}'.format(pval)) #0.000
#trafic search
#H0 prop search/total DM >= search/total base ,  
#H1 : prop search/total DM < search/total base (p.value << 0.05)
myNobs = np.array([sum(dfBasePVChannel.channel=="search"), len(dfBasePVChannel.index)])
myCount = np.array([sum(dfDMPVChannel.channel=="search"), len(dfDMPVChannel.index) ]) 
stat, pval = proportions_ztest(nobs=myNobs, count=myCount, alternative='smaller') 
print('{0:0.3f}'.format(pval)) #0.000
#trafic social 
#H0 prop social/total DM <= social/total base,  
#H1 : prop social/total DM > social/total base, (p.value << 0.05)
myNobs = np.array([sum(dfBasePVChannel.channel=="social"), len(dfBasePVChannel.index)])
myCount = np.array([sum(dfDMPVChannel.channel=="social"), len(dfDMPVChannel.index) ]) 
stat, pval = proportions_ztest(nobs=myNobs, count=myCount, alternative='larger') 
print('{0:0.3f}'.format(pval)) #0.000
#trafic webmail
#H0 prop webmail/total DM <= webmail/total base,  
#H1 : prop webmail/total DM > webmail/total base, (p.value << 0.05)
myNobs = np.array([sum(dfBasePVChannel.channel=="webmail"), len(dfBasePVChannel.index)])
myCount = np.array([sum(dfDMPVChannel.channel=="webmail"), len(dfDMPVChannel.index) ]) 
stat, pval = proportions_ztest(nobs=myNobs, count=myCount, alternative='larger') 
print('{0:0.3f}'.format(pval)) #0.000

dfDMPVChannel.to_csv("dfDMPVChannel.csv", sep=";", index=False)  #on sauvegarde pour plus tard





##########################################################################
# ACP - Analyse en Composantes Principales pour le 
# trafic Direct Marketing - Chaque observation est une page 
##########################################################################
#Recupération des données
myDateToParse = ['date']  #pour parser la variable date en datetime sinon object
dfDMPVChannel = pd.read_csv("dfDMPVChannel.csv", sep=";", dtype={'Année':object}, parse_dates=myDateToParse)
myArticles = pd.read_csv("myArticles.csv", sep=";", dtype={'Année':object}, parse_dates=myDateToParse)

#verifs
dfDMPVChannel.info()

######################################################################
#il faut nettoyer les landing pages. Normalement on doit en avoir 95 
#différentes que l'on va prendre dans myArticles
#voyons ce que l'on a 
dfDMPVChannel['landingPagePath'].value_counts()
#nettoyage des urls en doublons ou curieuses
dfDMPVChannel['cleanLandingPagePath'] = dfDMPVChannel['landingPagePath'].str.split("?", n = 1, expand = True)[0] 
dfDMPVChannel['cleanLandingPagePath'] = dfDMPVChannel['cleanLandingPagePath'].str.split("&", n = 1, expand = True)[0] 
dfDMPVChannel['cleanLandingPagePath'] = dfDMPVChannel['cleanLandingPagePath'].str.split("<", n = 1, expand = True)[0] 
dfDMPVChannel['cleanLandingPagePath'] = dfDMPVChannel['cleanLandingPagePath'].str.split("/ngg", n = 1, expand = True)[0] 
dfDMPVChannel['cleanLandingPagePath'] = dfDMPVChannel['cleanLandingPagePath'].str.split(")", n = 1, expand = True)[0]
dfDMPVChannel['cleanLandingPagePath'].value_counts()
#on va nettoyer avec un inner_join 
dfDMPVChannel.info() #28553
myArticles.info() #95
#######
myCleanLandingPagePath = myArticles[['pagePath']].copy()
myCleanLandingPagePath.rename(columns={'pagePath':'cleanLandingPagePath'} , inplace = True)
myCleanLandingPagePath.info()


dfDMPVChannelClean = pd.merge(dfDMPVChannel, myCleanLandingPagePath, on='cleanLandingPagePath', how='inner')
dfDMPVChannelClean.info() #28481 obs  on en a perdu environ 80
dfDMPVChannelClean.to_csv("dfDMPVChannelClean.csv", sep=";", index=False)  #on sauvegarde pour plus tard


#creation de la dataframe LPPChannel_DMDataForACP par page et canal 
dfDMPVChannelCleanLPP = dfDMPVChannelClean[['cleanLandingPagePath', 'channel', 'pageviews']].copy() #nouveau dataframe avec que la date et les canaux
dfDMPVChannelCleanLPP.info()
LPPChannel_DMDataForACP = dfDMPVChannelCleanLPP.groupby(['cleanLandingPagePath','channel']).count() #
LPPChannel_DMDataForACP.reset_index(inplace=True)
LPPChannel_DMDataForACP.info()

#création d'une colonne par type de channel
LPPChannel_DMDataForACPP = LPPChannel_DMDataForACP.pivot(index='cleanLandingPagePath',columns='channel',values='pageviews')

#Mettre des 0 à la place de NaN
LPPChannel_DMDataForACPP .fillna(0,inplace=True)
LPPChannel_DMDataForACPP.to_csv("LPPChannel_DMDataForACPP.csv", sep=";", index=False)  #on sauvegarde pour plus tard
LPPChannel_DMDataForACPP.info()  #description des données
LPPChannel_DMDataForACPP.describe() #résumé des données

#tests de normalité shapiro wilk
#direct
myW, myPValeur = stats.shapiro(LPPChannel_DMDataForACPP['direct'].values)
myW, myPValeur
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.distplot(LPPChannel_DMDataForACPP['direct'].values, hist=False)
ax.set_xlim(0,None)
#referral
myW, myPValeur = stats.shapiro(LPPChannel_DMDataForACPP['referral'].values)
myW, myPValeur
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.distplot(LPPChannel_DMDataForACPP['referral'].values, hist=False)
ax.set_xlim(0,None)
#search  on fait un vrai graphique 
myW, myPValeur = stats.shapiro(LPPChannel_DMDataForACPP['search'].values)
myW, myPValeur
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.distplot(LPPChannel_DMDataForACPP['search'].values, hist=False)
ax.set_xlim(0,None)
fig.suptitle("la variable search montre clairement que peu de pages \n concourent à beaucoup de trafic \ni.e : peu de pages sont bien référencées dans Google.", fontsize=10, fontweight='bold')
ax.set(xlabel="Nombre de Vues", ylabel='Densité',
       title="")
fig.text(.9,-.05,"Direct Marketing : Distribution du trafic 'search' selon les pages", fontsize=9, ha="right")
#plt.show()
fig.savefig("DM-Distribution-PV-search.", bbox_inches="tight", dpi=600)

#social
myW, myPValeur = stats.shapiro(LPPChannel_DMDataForACPP['social'].values)
myW, myPValeur
#webmail
myW, myPValeur = stats.shapiro(LPPChannel_DMDataForACPP['webmail'].values)
myW, myPValeur
#rem aucune distribution n'est normale 

#matrice de corrélation avec méthode de Spearman 
LPPChannel_DMDataForACPP.corr(method='spearman')

#####################################################################
# ACP Non normée Covariance celle que l'on avait avec R
#####################################################################
from sklearn.decomposition import PCA
X=LPPChannel_DMDataForACPP.values #uniquement les valeurs dans une matrice.
pcaNN = PCA(n_components=5)  #5 composantes
pcaNN.fit(X)


pcaNN.components_.T
pcaNN.explained_variance_
pcaNN.explained_variance_ratio_   #en pourcentage
pcaNN.explained_variance_ratio_[0] #Pourcentage de variance expliquée dans la 1ere Composante
#Préparation des données en DataFrame pour affichage
dfPcaNN = pd.DataFrame(data = pcaNN.explained_variance_ratio_
             , columns = ['Variance Expliquée'])
dfPcaNN.index.name = 'Composantes'
dfPcaNN.reset_index(inplace=True)
dfPcaNN['Composantes'] +=1

#Graphique Screeplot
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.barplot(x='Composantes', y= 'Variance Expliquée', data=dfPcaNN)
#fig.suptitle("La première composante comprend déja " + "{0:.2f}%".format(pca.explained_variance_ratio_[0]*100) + "de l'information", fontsize=10, fontweight='bold')
ax.set(xlabel='Composantes', ylabel='% Variance Expliquée',
       title="La première composante comprend déja " + "{0:.2f}%".format(pcaNN.explained_variance_ratio_[0]*100) + "de l'information")
fig.text(.9,-.05,"Screeplot du % de variance des composantes de l'ACP Non Normée \n pour les canaux Direct Marketing", fontsize=9, ha="right")
#plt.show()
fig.savefig("DM-PCA-NN-screeplot-channel.png", bbox_inches="tight", dpi=600)



##############
##nuage des individus et axes des variables
#Labels
labels=LPPChannel_DMDataForACPP.columns.values  

score= X[:,0:2]
coeff=np.transpose(pcaNN.components_[0:2, :])
n = coeff.shape[0]


xs = score[:,0]
ys = score[:,1]  
#
scalex = 1.0/(xs.max() - xs.min())
scaley = 1.0/(ys.max() - ys.min())

#Graphique du nuage des pages et des axes des variables.
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.scatterplot(xs * scalex,ys * scaley, alpha=0.4) #
for i in range(n):
    ax.arrow(0, 0, coeff[i,0]*1, coeff[i,1]*1,color = 'r',alpha = 0.5, head_width=.03)
    ax.text(coeff[i,0]*1.15, coeff[i,1]*1.15 , labels[i], color = 'r', ha = 'center', va = 'center')
ax.set(xlabel='Composante 1', ylabel='Composante 2',
       title="search est quasiment dans l'axe de la composante 1 \n direct, webmail et social et un peu moins referral sont \n quasiment tous perpendiculaires à search")
ax.set_ylim((-1, 1.1))
fig.text(.9,-.05,"Nuage des pages et axes des variables non normalisées \n pour les canaux Direct Marketing", fontsize=9, ha="right")
#plt.show()
fig.savefig("DM-PCA-NN-cloud-channell.png", bbox_inches="tight", dpi=600)


#####################################################################
# ACP Normée StandardScaler : Corrélation Pearson  celle que 
# l'on avait avec SAS exemple 1
#####################################################################
##nuage des individus et axes des variables

X=LPPChannel_DMDataForACPP.values  #uniquement les valeurs dans une matrice.

from sklearn.preprocessing import StandardScaler  #import du module 

scaler = StandardScaler() #instancie un objet StandardScaler
scaler.fit(X) #appliqué aux données
X_scaled = scaler.transform(X) #données transformées 

pcaSP = PCA(n_components=5) #instancie un objet PCA
pcaSP.fit(X_scaled)  #appliqué aux données scaled

pcaSP.components_.T
pcaSP.explained_variance_
pcaSP.explained_variance_ratio_   #en pourcentage
pcaSP.explained_variance_ratio_[0]
#Préparation des données pour affichage
dfPcaSP = pd.DataFrame(data = pcaSP.explained_variance_ratio_
             , columns = ['Variance Expliquée'])
dfPcaSP.index.name = 'Composantes'
dfPcaSP.reset_index(inplace=True)
dfPcaSP['Composantes'] +=1

#Graphique
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.barplot(x='Composantes', y= 'Variance Expliquée', data=dfPcaSP )
#fig.suptitle("La première composante comprend déja " + "{0:.2f}%".format(pca.explained_variance_ratio_[0]*100) + "de l'information", fontsize=10, fontweight='bold')
ax.set(xlabel='Composantes', ylabel='% Variance Expliquée',
       title="La première composante comprend " + "{0:.2f}%".format(pcaSP.explained_variance_ratio_[0]*100) + "de l'information")
fig.text(.9,-.05,"Screeplot du % de variance des composantes de l'ACP Normalisée \n Corrélation de Pearson pour les canaux Direct Marketing", fontsize=9, ha="right")
#plt.show()
fig.savefig("DM-PCA-StandardScaler-Pearson-screeplot-channel.png", bbox_inches="tight", dpi=600)


##############
##nuage des individus et axes des variables

score= X_scaled[:,0:2]
coeff=np.transpose(pcaSP.components_[0:2, :])
n = coeff.shape[0]

xs = score[:,0]
ys = score[:,1]  
#
scalex = 1.0/(xs.max() - xs.min())
scaley = 1.0/(ys.max() - ys.min())

#Graphique du nuage des pages et des axes des variables.
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.scatterplot(xs * scalex,ys * scaley, alpha=0.4) #
for i in range(n):
    ax.arrow(0, 0, coeff[i,0]*1, coeff[i,1]*1,color = 'r',alpha = 0.5, head_width=.03)
    ax.text(coeff[i,0]*1.15, coeff[i,1]*1.15 , labels[i], color = 'r', ha = 'center', va = 'center')
ax.set(xlabel='Composante 1', ylabel='Composante 2',
       title="Les variables sont toutes du même bord de l'axe principal 1 \n Sur l'axe 2 Referral se détache légèrement")
ax.set_ylim((-0.7, 1.1))

fig.text(.9,-.05,"Nuage des pages et axes des variables Normalisées via StandardScaler \n Corrélation de Pearson pour les canaux Direct Marketing", fontsize=9, ha="right")
#plt.show()
fig.savefig("DM-PCA-StandardScaler-Pearson-cloud-channel.png", bbox_inches="tight", dpi=600)


#####################################################################
# ACP Normée StantardScaler Corrélation Spearman celle que l'on avait 
# avec SAS exemple 2
#####################################################################
##nuage des individus et axes des variables
X=LPPChannel_DMDataForACPP.values  #uniquement les valeurs dans une matrice.
X=X.ravel().argsort().argsort().reshape(X.shape) #Matrice des rangs pour Spearman
from sklearn.preprocessing import StandardScaler  #import du module 

scaler = StandardScaler() #instancie un objet StandardScaler
scaler.fit(X) #appliqué aux données
X_scaled = scaler.transform(X) #données transformées 

pcaSS = PCA(n_components=5) #instancie un objet PCA
pcaSS.fit(X_scaled)  #appliqué aux données scaled

pcaSS.components_.T
pcaSS.explained_variance_
pcaSS.explained_variance_ratio_   #en pourcentage ce qui nous intéresse
pcaSS.explained_variance_ratio_[0]
#Préparation des données pour affichage
dfPcaSS = pd.DataFrame(data = pcaSS.explained_variance_ratio_
             , columns = ['Variance Expliquée'])
dfPcaSS.index.name = 'Composantes'
dfPcaSS.reset_index(inplace=True)
dfPcaSS['Composantes'] +=1

#Graphqiue
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.barplot(x='Composantes', y= 'Variance Expliquée', data=dfPcaSS )
#fig.suptitle("La première composante comprend déja " + "{0:.2f}%".format(pca.explained_variance_ratio_[0]*100) + "de l'information", fontsize=10, fontweight='bold')
ax.set(xlabel='Composantes', ylabel='% Variance Expliquée',
       title="La première composante comprend " + "{0:.2f}%".format(pcaSS.explained_variance_ratio_[0]*100) + "de l'information")
fig.text(.9,-.05,"Screeplot du % de variance des composantes de l'ACP Normalisée \n Corrélation de Spearman pour les canaux Direct Marketing", fontsize=9, ha="right")
#plt.show()
fig.savefig("DM-PCA-StandardScaler-Spearman-screeplot-channel.png", bbox_inches="tight", dpi=600)


##############
##nuage des individus et axes des variables
score= X_scaled[:,0:2]
coeff=np.transpose(pcaSS.components_[0:2, :])
n = coeff.shape[0]

xs = score[:,0]
ys = score[:,1]  
#
scalex = 1.0/(xs.max() - xs.min())
scaley = 1.0/(ys.max() - ys.min())

#Graphique du nuage des pages et des axes des variables.
sns.set()  #paramètres esthétiques ressemble à ggplot par défaut.
fig, ax = plt.subplots()  #un seul plot 
sns.scatterplot(xs * scalex,ys * scaley, alpha=0.4) #
for i in range(n):
    ax.arrow(0, 0, coeff[i,0]*1, coeff[i,1]*1,color = 'r',alpha = 0.5, head_width=.03)
    ax.text(coeff[i,0]*1.15, coeff[i,1]*1.15 , labels[i], color = 'r', ha = 'center', va = 'center')
ax.set(xlabel='Composante 1', ylabel='Composante 2',
       title="Les variables sont toutes du même bord de l'axe principal 1 \n Sur l'axe 2 Referral se détache nettement")
ax.set_ylim((-0.6, 1.1))

fig.text(.9,-.05,"Nuage des pages et axes des variables Normalisée avec StandardScaler \n Corrélation de Spearman pour les canaux Direct Marketing", fontsize=9, ha="right")


#plt.show()
fig.savefig("DM-PCA-StandardScaler-Spearman-cloud-channel.png", bbox_inches="tight", dpi=600)




##########################################################################
# MERCI pour votre attention !
##########################################################################
#on reste dans l'IDE
#if __name__ == '__main__':
#  main()

