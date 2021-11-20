Standalone CLI programs for tools of https://texttoolkit.com :
- cdg.py: a compilation database generator for GNU make

And other text tools:
- merge-files.py: join every line from a few files as columns

# merge-files.py

For example, there are three files:
```
$ cat c1.txt
1
2
3

$ cat c2.txt
a
b

$ cat c3.txt
x
y
z
```

Join them like this: `python merge-files joined.txt , c0.txt c1.txt c2.txt`,
then `joined.txt` will have:
```
$ cat joined.txt
1,a,x
2,b,z
```
