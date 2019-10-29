# Movie_Arch_Tool - 电影自动归档脚本
![img](https://i.loli.net/2019/10/29/yBdmY5gUPlDzCnh.gif)

![img](https://i.loli.net/2019/10/09/CjrEZxpN3zRF18k.jpg)

## FEATURE
1. 搜索当前目录电影文件，在豆瓣中获取相应电影信息
2. 创建以 `${中文译名}-${电影原名}` 的文件夹自动归类
3. 下载对应电影封面
4. Windows 端自动修改文件夹图标为电影封面
5. 自动下载电影对应字幕

## INSTALL
需要安装 `requests`, `BeautifulSoup`, `Pillow`。

```
pip install requests bs4 pillow
```  

## HOW TO USE
将脚本与需处理的电影文件放置于同一目录下，运行脚本即可

字幕下载功能采用 [射手网(伪)](http://assrt.net/) API，需自行[注册](https://2.assrt.net/user/register.xml)获取 Token 填入脚本

## TODO
1. Mac 端自动修改文件夹图标为电影封面


## BUG
1. 搜索功能需优化，目前仅为直接提交文件名至豆瓣进行搜索，部分复杂文件名无法获取正确结果
2. 电影名中带冒号的文件会处理失败

## LINK
[WTX's Blog - 电影一键归档脚本](https://wtx.moe/archives/97/)