@echo off
setlocal enabledelayedexpansion

echo Copying CoreNLP jars...
cd stanford-corenlp-full*

rem
rem This will stop working if the version number is 
rem more than one digit.
rem Need a Windows shell programmer to fix this.
rem
rem Also, the original script set up symlinks, but
rem that requires permission changes on Windows, so
rem files are just being copied.
rem
for %%a in (stanford-corenlp-?.?.?.jar) do (
    copy %%a ..\stanford-corenlp.jar
)
for %%a in (stanford-corenlp*models.jar) do (
    copy %%a ..\stanford-corenlp-models.jar
)

for %%a in (slf4j-*.jar) do (
    copy %%a ..
)

for %%a in (ejml*.jar) do (
    copy %%a ..\ejml.jar
)
