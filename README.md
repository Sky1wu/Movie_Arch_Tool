# Movie_Arch_Tool - 电影自动归档脚本

![img](https://i.loli.net/2019/10/29/yBdmY5gUPlDzCnh.gif)

![img](https://i.loli.net/2019/10/09/CjrEZxpN3zRF18k.jpg)

## FEATURE

1. 搜索当前目录电影文件，在 TMDb 中获取相应电影信息
2. 创建以 `${中文译名} ${电影原名}` 的文件夹自动归类
3. 下载对应电影封面
4. Windows 端自动修改文件夹图标为电影封面
5. 自动下载电影对应字幕

## INSTALL

需要安装 `requests`, `Pillow`。

### windows

```shell
pip install requests pillow
```  

### macOS

macOS 的 Python2 自带 PyObjC，Python3 需要自行安装。

```shell
pip install requests pillow pyobjc
```  

## HOW TO USE

在 [The Movie Database (TMDb)](https://www.themoviedb.org/) 注册并申请 API，打开脚本在自定义区域的 `TMDb_API_Key` 中填入 `API Key (v3 auth)`。

将脚本与需处理的电影文件放置于同一目录下，运行脚本即可。

请在 Python3 环境下运行。

~~字幕下载功能采用 [射手网(伪)](http://assrt.net/) API，需自行[注册](https://2.assrt.net/user/register.xml)获取 Token 填入脚本~~

字幕下载功能已移除

## TODO

1. 已归入文件夹但无封面的电影自动补全封面。

## LINK

[WTX's Blog - 电影一键归档脚本](https://wtx.moe/archives/97/)
