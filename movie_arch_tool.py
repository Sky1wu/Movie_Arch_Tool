import os
import requests
import sys
import shutil
from bs4 import BeautifulSoup
import platform
from urllib.parse import unquote

if platform.system() == 'Windows':
    import ctypes
    from PIL import Image
    import win32api
    import win32con
    from ctypes import POINTER, Structure, c_wchar, c_int, sizeof, byref
    from ctypes.wintypes import BYTE, WORD, DWORD, LPWSTR, LPSTR

# 自定义区域
ext_list = [".mkv", ".mp4"]  # 脚本扫描的文件，可自行添加
assrt_token = ''  # 射手网(伪) 的 API，用于下载字幕，可留空

os.chdir(sys.path[0])
dirs = os.listdir('.')

for file_name in dirs:
    if os.path.splitext(file_name)[1].lower() in ext_list:
        movie_name = os.path.splitext(file_name)[0]
        while True:
            url = 'https://movie.douban.com/j/subject_suggest?q=' + movie_name
            response = requests.get(url).json()
            if len(response):
                break
            else:
                print(file_name)
                movie_name = input('以上文件匹配失败，请手动输入电影名称：')

        print(movie_name + ' 信息匹配成功')
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

        if movie_title == sub_title:
            path = sys.path[0]+'/'+movie_title + '/'
        else:
            path = sys.path[0]+'/'+movie_title+'-'+sub_title+'/'

        if not os.path.exists(path):
            os.mkdir(path)

        shutil.move(file_name, path)
        img_path = path + movie_title+'.jpg'
        with open(img_path, 'wb') as file:
            file.write(pic_add.content)
        file.close()
        print(movie_name+' 封面下载完成')

        # 字幕下载
        if assrt_token is not '' and movie_title != sub_title:
            assrt_search_url = 'http://api.assrt.net/v1/sub/search?token='
            url = assrt_search_url+assrt_token+'&q='+movie_title+' '+sub_title
            response = requests.get(url).json()

            for each_sub in response['sub']['subs']:
                if('双语' in each_sub['lang']['desc'] or '简' in each_sub['lang']['desc']):
                    if(each_sub['subtype'] == '其他'):
                        continue
                    sub_id = each_sub['id']
                    break

            assert_url = 'http://api.assrt.net/v1/sub/detail?token='
            url = assert_url+assrt_token+'&id='+str(sub_id)
            response = requests.get(url).json()
            sub_url = response['sub']['subs'][0]['filelist'][0]['url']
            sub_file = requests.get(sub_url)
            sub_url = str(sub_url)
            sub_file_name = unquote(os.path.basename(
                sub_url[: sub_url.index('?_=')]))
            sub_path = path+sub_file_name

            with open(sub_path, 'wb') as file:
                file.write(sub_file.content)
            file.close()
            print(movie_name+' 字幕下载完成')

        # 修改 Windows 文件夹图标
        if platform.system() == 'Windows':
            img = Image.open(img_path)
            x, y = img.size
            x = int(256/y*x)

            img = img.resize((x, 256), Image.ANTIALIAS)
            img_new = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
            img_new.paste(img, (int((256 - x) / 2), 0))
            img_new.save(path+'favicon.ico', "ico", quality=100)

            folderpath = path
            iconpath = 'favicon.ico'

            '''
            此处修改文件夹图标的方法来自于 https://stackoverflow.com/questions/4662759/how-to-change-folder-icons-with-python-on-windows
            '''
            HICON = c_int
            LPTSTR = LPWSTR
            TCHAR = c_wchar
            MAX_PATH = 260
            FCSM_ICONFILE = 0x00000010
            FCS_FORCEWRITE = 0x00000002
            SHGFI_ICONLOCATION = 0x000001000

            class GUID(Structure):
                _fields_ = [
                    ('Data1', DWORD),
                    ('Data2', WORD),
                    ('Data3', WORD),
                    ('Data4', BYTE * 8)]

            class SHFOLDERCUSTOMSETTINGS(Structure):
                _fields_ = [
                    ('dwSize', DWORD),
                    ('dwMask', DWORD),
                    ('pvid', POINTER(GUID)),
                    ('pszWebViewTemplate', LPTSTR),
                    ('cchWebViewTemplate', DWORD),
                    ('pszWebViewTemplateVersion', LPTSTR),
                    ('pszInfoTip', LPTSTR),
                    ('cchInfoTip', DWORD),
                    ('pclsid', POINTER(GUID)),
                    ('dwFlags', DWORD),
                    ('pszIconFile', LPTSTR),
                    ('cchIconFile', DWORD),
                    ('iIconIndex', c_int),
                    ('pszLogo', LPTSTR),
                    ('cchLogo', DWORD)]

            shell32 = ctypes.windll.shell32

            fcs = SHFOLDERCUSTOMSETTINGS()
            fcs.dwSize = sizeof(fcs)
            fcs.dwMask = FCSM_ICONFILE
            fcs.pszIconFile = iconpath
            fcs.cchIconFile = 0

            shell32.SHGetSetFolderCustomSettings(
                byref(fcs), folderpath, FCS_FORCEWRITE)

            win32api.SetFileAttributes(
                path+'favicon.ico', win32con.FILE_ATTRIBUTE_HIDDEN)
            os.remove(img_path)
            print(movie_name+' 封面修改完成')
