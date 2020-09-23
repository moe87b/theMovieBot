import os
import discord
from dotenv import load_dotenv
import requests
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
MOVIE_TOKEN = os.getenv("MOVIE_TOKEN")
client = discord.Client()
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    #!m command
    if message.content[:2] == '!m':
        if message.content == '!m help':
            await message.channel.send("""
        There are 4  commands:
        help, movie, search and genre. 
        You can call each one by sending !m *command name*. 
        movie: gives you information about a specific movie
        search: gives you a list of movie titles
        genre: shows the available movie genres
        """)
        if message.content[:8] == "!m movie":
            name = message.content[9:]
            data = movie(name)
            if type(data) == str:
                await message.channel.send(data)
                return
            await message.channel.send('Title: {} \nCatogories: {} \nRelease date: {} \nVote average: {} \nOverview: {} \n Poster: {}'.format(data['title'], data['categories'], data['release date'], data['vote average'], data['overview'], data['poster']))
        
        if message.content[:11] == "!m searchid":
            id = message.content[12: ]
            data = searchid(id)
            if type(data) == str:
                await message.channel.send(data)
                return
            await message.channel.send('Title: {} \nCatogories: {} \nRelease date: {} \nVote average: {} \nOverview: {} \n Poster: {}'.format(data['title'], data['categories'], data['release date'], data['vote average'], data['overview'], data['poster']))
            
            

            return

        if message.content[:9] == '!m search':
            name = message.content[10:]
            header = 'Results for "{}" Page 1'.format(name)
            data = search(name, 1)
            response = header
        if data == []:
                response = response+"\n Sorry, no results found"
        for x in data:
            response = response+"\n"+x
        response = response+"\n React to this message to show more results"
        await message.channel.send(response)
        if message.content[:9] == "!m genres":
            data = genre()
            toSend = ""
            for x in data:
                toSend = toSend+x+"\n"
            await message.channel.send(toSend)
        
        
        
@client.event
async def on_reaction_add(reaction, user):
    message = reaction.message
    if message.content[:11].lower() == "results for":
        startindex = message.content.rfind('"')
        endIndex = message.content.find('1-')
        oldPage = message.content[startindex+7: endIndex-1]
        oldPage = oldPage.strip()
        oldPage = int(oldPage)
        
        startindexName = message.content.find('"')
        name = message.content[startindexName+1: startindex]
        data = search(name, oldPage+1)
        response =  'Results for "{}" Page {}'.format(name, oldPage+1)
        if data == []:
            response = response+"\n Sorry, no results found"
        for x in data:
            response = response+"\n"+x
        response = response+"\n React to this message to show more results"
        await message.channel.send(response)
@client.event
async def on_ready():
    print("connected")
def movie(name, lang='en'):
    resp = requests.get("https://api.themoviedb.org/3/search/movie?api_key="+MOVIE_TOKEN+"&query="+name+"&language="+lang)
    if resp.json()['total_results'] == 0:
        return "Sorry, no results found"
    movieResp = resp.json()['results'][0]
    genres = requests.get("https://api.themoviedb.org/3/genre/movie/list?api_key=e2aa2c645f727e2db2ed46201b36c7f6").json()['genres']    
    movieGenresId = movieResp['genre_ids']
    
    
    res = {}    
    res['title'] = movieResp['title']
    res['vote average'] = movieResp['vote_average']
    res['overview'] = movieResp['overview']
    res['release date'] = movieResp['release_date']
    category = ""
    for x in genres:
        if x['id'] in movieGenresId:
            category = category+x['name']+", "
    res['categories'] = category
    if movieResp['poster_path'] != "" and movieResp['poster_path'] != None:
        res['poster'] = "https://image.tmdb.org/t/p/original"+movieResp['poster_path']
    else:
        res['poster'] = "Not available"
    return res

def genre():
    response = requests.get("https://api.themoviedb.org/3/genre/movie/list?api_key="+MOVIE_TOKEN)
    genres = response.json()
    res  =[]
    for x in genres['genres']:
        res.append(x['name'])
    return res

def search(movie, page=1):
    resp = requests.get("https://api.themoviedb.org/3/search/movie?api_key="+MOVIE_TOKEN+"&query="+movie+"&page="+str(page))
    res = []
    count = 0
    if resp.json()['total_results'] == 0:
            return res
    for x in resp.json()['results']:
        count = count +1
        res.append(str(count)+"- "+x['title']+" - "+str(x['id']))
    
    return res

def searchid(id):
    resp = requests.get("https://api.themoviedb.org/3/movie/"+id+"?api_key=e2aa2c645f727e2db2ed46201b36c7f6&language=en-US")
    data = resp.json()
    if 'success' in data:
        return "Sorry, no results found"
    genresData = data['genres']
    res = {}
    res['title'] = data['original_title']
    res['vote average'] = data['vote_average']
    res['overview'] = data['overview']  
    res['release date'] = data['release_date']
    if data['poster_path'] != "" and data['poster_path'] != None:
        res['poster'] = "https://image.tmdb.org/t/p/original"+data['poster_path']
    else:
        res['poster'] = "Not available"
    
    genres = ""
    for x in genresData:
        genres = genres+x['name']+", "
    
    print(genres)
    res['categories'] = genres
    
    return res

client.run(TOKEN)