import re
import requests
import os
import sys
import shutil
import platform

if platform.system() == 'Windows':
    import ctypes
    from PIL import Image
    import win32api
    import win32con
    from ctypes import POINTER, Structure, c_wchar, c_int, sizeof, byref
    from ctypes.wintypes import BYTE, WORD, DWORD, LPWSTR, LPSTR


# 自定义区域
TMDb_API_Key = ''  # TMDb 的 API Key
ext_list = [".mkv", ".mp4"]  # 脚本扫描的文件扩展名
# 自定义区域结束

TMDb_API_URL = 'https://api.themoviedb.org/3'


def getMetadata(fileName):
    '''
    Get metadata from file name.
    '''
    print('获取元数据...')
    res = re.sub(r'\[.*?\]|\(.*?\)', '', fileName)  # 删除 [] 内容
    res = re.sub(r'[^\x00-\x7f]', '', res)  # 删除中文
    year = False
    if re.search(r"\d{4}\.", res):
        year = re.findall(r"\d{4}\.", res)[-1][:-1]  # 获取年份
        res = res[:res.rfind(re.findall(r"\d{4}\.", res)[-1])]  # 删除年份后内容
    res = res.replace('.', ' ')  # 删除 . 符号
    res = ' '.join(res.split())  # 删除多余空格
    if res:
        return res, year
    else:
        return False


def SearchonTMDb(title, year):
    '''
    Get movie id from TMDb.
    '''
    print('搜索电影信息...')
    TMDbSearchURL = TMDb_API_URL+'/search/movie'

    TMDbSearchData = {
        'api_key': TMDb_API_Key,
        'query': title,
        'year': year
    }

    TMDbSearchRes = requests.get(
        url=TMDbSearchURL, params=TMDbSearchData).json()

    if TMDbSearchRes['total_results']:
        TMDbMovieID = TMDbSearchRes['results'][0]['id']
        return str(TMDbMovieID)
    else:
        return False


def DetailsonTMDb(TMDbMovieID):
    '''
    Get the primary information about a movie from TMDb via movie id.
    '''

    TMDbDetailsURL = TMDb_API_URL+'/movie/'+TMDbMovieID

    TMDbDetailsData = {
        'api_key': TMDb_API_Key,
        'language': 'zh-CN'
    }

    TMDbDetailsRes = requests.get(
        url=TMDbDetailsURL, params=TMDbDetailsData).json()

    title_zh_CN = TMDbDetailsRes['title'].replace(': ', '：')
    original_title = TMDbDetailsRes['original_title'].replace(': ', '：')
    poster_path = TMDbDetailsRes['poster_path']

    return title_zh_CN, original_title, poster_path


def getPosterImage(poster_path):
    '''
    Get poster image from TMDb.
    '''
    print('下载电影封面...')
    TMDbImageBaseURL = 'https://image.tmdb.org/t/p/w300'

    posterURL = TMDbImageBaseURL+poster_path

    posterImage = requests.get(posterURL)

    return posterImage.content


def changeFloderIconWin(folderPath, posterLocalPath):
    img = Image.open(posterLocalPath)
    x, y = img.size
    x = int(256/y*x)

    img = img.resize((x, 256), Image.ANTIALIAS)
    img_new = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    img_new.paste(img, (int((256 - x) / 2), 0))
    img_new.save(folderPath+'favicon.ico', "ico", quality=100)
    iconPath = 'favicon.ico'

    '''
    此处修改文件夹图标的方法来自于 https://stackoverflow.com/questions/4662759/how-to-change-folder-icons-with-python-on-windows
    '''
    # HICON = c_int
    LPTSTR = LPWSTR
    # TCHAR = c_wchar
    # MAX_PATH = 260
    FCSM_ICONFILE = 0x00000010
    FCS_FORCEWRITE = 0x00000002
    # SHGFI_ICONLOCATION = 0x000001000

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
    fcs.pszIconFile = iconPath
    fcs.cchIconFile = 0

    shell32.SHGetSetFolderCustomSettings(
        byref(fcs), folderPath, FCS_FORCEWRITE)

    win32api.SetFileAttributes(
        folderPath+'favicon.ico', win32con.FILE_ATTRIBUTE_HIDDEN)
    os.remove(posterLocalPath)


if __name__ == "__main__":
    os.chdir(sys.path[0])
    dirs = os.listdir('.')

    for originalFileName in dirs:
        skipFlag = False

        if os.path.splitext(originalFileName)[1].lower() in ext_list:
            print('当前文件：'+originalFileName)
            fileNameWithoutExt = os.path.splitext(originalFileName)[0]
            titleFromFile, year = getMetadata(fileNameWithoutExt)

            while True:
                if titleFromFile:
                    TMDbMovieID = SearchonTMDb(titleFromFile, year)
                    if TMDbMovieID:
                        break
                    else:
                        titleFromFile = input(
                            originalFileName+' 无搜索结果，请手动输入电影名（直接回车跳过该文件）：')
                else:
                    titleFromFile = input(
                        originalFileName+' 元数据获取失败，请手动输入电影名（直接回车跳过该文件）：')

                if titleFromFile:
                    continue
                else:
                    skipFlag = True
                    break

            if skipFlag:
                continue

            title_zh_CN, original_title, poster_path = DetailsonTMDb(
                TMDbMovieID)

            if title_zh_CN == original_title:
                folderPath = sys.path[0]+'/'+original_title+'/'
            else:
                folderPath = sys.path[0]+'/'+title_zh_CN+' '+original_title+'/'

            if not os.path.exists(folderPath):
                os.mkdir(folderPath)

            shutil.move(originalFileName, folderPath)
            posterLocalPath = folderPath+title_zh_CN+'.jpg'

            posterImage = getPosterImage(poster_path)

            file = open(posterLocalPath, 'wb')
            file.write(posterImage)
            file.close()

            if platform.system() == 'Windows':
                changeFloderIconWin(folderPath, posterLocalPath)
