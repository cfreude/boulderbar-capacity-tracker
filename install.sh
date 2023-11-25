sudo apt-get install python3-venv
cd ~
mkdir boulderbar
cd boulderbar
python -m venv ./env
source ./env/bin/activate
pip install pandas plotext
git clone 