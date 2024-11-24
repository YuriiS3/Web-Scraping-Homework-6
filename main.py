import requests
from bs4 import BeautifulSoup
import json
import sqlite3

def parse_page(url: str) -> dict:
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    r = requests.get(url, headers={'user-agent': user_agent})

    data = []

    if not r.ok:
        # logging.error()
        return {'Link': url, 'Topics': data}

    soup = BeautifulSoup(r.text, 'lxml')

    try:
        Related_Topics_all = soup.find('ul', class_='ssrcss-1ujonwb-ClusterItems e1ihwmse0').find_all('li')

        for Related_Topics in Related_Topics_all:
            RT = Related_Topics.find('a').text

            data.append(RT)
    except:
        # logging.error()
        data = None

    return {'Link': url, 'Topics': data}



def write_sql(data: list) -> None:
    filename = 'Articles.db'

    # 1. create table
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()

    sql = """
        create table if not exists Articles (
            id integer primary key,
            [Link] text,
            [Topics] text
        )
    """
    cursor.execute(sql)

    sql = """
        delete from Articles
    """
    cursor.execute(sql)

    # 2. insert data
    for item in data:
        cursor.execute("""
            insert into Articles ([Link], [Topics])
            values (?, ?)
        """, (item['Link'], str(item['Topics'])))

    conn.commit()
    conn.close()



def read_sql() -> None:
    filename = 'Articles.db'

    connection = sqlite3.connect(filename)
    cursor = connection.cursor()

    # 1. get names of people
    sql = """
        select *
        from Articles
    """
    rows = cursor.execute(sql).fetchall()
    print(rows)

    connection.close()



def parse_html():
    url = 'https://www.bbc.com/sport'

    # response = requests.get(url)
    # with open('sport.html', 'w', encoding="utf-8") as f:
    #     f.write(response.text)

    with open('sport.html', 'r', encoding="utf-8") as f:
        text = f.read()

    soup = BeautifulSoup(text, 'lxml')

    urls = []

    articles_path = soup.find('ul', class_='ssrcss-1xxqo5f-Grid e12imr580')
    articles_all = articles_path.find_all('div', {'class': 'ssrcss-1f3bvyz-Stack e1y4nx260'})

    i = 0
    for article in articles_all:
        url = article.find('a').get('href')
        url = 'https://www.bbc.com' + url
        urls.append(url)

        i = i+1
        if i == 5:
            break

    result = []
    for url in urls:
        # print(url)
        result.append(parse_page(url))

    with open('urls.json', 'w') as f:
        json.dump(result, f, indent=4)

    write_sql(result)
    read_sql()

if __name__ == '__main__':
    parse_html()
