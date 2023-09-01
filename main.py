from selenium import webdriver
import csv
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
import random


# отдельно для каждого сайта выделим название, оценку, год, страну и жанр фильмов из html тегов
def get_rows_kinopoisk(names, score, country, year, genre):
    names = [x.contents[0] for x in names]
    score = [x.contents[0] for x in score]
    country = [x.contents[0] for i, x in enumerate(country) if not i % 2]
    year = [x.contents[0][-4:] for x in year]
    genre = [x.contents[0] for i, x in enumerate(genre) if i % 2]
    return {"name": names, "score": score, "country": country, "year": year, "genre": genre}


def get_rows_imdb(names, score, country, year, genre):
    names = [x.contents[3].text for x in names]
    score = [x.contents[3].text for x in score]
    year = [x.contents[0][1:5] for x in year]
    genre = [re.findall(r'(\w+, \w+)', x.text) for x in genre]
    for x in range(len(names)):
        country.append('')
    return {"name": names, "score": score, "country": country, "year": year, "genre": genre}


def get_rows_metacritic(names, score, country, year, genre):
    names = [x[0].contents[1].text for x in names]
    score = [x[0].contents[0] if x != [] else 'tdb' for x in score]
    year = [x[0].text[-5:-1] for x in year]
    country = [x[0].contents[3].text[1:-1]if x != [] else '-' for x in country]
    genre = [re.sub('  ', '', x[0].contents[3].text)[1:] for x in genre]
    return {"name": names, "score": score, "country": country, "year": year, "genre": genre}


def get_rows_rottentomatoes(names, score, country, year, genre):
    names = [x[0].contents[0] for x in names]
    year = [x[0].text[:4] for x in year]
    genre = [re.sub('\n', '', re.sub(' ', '', x[0].contents[0])) for x in genre]
    return {"name": names, "score": score, "country": country, "year": year, "genre": genre}


# запишем все сайты, с которых берем информацию, начальную страницу (т.к. на сайте метакритик нумерация начинается с
# нуля) и конечную
sites = ['https://www.kinopoisk.ru/lists/top500/?page={}&tab=all',
         'https://www.imdb.com/list/ls062911411/?page={}',
         'https://www.metacritic.com/browse/movies/score/metascore/all/filtered?view=detailed&page={}',
         'https://www.rottentomatoes.com/top/bestofrt/?page={}']
pages = [(1, 10), (1, 6), (0, 5), (1, 1)]
# в словарь запишем для каждого сайта теги для поиска нужной информации
scarper = {
    'kinopoisk': {'names': ('p', {"class": "selection-film-item-meta__name"}),
                  'score': ('span', {"class": "rating__value rating__value_positive"}),
                  'year': ('p', {"class": "selection-film-item-meta__original-name"}),
                  'country': ('span', {"class": "selection-film-item-meta__meta-additional-item"}),
                  'genre': ('span', {"class": "selection-film-item-meta__meta-additional-item"})},
    'imdb': {'names': ('h3', {"class": "lister-item-header"}),
             'score': ('div', {"class": "ipl-rating-star small"}),
             'year': ('span', {"class": "lister-item-year text-muted unbold"}),
             'country': ('---', {"---": "---"}),
             'genre': ('span', {"class": "genre"})},
    'metacritic': {'names': ('div', {"class": "product_page_title oswald upper"}),
                   'score': ('span', {"class": "metascore_w user larger movie positive"}),
                   'year': ('span', {"class": "release_date"}),
                   'country': ('tr', {"class": "countries"}),
                   'genre': ('tr', {"class": "genres"}),
                   'movie': ('a', {"class": "title"})},
    'rottentomatoes': {'names': ('h1', {"class": "scoreboard__title"}),
                       'year': ('p', {"class": "scoreboard__info"}),
                       'country': ('---', {"---": "---"}),
                       'genre': ('div', {"class": "meta-value genre"}),
                       'movie': ('a', {"class": "unstyled articleLink"})}
}

