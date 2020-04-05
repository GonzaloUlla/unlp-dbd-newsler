echo "Creating python environment"
python -m venv .

echo "Activating environment"
.\Scripts\activate.bat

echo "Installing dependencies"
pip install -r requirements.txt

echo "##################################################"
echo "To deactivate env just do .\Scripts\deactivate.bat"
echo "##################################################"
