@echo off
echo Starting Cryptocurrency Forecasting Application...
echo.

REM Test data sources first
echo Testing data sources...
python test_manual.py
echo.

echo Press any key to start the Flask application...
pause

echo.
echo Starting Flask server...
echo Open your browser to: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python main.py