# пройдем по каждому сайту
for i in range(0, 4):
    # определяем название сайта с помощью регулярки
    site = re.findall(r'www.([A-Za-z]+).', sites[i])[0]
    # создаем файл csv для этого сайта и задаем названия столбцов
    with open(site + ".csv", 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["name", "score", "country", "year", "genre"])

    # проходим по всем страницам на этом сайте
    for page in range(pages[i][0], pages[i][1] + 1):
        # открываем страницу с текущим номером, записываем информацию с этой страницы
        url = sites[i].format(page)
        print(url)
        chrome_options = webdriver.chrome.options.Options()
        chrome_options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(executable_path="C:\\Users\olgab\PycharmProjects\sel_scarp\chromedriver.exe", chrome_options=chrome_options)
        driver.get(url)
        time.sleep(random.randint(16, 21))
        result = driver.page_source
        value = BeautifulSoup(result, features="lxml")

        # на кинопоиске и imdb вся необходимая информация находится на страницах с общим списком фильмов,
        # поэтому можно стразу взять ее, используя словарь тегов
        if site == 'kinopoisk' or site == 'imdb':
            names = value.find_all(scarper[site]['names'][0], scarper[site]['names'][1])
            scores = value.find_all(scarper[site]['score'][0], scarper[site]['score'][1])
            years = value.find_all(scarper[site]['year'][0], scarper[site]['year'][1])
            countries = value.find_all(scarper[site]['country'][0], scarper[site]['country'][1])
            genres = value.find_all(scarper[site]['genre'][0], scarper[site]['genre'][1])

        # на metacritic и rottentomatoes информацию нужно брать с самих страниц фильма
        # создаем список всех фильмов с главной страницы
        elif site == 'metacritic':
            movies = value.find_all(scarper[site]['movie'][0], scarper[site]['movie'][1])
            movies = ['https://www.' + site + '.com' + x.get('href') + '/details' for x in movies]
        else:
            movies = value.find_all(scarper[site]['movie'][0], scarper[site]['movie'][1])
            movies = ['https://www.' + site + '.com' + x.get('href') for x in movies][40:140]

        # создаем списки под информацию о фильмах
        if site == 'metacritic' or site == 'rottentomatoes':
            names = []
            scores = []
            years = []
            countries = []
            genres = []

            # проходим по всем фильмам со страницы, сохраняем информацию и находим нужную по тегам из словаря
            for movie in movies:
                print(movie)
                chrome_options.add_argument('--headless')
                driver = webdriver.Chrome(executable_path="C:\\Users\olgab\PycharmProjects\sel_scarp\chromedriver.exe",
                                          chrome_options=chrome_options)
                driver.get(movie)
                result = driver.page_source
                value = BeautifulSoup(result, features="lxml")
                name = value.find_all(scarper[site]['names'][0], scarper[site]['names'][1])
                year = value.find_all(scarper[site]['year'][0], scarper[site]['year'][1])
                country = value.find_all(scarper[site]['country'][0], scarper[site]['country'][1])
                genre = value.find_all(scarper[site]['genre'][0], scarper[site]['genre'][1])

                # на сайте rottentomatoes оценка фильма находится в shadow root, поэтому ее нельзя увидеть через bs 4
                # используем execute_script в selenium и сразу преобразовываем оценку вида '13%' в '1.3'
                if site == 'metacritic':
                    score = value.find_all(scarper[site]['score'][0], scarper[site]['score'][1])
                else:
                    score = int(driver.execute_script('return document.querySelector('
                                                      '"score-board").shadowRoot.querySelector('
                                                      '"score-icon-audience").shadowRoot.querySelector("div.wrap '
                                                      'span.percentage")').text[:-1]) / 10
                # добавляем информацию о текущем фильме в общий список фильмов с этой страницы если фильм считался
                # (потому что на метакритике проблема с загрузкой некоторых страниц)
                if name:
                    names.append(name)
                    scores.append(score)
                    years.append(year)
                    countries.append(country)
                    genres.append(genre)

        # в зависимости от сайта применяем разные функции для очистки данных от html тегов
        if site == 'imdb':
            rows = get_rows_imdb(names, scores, countries, years, genres)
        elif site == 'kinopoisk':
            rows = get_rows_kinopoisk(names, scores, countries, years, genres)
        elif site == 'metacritic':
            rows = get_rows_metacritic(names, scores, countries, years, genres)
        elif site == 'rottentomatoes':
            rows = get_rows_rottentomatoes(names, scores, countries, years, genres)

        # добавляем очищенную информацию в csv-файл и закрываем браузер
        df = pd.DataFrame(rows, columns=["name", "score", "country", "year", "genre"])
        df.to_csv(site + ".csv", mode='a', index=False, header=False,
                  columns=["name", "score", "country", "year", "genre"])

        driver.close()
