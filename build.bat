@RD /S /Q build
@RD /S /Q dist

pyinstaller VODHighlights.py --onefile --name "StreamHighlightReelCreator" -i assets/logo.ico -y --clean --splash assets/splash_screen.png

cp assets dist -r

cd dist
zip -r "StreamHighlightReelCreatorWindows.zip" *

cp ../defaults.json defaults.json

PAUSE
