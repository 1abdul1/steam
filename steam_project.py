# -------------------------------------------------IMPORTS-------------------------------------------------#
import threading
import PySimpleGUI as sg
import json
from urllib.request import urlopen
import requests
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import sshpi

# -------------------------------------------------PRE-VALUES-------------------------------------------------#
API_key = 'AF90EFF02499BB3CDDFFF28629DEA47B'
game_list = []
game_data = []
tempo = []
percentage = 0
gen_list = []
user_data_lst = []
# -------------------------------------------------COLUMNS-------------------------------------------------#
user_column = [  # De eerste Colom waar de gebruikersnaam kan worden ingevuld en de algemen data komt
    [(sg.Text('Username: ')),
     (sg.Input(size=(25, 20), key='_USER_')),
     (sg.Button('Search', key='_SEARCH_'))
     ],
    [sg.Listbox(values=gen_list, enable_events=True, size=(55, 10), k='_GENERAL_')]
]

file_list_column = [  # De gebruikers bibliotheek weergeven met een zoek functie
    [sg.Text('Search Game: ', size=(10, 1)),
     sg.Input(do_not_clear=True, size=(30, 1), enable_events=True, key='_INPUT_'),
     ],
    [sg.Listbox(values=game_list, enable_events=True, size=(55, 20), key='_LIST_')], ]

game_data_column = [  # Alle game data van de aangeklikte game weergeven
    [(sg.Text("Game data will be displayed here:")), ],
    [(sg.Listbox(values=game_data, enable_events=True, size=(55, 20), expand_x=True, expand_y=True, key='_DATA_'))],
]

# -------------------------------------------------TABS-------------------------------------------------#

tab1 = [[sg.Canvas(size=(1250, 600), k='_TIME_GRAPH_')]]  # Verschillende tabs voor de unieke data
tab2 = [[sg.Canvas(size=(1250, 600), k='_GEN_GRAPH_')]]
tab3 = [[sg.Canvas(size=(1250, 600), k='_Time_GEN_')]]
tab5 = [[sg.Canvas(size=(1250, 600), k='_CSGO_')]]

tab_group_layout = [[sg.Tab('Time Graph', tab1, font='Courier 15', key='_TIME_GRAPH_', expand_x=True),
                     sg.Tab('Genre Graph', tab2, font='Courier 15', key='_GEN_GRAPH_', expand_x=True),
                     sg.Tab('Time per Genre', tab3, font='Courier 15', key='_Time_GEN_', expand_x=True),
                     sg.Tab('CS:GO Stats', tab5, font='Courier 15', key='_CSGO_', expand_x=True),
                     ]]

# -------------------------------------------------LAYOUT-------------------------------------------------#

layout = [  # volgorde van de layout van links naar rechts
    [sg.Frame(layout=user_column, title='', border_width=0, vertical_alignment='top'),
     sg.Frame(layout=file_list_column, title='', border_width=0, vertical_alignment='top'),
     sg.Frame(layout=game_data_column, title='', border_width=0, vertical_alignment='top'), ],
    [sg.TabGroup(layout=tab_group_layout, enable_events=True, )]
]
window = sg.Window("Victis-Victis Add-On", layout, size=(1380, 960), element_justification='center', resizable=True,
                   finalize=True)
window.Maximize()
window.finalize()
window['_LIST_'].expand(True, True, True)


# -------------------------------------------------FUNCTIONS-------------------------------------------------#

# --------URL Functies--------#
def URL1(username):  # User ID opvragen
    URL = f'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={API_key}&vanityurl={username}'
    return URL


def URL2(steam_id):  # Games Opvragen
    URL = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={API_key}&steamid={steam_id}&format=json&include_appinfo=1"
    return URL


def URL3(appid, steam_id):  # User stats van een game opvragen
    URL = f'http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid={appid}&key={API_key}&steamid={steam_id}'
    return URL


def URL4(appid):  # Alle achievements opvragen
    URL = f'http://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/?gameid={appid}&format=json'
    return URL


def URL5():  # Friendlist
    URL = f' http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={API_key}&steamid={steam_id}&relationship=friend'
    return URL


