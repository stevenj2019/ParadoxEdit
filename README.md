# ParadoxEdit
x-Edit Styled utility, packaged with scripts to modify certiain paradox objects/files en masse.

### **Fair Warning, this is currently non-stable, i STRONGLY suggest to keep safe_mode active. this generates .bak files.**

## Current Functionality
General Functionality, adding blocks, arguments, and editing values are supplied (though useless to most modders)
alongside scripts i have pre-written including:
* Removing Comments, and whitespace
* Bulk insert of GFX Assets (including Focus option)
* Fix missing _shines (TODO)
* inject logs into events (TODO)
* sorting files (TODO)
to access the scripts, you right click the left view, over the file/cateogry you wish to apply them too, 
regardless of how you choose to interface with your files, you will get visual hints of modiciation (green=added, yellow=modifies red=marked for deletion) which will vanish when you save, 
This is far from complete. but the functionality exists to replace the old, and janky GFX Tool, 

Feel free to open issues for any problems(use bug tag) or for feature requests(use enhancement tag) there is currently no logging, next version will have this + remaining script conversion from the [gist](https://gist.github.com/stevenj2019/04b322de5374b9f0cec8dadfd2eb7c6d)

## Want to copy/contribute

I would significantly prefer to see a contribution, This is ultimately a community tool i personally will rarely use (i prefer the "SDK" myself), this was ONLY made because whenever i write a script i typically get a sigh in response, or a tonne of questions, ultimately here for fun, so do as you will, if you wish to fork, it is **not permitted** to profit from my code. again, community tool, it should be freely available to the community, people do not make money doing mods. they should not pay for the tooling.

## Dont trust the builds?
Healthy Skepticism, i can respect that, this is mostly for those who are not equipped to handle, and do not wish to learn or setup python, 
you have options:
From more python, to less in order
### ParadoxParser "SDK"
#### requires
- Python(3.12) Setup
- Python coding knowledge

[github](https://github.com/stevenj2019/ParadoxParser)
This is what inspired me to do this, it is a Parser that serialises Paradox files into Python Objects for easier/more reliable and scalable modifications, for many use cases, even this is a little overkill, but have at it, there is a [gist](https://gist.github.com/stevenj2019/04b322de5374b9f0cec8dadfd2eb7c6d) with some examples of how to use it

### Pre-coded Scripts
#### requires
- Python(3.12) Setup

the same [gist](https://gist.github.com/stevenj2019/04b322de5374b9f0cec8dadfd2eb7c6d) has a few helpful scripts in them, now i am doing this, i will not be adding to this list however, (there are some pretty heavy changes needed to convert them to be used in the app itself), but by all means, have away at it 

### run the .py directly 
#### requires
- Python(3.12) Setup

you can just run this as i do while i code, via the python file directly, 
Setup:
```
pip install -r requirements.txt
python src/PDXEdit.py
```
### Build it yourself
#### requires
- Python(3.12)
you can also build it yourself, if you like the idea, but dont trust me to do it (i am a little hurt but sure lol)
```
pip install -r requirements.txt
pip install pyinstaller
pyinstaller PDXEdit.spec
```
this will generate the relevant binary into your dist/ folder
