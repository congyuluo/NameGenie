Welcome to the GenRefactor reproducible package. This package contains the programs used to generate the results in the
paper. Please make sure you have the following requirements, which was the environment which we performed tests in:
- Apple Silicon powered Mac computer running macOS 12.6
- Python 3.9
- The following python packages:
Package                 Version
----------------------- --------
annotated-types         0.7.0
anyio                   4.4.0
certifi                 2024.7.4
clipboard               0.0.4
distro                  1.9.0
exceptiongroup          1.2.2
h11                     0.14.0
httpcore                1.0.5
httpx                   0.27.0
idna                    3.7
MouseInfo               0.1.3
numpy                   2.0.0
openai                  1.35.13
pillow                  10.4.0
pip                     23.2.1
PyAutoGUI               0.9.54
pydantic                2.8.2
pydantic_core           2.20.1
PyGetWindow             0.0.9
Pygments                2.18.0
PyMsgBox                1.0.9
pyobjc-core             10.3.1
pyobjc-framework-Cocoa  10.3.1
pyobjc-framework-Quartz 10.3.1
pyperclip               1.9.0
PyRect                  0.2.0
PyScreeze               0.1.30
pytweening              1.2.0
rubicon-objc            0.4.9
setuptools              68.2.0
six                     1.16.0
sniffio                 1.3.1
tqdm                    4.66.4
typing_extensions       4.12.2
wheel                   0.41.2
- Enable the accessibility settings when prompted to
- JetBrains InteliJ IDEA Ultimate 2024.1

Do the following configurations in common.py:

After all of the prerequisites are met, run the following color calibrations on your monitor using OSX's digital color
meter, and fill it in the file. This is because GenRefactor interacts with InteliJ's renaming functionalities through
GUI. Make sure to test the colors of the following elements on your InteliJ IDE, otherwise it will not work:

- (color_1):
Click on a refactorable variable in the IDE, and press Shift + F6 to rename it. The blue window shall show up, at
this time, use the color meter to measure the background color of the blue window. Fill in the color in the file. You
should get something like (33, 66, 131), do not use my value, as it will not work for different monitors.

- (color_2):
Create an error in the code, and hover over the error. The red window shall show up, at this time, use the color meter
to measure the background color of the red window. Fill in the color in the file. You should get something like
(148, 37, 35).

- (color_3):
Click on an unrefactorable name in the code, and press Shift + F6 to rename it. The red window should pop-up, use
the color meter to find the background color of the window. Expect something like (109, 23, 44).

- (color_4):
Click on a function name with testing usage, and press Shift + F6 to rename it. Enter a new name, and hit enter. The
selection window should pop-up, use the color meter to find the blue color of the window. Expect something like
(47, 101, 202).

- (color_5):
Refactor an identifier name using the rename function, and press Command + Z to undo the change. The undo window should
show up. Use the color meter to find the color of the button. Expect something like (54, 88, 128)

Open a project using IntelliJ, and wait for the IDE to finish indexing. Make sure there are no existing errors in the
code as indicated by IntelliJ.

Place IntelliJ window on your display #1 (if you have multiple displays). Scale the window below 350*350 pixels. Put it
in the top left corner of the screen. Place terminal window, or IDE window for GenRefactor on the right side.

- Configure your own openai API key in the file. (API_KEY)
- Configure the root directory you would like to refactor in the file. (refactoring_directory)
- Select the sampling ratio you would like to use in the file. (1 means all, 2 means half, 3 means one third, etc.)
(sampling_ratio)
- Use the pre_test.py to test the parsing and sampling ratio of the code.

Run GenRefactor with running main.py (Please use the included SampleProject to test the tool).

During running the tool, if the tool encounters problems, adjust the parameters in the code accordingly. The tool is to
automatically stop if there is a problem. If the tool stops, manually fix the problem in the IDE, and continue to run by
entering something in the terminal window, which GenRefactor takes over again.

After running, GenRefactor shall exit with zero exit code. "logs" directory should be generated, and log.txt contains
the resulting refactorings.

We apologize as the current version of the tool is extremely difficult to operate, and we are working on adapting this
tool to work through interfaces other than GUI.

Here is a list of all 20 open-source projects we used in our study:
1brc
https://github.com/gunnarmorling/1brc
The One Billion Row Challenge -- A fun exploration of how quickly 1B rows from a text file can be aggregated with Java
Chat2DB
https://github.com/CodePhiliaX/Chat2DB
AI-driven database tool and SQL client, The hottest GUI client, supporting MySQL, Oracle, PostgreSQL, DB2, SQL Server, DB2, SQLite, H2, ClickHouse, and more.
FoldCraftLauncher
https://github.com/FCL-Team/FoldCraftLauncher
Fold Craft Launcher, an Android Minecraft : Java Edition launcher.
TheAlgorithms - Java
https://github.com/TheAlgorithms/Java
Juggle
https://github.com/somta/Juggle
一款适用于微服务编排，第三方api集成，私有化定制开发，编写BFF聚合层等场景的强大低码编排工具！
NewPipeExtractor
https://github.com/TeamNewPipe/NewPipeExtractor
NewPipe's core library for extracting data from streaming sites
Paper
https://github.com/PaperMC/Paper
The most widely used, high performance Minecraft server that aims to fix gameplay and mechanics inconsistencies
Stirling-PDF
https://github.com/Stirling-Tools/Stirling-PDF
#1 Locally hosted web application that allows you to perform various operations on PDF files
alist-tvbox
https://github.com/power721/alist-tvbox
AList proxy server for TvBox, support playlist and search.
disruptor
https://github.com/LMAX-Exchange/disruptor
High Performance Inter-Thread Messaging Library
flink-cdc
https://github.com/apache/flink-cdc
Flink CDC is a streaming data integration tool
flowable-engine
https://github.com/flowable/flowable-engine
A compact and highly efficient workflow and Business Process Management (BPM) platform for developers, system admins and business users.
lawnchair
https://github.com/LawnchairLauncher/lawnchair.git
Lawnchair is a free, open-source home app for Android. Taking Launcher3 — Android’s default home app — as a starting point, it ports Pixel Launcher features and introduces rich options for customization.
openapi-generator
https://github.com/OpenAPITools/openapi-generator
OpenAPI Generator allows generation of API client libraries (SDK generation), server stubs, documentation and configuration automatically given an OpenAPI Spec (v2, v3)
Termux-app
https://github.com/termux/termux-app
Termux - a terminal emulator application for Android OS extendible by variety of packages.
Arclight
https://github.com/IzzelAliz/Arclight
A Bukkit(1.19/1.20) server implementation in modding environment using Mixin. ⚡
GrimAC
https://github.com/GrimAnticheat/Grim
Fully async, multithreaded, predictive, open source, 3.01 reach, 1.005 timer, 0.01% speed, 99.99% antikb, "bypassable" 1.8-1.20 anticheat.
Shedlock-master
https://github.com/lukas-krecan/ShedLock.git
Distributed lock for your scheduled tasks
DJL
https://github.com/deepjavalibrary/djl
An Engine-Agnostic Deep Learning Framework in Java
Iced-latte
https://github.com/Sunagatov/Iced-Latte
a online Marketplace for coffee retail (Backend)