def URL6():  # playersummaries
    URL = f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={API_key}&steamids={steam_id}'
    return URL


def URL7():  # GetOwnedGames
    URL = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={API_key}&steamid={steam_id}&format=json'
    return URL


def URL8():  # Get Player Bans
    URL = f'https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key={API_key}&steamids={steam_id}'
    return URL


# --------Data Functies--------#
def append():  # Zorgt ervoor dat de userbanned, recently_played, friendlst, playersumaries in een Listbox worden gezet.
    x = userbanned()
    y = recently_played()
    z = friendlst()
    u = playersumaries()
    user_data_lst.clear()
    user_data_lst.append(f'Steam persona name:              {u[0]}')
    user_data_lst.append(f'User Since:                             {u[2]}')
    user_data_lst.append(f'Country code:                          {u[1]}')
    user_data_lst.append(f'How many friends on steam:     {z}')
    user_data_lst.append(f'Hours played last 2 weeks:       {y}')
    user_data_lst.append(f'vacbans:                                  {x}')

    window.Element('_GENERAL_').update(user_data_lst)


def userbanned():  # fetch data van de steam api over de userdata qua bans
    userbanned_json = urlopen(URL8())
    userbanned = json.loads(userbanned_json.read())
    for x in userbanned['players']:
        VAC = x["NumberOfVACBans"]
    return VAC


def recently_played():  # hoeveel de user heeft gespeeld in de laatste 2 weken
    recently_played_json = urlopen(URL7())
    recently_played = json.loads(recently_played_json.read())
    totaltime = 0
    for x in recently_played['response']['games']:
        if 'playtime_2weeks' in x:
            game_per_2_weeks = x['playtime_2weeks']
            totaltime = game_per_2_weeks + totaltime
    uren = round(totaltime / 60)
    return uren


def friendlst():  # hoeveel games de user heeft.
    friend_json = urlopen(URL5())
    friend = json.loads(friend_json.read())
    friends = 0
    for x in friend['friendslist']['friends']:
        if x['relationship'] == 'friend':
            friends = friends + 1
    return friends


def playersumaries():  # verkrijgt de landcode van de user en steamname van de user op dat moment op steam
    lst = []
    playersumary_json = urlopen(URL6())
    playersumary = json.loads(playersumary_json.read())
    for x in playersumary['response']['players']:
        steam_player_name = x['personaname']
        land = x['loccountrycode']
        url = x['avatarfull']
        seconds = x['timecreated']
        date = time.gmtime(seconds)
    lst.append(steam_player_name)
    lst.append(land)
    lst.append(f'{date[2]}/{date[1]}/{date[0]}')
    return lst


def Tags(game_list):  # Tags van de gebruiker uitzoeken
    global tagsdict
    steam_json = open('FINAL MAP\steam.json', 'r')  # steam json lijst
    steam_list = json.loads(steam_json.read())
    genre = open('C:\Users\3abode\PycharmProjects\Programming\popular_genres.txt', 'r+')  # lijst met genre/tags
    appidlst = []
    tagsdict = {}
    y = 0
    genre_list = []
    for x in genre:  # in een genre pythonlijst zetten
        genre_list.append(x)
    genre_list.sort()
    genre.close()
    for genre in genre_list:  # lijst in een Dictionary zetten
        tagsdict[genre[:-1]] = y
    for gameid in game_list["response"]["games"]:  # app id lijst van de gebruiker opvragen
        appid = gameid["appid"]
        appidlst.append(appid)
        appidlst.sort()
    for id in appidlst:
        for value in steam_list:
            if id == value["appid"]:  # checken if id van appidlst gelijk is aan een appid
                for game in steam_list:
                    if id == game["appid"]:  # als de appid gelijk is
                        tag = game["steamspy_tags"]  # de steam tags pakken
                        tag_list = tag.split(";")  # tags opsplitsen
                        for tag in tag_list:
                            if tag in tagsdict:  # checken of tag in tagsdict staat
                                tagsdict[tag] = tagsdict[tag] + 1  # tag +1 value geven
                            else:
                                tagsdict[tag] = 1  # tag toevoegen aan dictionary en een waarde van 1 geven
                                genre_list.append(tag)  # tag toevoegen aan genre_list
                                with open('C:/Users/tomno/Documents/GitHub/steam/Tom/popular_genres.txt',
                                          'a') as add_genre:
                                    add_genre.write(f'\n{tag}')  # tag toevoegen aan alle bekende tags/genres
    tagslst = []
    for key, val in tagsdict.items():
        key = key.replace(" ", "_")  # spaties vervangen voor '_'
        if val >= 1:
            if val < 10:
                val = f'00{val}'  # als de waarde lager dan 10 is een 0 voor het cijfer toevoegen
                tagslst.append(f'{val};{key}')  # nieuwe waare toeveoegen in lijst
                tagslst.sort(reverse=True)
            elif val >= 10 and val < 100:
                val = f'0{val}'  # als de waarde lager dan 10 is een 0 voor het cijfer toevoegen
                tagslst.append(f'{val};{key}')  # nieuwe waare toeveoegen in lijst
                tagslst.sort(reverse=True)
            else:
                tagslst.append(f'{val};{key}')  # waarde toevoegen aan lijst
    tagslst.sort()  # lijst sorteren van groot naar klein
    return tagslst


