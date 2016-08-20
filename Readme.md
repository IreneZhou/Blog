#Readme.md

（建议）为一个工程创建一个虚拟环境：

```
$ pip install virtualenv
$ cd my_project_folder
$ virtualenv venv
```

你可以选择使用一个Python解释器：

```
$ virtualenv -p /usr/bin/python3.5 venv
```

这将会使用 `/usr/bin/python3.5` 中的Python解释器。

要开始使用虚拟环境，其需要被激活：

```
$ source venv/bin/activate

```



安装包及运行工程：

````
$ pip install -r requirements.txt
$ python3 manage.py runserver
````

