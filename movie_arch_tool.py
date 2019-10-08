import os
import requests
import sys
import shutil
from bs4 import BeautifulSoup

os.chdir(sys.path[0])
dirs = os.listdir('.')
ext_list = [".mkv", ".mp4"]
for file_name in dirs:
    if os.path.splitext(file_name)[1].lower() in ext_list:
        url = 'https://movie.douban.com/j/subject_suggest?q='+file_name
        response = requests.get(url).json()
        movie_id = response[0]['id']
        movie_title = response[0]['title']
        sub_title = response[0]['sub_title']
        url = 'https://movie.douban.com/subject/'+movie_id+'/photos?type=R'
        response = requests.get(url)

        soup = BeautifulSoup(response.content.decode('utf-8'), 'lxml')
        all_picture = soup.find('ul', class_="poster-col3 clearfix")
        all_img_tag = all_picture.find_all('img')
        picture = all_img_tag[0]['src']
        pic_add = requests.get(picture)

        path = sys.path[0]+'/'+movie_title+'-'+sub_title+'/'
        if not os.path.exists(path):
            os.mkdir(path)
        shutil.move(file_name, path)
        path += movie_title
        with open(path+'.jpg', 'wb') as file:
            file.write(pic_add.content)
        file.close()