def time_func(game_library):  # play time bepalen per game
    most_played = []
    time_list = []
    for game in game_library["response"]["games"]:
        if game["playtime_forever"] != 0:
            time_list.append(game["playtime_forever"])
            time_list.sort()
    for x in range(len(time_list) - 10, len(time_list)):  # Tijden met games samen voegen voor de lijst
        for game in game_library["response"]["games"]:
            name = game["name"]
            if time_list[x] == game["playtime_forever"]:
                if game["playtime_forever"] >= 60:
                    hours = (game["playtime_forever"] // 60)  # Minuten in uren zetten
                    minutes = (((game["playtime_forever"] // 60) - hours) * 60)  # Overige weer terug zetten in minuten
                    p_time = (game["playtime_forever"] / 60)
                    play_time = round(p_time, 2)
                    most_played.append(f'{name};{hours};{minutes};{play_time}')
                else:
                    most_played.append(f'{name};{game["playtime_forever"]}')
    return most_played


def userID(username):  # User info krijgen uit de steam API
    global steam_id
    if username.isdecimal():  # kan nu ook volledige steamid invullen (voor brendan enzo)
        steam_id = username
        return gen_data()
    else:
        URL = URL1(username)
        response1 = urlopen(URL)
        user_data = json.loads(response1.read())
        if user_data["response"]["success"] == 1:  # User opzoeken
            steam_id = user_data['response']['steamid']
            game_info()
        else:
            sg.popup_error('User does not exist')


def gen_data(game_library):  # Algemene Data zoals meest gespeelde games + tijden
    global gen_list
    time_list = []
    x = 0
    gen_list.clear()  # Herhaaldelijk inladen voorkomen
    try:
        for game in game_library["response"]["games"]:
            if game["playtime_forever"] != 0:
                time_list.append(game["playtime_forever"])
                time_list.sort()
        for x in range(len(time_list) - 5, len(time_list)):  # Tijden met games samen voegen voor de lijst
            for game in game_library["response"]["games"]:
                if time_list[x] == game["playtime_forever"]:
                    if game["playtime_forever"] >= 60:
                        hours = game["playtime_forever"] // 60  # Minuten in uren zetten
                        minutes = round(
                            ((game["playtime_forever"] / 60) - hours) * 60)  # Overige weer terug zetten in minuten
                        if minutes < 10:
                            minutes = f'0{minutes}'
                        play_time = f'{hours}:{minutes}'
                    else:
                        play_time = game["playtime_forever"]
                    gen_list.append(f'{game["name"]}, {play_time}')
        window.Element('_GENERAL_').Update(gen_list)
        Tags(game_library)
        return gen_list
    except KeyError:
        sg.popup_error("Game list not available\n(Maybe multiple users share that name?)")


def game_info():  # Alles games van de User verzamelen en in een lijst stoppen
    global game_name
    global game_library
    URL = URL2(steam_id)
    response5 = urlopen(URL)
    game_library = json.loads(response5.read())
    x = 0
    game_list.clear()
    for game in game_library["response"]["games"]:  # Lijst van alle games van de gebruiker
        game_list.append(game["name"])
        x += 1
    game_list.sort()
    window.Element('_LIST_').Update(game_list)


def achievements(appid, playtime):  # Behaalde achievement percentage van de aangeklikte game verzamalen
    global percentage
    URL1 = URL3(appid, steam_id)
    URL2 = URL4(appid)
    achieved = 0
    to_achieve = 0
    progress = 0
    game_data = []
    r = requests.get(URL1)
    response3 = r.status_code
    try:
        game_data.clear()
        if response3 == 200:  # Response code check (positief)
            window.Element('_DATA_').Update('')
            achievement_user = r.json()
            if achievement_user['playerstats']['achievements']:  # Achievements opzoeken van de gebruiker
                for x in achievement_user['playerstats']['achievements']:
                    achieved += 1
                response4 = requests.get(URL2)
                achievement_all = response4.json()
            for x in achievement_all['achievementpercentages'][
                'achievements']:  # Alle beschikbare Achievements opzoeken van het spel
                to_achieve += 1
                progress = achieved / to_achieve
                p = progress * 100
                percentage = f"behaald:     {round(p, 2)}%"
                game_data.clear()
                game_data.append(game_name)
                game_data.append(playtime)
                game_data.append(percentage)
                window.Element('_DATA_').Update(game_data)
                window.Element('_DATA_').Update(game_data)
            threading.Thread(target=sshpi.gamedisplay, args=(game_name[14:], uname, 1)).start()
            threading.Thread(target=sshpi.ledbalk, args=(int(progress * 100),)).start()
        if response3 == 400:  # Response code check (negatief)
            window.Element('_DATA_').Update('')
            NA = "Not Available"
            game_data.clear()
            game_data.append(game_name)
            game_data.append(playtime)
            game_data.append(NA)
            window.Element('_DATA_').Update(game_data)
            threading.Thread(target=sshpi.gamedisplay, args=(game_name[14:], uname, 0)).start()
    except KeyError:  # Als er geen Achievements zijn
        window.Element('_DATA_').Update('')
        NA = "Not Available"
        game_data.clear()
        game_data.append(game_name)
        game_data.append(playtime)
        game_data.append(NA)
        window.Element('_DATA_').Update(game_data)
        threading.Thread(target=sshpi.gamedisplay, args=(game_name[14:], uname, 0)).start()


def game_id(name):  # App ID met playtime opzoeken
    global game_name
    for game in game_library['response']['games']:
        if name == game['name']:
            spel = game['name']
            game_name = f'game:         {spel}'
            app_id = game["appid"]
            if game["playtime_forever"] >= 60:
                hours = game["playtime_forever"] // 60
                minutes = round(((game["playtime_forever"] / 60) - hours) * 60)
                if minutes < 10:
                    minutes = f'0{minutes}'
                playtime = f'playtime:     {hours}h:{minutes}m'
            else:
                playtime = f'playtime:     {game["playtime_forever"]}m'
            achievements(app_id, playtime)


# --------Grafieken Functies--------#
def graph_values(game_list):  # grafiek 1e tab
    time_list = []
    x = 0
    x_axis = ['']  # lst van de games
    y_axis = [0]  # lst van de uren
    play_stat = time_func(game_list)
    for x in play_stat:
        new_x = x.split(';')
        x_axis.append(new_x[0])
        y_axis.append(float(new_x[3]))
    plt.figure(figsize=(15, 7))  # maat van het figuur bepalen
    plt.tick_params(axis='y', which='major', labelsize=6)
    plt.xticks(rotation=90)
    plt.barh(x_axis, y_axis, label='Time')
    for i, v in enumerate(y_axis):
        if i > 0:  # als de waarde groter is dan 0 tekst toevoegen
            plt.text(v + 0.1, i + 0, str(f'  {str(round(int(v), 0))}'), color='black')
    plt.title("Mosted played games"), plt.xlabel("hours"), plt.ylabel("Games")  # labels voor de grafiek maken
    plt.ylim(ymin=0)
    plt.legend()
    fig = plt.gcf()  # een afbeelding maken van de grafiek
    return fig


def graph_genre(game_library):  # grafiek 2e tab
    x = 0
    x_axis = ['']  # lst van de games
    y_axis = [0]  # lst van de uren
    genre_list = Tags(game_library)
    for x in genre_list[-10:]:
        new_x = x.split(';')
        x_axis.append(new_x[1])
        y_axis.append(float(new_x[0]))
    plt.figure(figsize=(15, 7))  # maat van het figuur bepalen
    plt.tick_params(axis='y', which='major', labelsize=6)
    plt.xticks(rotation=90)
    plt.barh(x_axis, y_axis, label='Genre')
    for i, v in enumerate(y_axis):
        if i > 0:  # als de waarde groter is dan 0 tekst toevoegen
            plt.text(v + 0.1, i + 0, str(f'-{str(round(int(v), 0))}'), color='black')
    plt.title("Most Owned Genre"), plt.xlabel("Amount"), plt.ylabel("Genre")  # labels voor de grafiek maken
    plt.ylim(ymin=0)
    plt.legend()
    fig = plt.gcf()  # een afbeelding maken van de grafiek
    return fig


def graph_genre_time(game_list):  # grafiek 3e tab
    steam_json = open('FINAL MAP\steam.json', 'r')
    steam_list = json.loads(steam_json.read())
    genre = open('FINAL MAP\popular_genres.txt', 'r+')
    genre_dict = {}
    genre_dict.clear()
    time_list = []
    x_axis = ['']
    y_axis = [0]
    for x in genre:  # genre in dictionary zetten
        x = x[:-1]
        genre_dict[x] = 0
    for y in game_list["response"]["games"]:  # games zoeken
        game_y = y
        for x in steam_list:
            game_x = x
            if game_y['name'] == game_x['name']:  # tags van de game opzoeken
                if game_y['playtime_forever'] >= 1:
                    z = game_x['steamspy_tags']
                    z_split = z.split(';')
                    for i in z_split:
                        if i in genre_dict:
                            genre_dict[i] = genre_dict[i] + game_y['playtime_forever']  # tijd bij het genre optellen
    for x in genre_dict:
        if genre_dict[x] >= 1 and genre_dict[x] < 10:  # voorzorg voor sorteren
            time_list.append(f'0000000{genre_dict[x]}; {x}')
        elif genre_dict[x] >= 10 and genre_dict[x] < 100:
            time_list.append(f'000000{genre_dict[x]}; {x}')
        elif genre_dict[x] >= 100 and genre_dict[x] < 1000:
            time_list.append(f'00000{genre_dict[x]}; {x}')
        elif genre_dict[x] >= 1000 and genre_dict[x] < 10000:
            time_list.append(f'0000{genre_dict[x]}; {x}')
        elif genre_dict[x] >= 10000 and genre_dict[x] < 100000:
            time_list.append(f'000{genre_dict[x]}; {x}')
        elif genre_dict[x] >= 100000 and genre_dict[x] < 1000000:
            time_list.append(f'00{genre_dict[x]}; {x}')
        elif genre_dict[x] >= 1000000 and genre_dict[x] < 10000000:
            time_list.append(f'0{genre_dict[x]}; {x}')
        elif genre_dict[x] >= 10000000 and genre_dict[x] < 100000000:
            time_list.append(f'{genre_dict[x]}; {x}')
    time_list.sort(reverse=False)
    for x in time_list[-10:]:  # Top 10 eruit halen
        new_x = x.split(';')
        x_axis.append(new_x[1])
        new_new_x = int(new_x[0]) // 60
        y_axis.append(new_new_x)
    plt.figure(figsize=(15, 7))  # maat van het figuur bepalen
    plt.tick_params(axis='y', which='major', labelsize=6)
    plt.xticks(rotation=90)
    plt.barh(x_axis, y_axis, label='Time')
    for i, v in enumerate(y_axis):
        if i > 0:  # als de waarde groter is dan 0 tekst toevoegen
            plt.text(v + 0.1, i + 0, str(f'  {str(round(int(v), 0))}'), color='black')
    plt.title("Most played Genres"), plt.xlabel("hours"), plt.ylabel("Genre")  # labels voor de grafiek maken
    plt.ylim(ymin=0)
    plt.legend()
    fig = plt.gcf()  # een afbeelding maken van de grafiek
    return fig


def csgo():  # grafiek 5e tab
    lst_stats = ['']
    lst_values = [0]
    kd = []
    winrate = []
    dictdict = {}
    URL = URL3(730, steam_id)
    response_csgo_stats = urlopen(URL)
    csgo_stats = json.loads(response_csgo_stats.read())
    for stats in csgo_stats['playerstats']['stats']:
        stats_all = stats['name']
        values_all = stats['value']
        if stats_all == 'total_kills':
            kd.append(values_all)
        elif stats_all == 'total_deaths':
            kd.append(values_all)
        elif stats_all == 'total_kills_ak47':
            lst_stats.append(stats_all)
            lst_values.append(values_all)
        elif stats_all == 'total_kills_m4a1':
            lst_stats.append(stats_all)
            lst_values.append(values_all)
        elif stats_all == 'total_kills_awp':
            lst_stats.append(stats_all)
            lst_values.append(values_all)
        elif stats_all == 'total_matches_played':
            lst_stats.append(stats_all)
            lst_values.append(values_all)
            winrate.append(values_all)
        elif stats_all == 'total_matches_won':
            lst_stats.append(stats_all)
            lst_values.append(values_all)
            winrate.append(values_all)
    kd_ratio = round(100 * (kd[0] / kd[1]))
    winrate_ratio = round(100 * (winrate[0] / winrate[1]))
    lst_stats.append('Kill/Death Ratio in procent')
    lst_values.append(kd_ratio)
    lst_stats.append('Win/Loss Ratio in procent')
    lst_values.append(winrate_ratio)
    plt.figure(figsize=(15, 7))  # maat van het figuur bepalen
    plt.tick_params(axis='y', which='major', labelsize=6)
    plt.xticks(rotation=90)
    plt.barh(lst_stats, lst_values, label='Value')
    for i, v in enumerate(lst_values):
        if i > 0:  # als de waarde groter is dan 0 tekst toevoegen
            plt.text(v + 0.1, i + 0, str(f'  {str(round(int(v), 0))}'), color='black')
    plt.title("CS:GO stats"), plt.xlabel("Value"), plt.ylabel("Stats")
    plt.ylim(ymin=0)
    plt.legend()
    fig = plt.gcf()  # een afbeelding maken van de grafiek
    return fig


def draw(canvas, figure):  # van de grafiek een bruikbaar figuur maken
    canvas_fig = FigureCanvasTkAgg(figure, canvas)
    canvas_fig.draw()
    canvas_fig.get_tk_widget().pack(side='top', fill='both', expand=1)  # de grafiek tekenen
    return canvas_fig


# -------------------------------------------------value activaties-------------------------------------------------#

global uname

while True:
    event, values = window.Read()
    last_search = ""
    search_list = []
    if event is None or event == 'Exit':  # Afsluiten van het programma zonder Errors
        break
    if values['_USER_'].strip() != '' and ' ' not in values['_USER_'].strip():  # User opzoeken
        username = values['_USER_']
        uname = username
        game_data = userID(username)
        append()
    if values['_INPUT_'] != '':  # Live search in library
        search = values['_INPUT_']
        for i in game_list:
            if search in i:
                search_list.append(i)
        window.Element('_LIST_').update(search_list)
    if event == '_LIST_':  # Specifieke Game data in de GUI verwerken
        app_name = values['_LIST_']
        game_name = str(app_name[0])
        game_id(game_name)
        window.Element('_DATA_').Update(game_data)
    if event == '_SEARCH_':  # Grafieken in het scherm weergeven
        fig1 = graph_values(game_library)
        draw(window['_TIME_GRAPH_'].TKCanvas, fig1)
        fig2 = graph_genre(game_library)
        draw(window['_GEN_GRAPH_'].TKCanvas, fig2)
        fig3 = graph_genre_time(game_library)
        draw(window['_Time_GEN_'].TKCanvas, fig3)
        fig4 = csgo()
        draw(window['_CSGO_'].TKCanvas, fig4)
window.close()