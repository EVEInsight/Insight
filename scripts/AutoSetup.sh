#!/usr/bin/env bash
# This script automatically creates a Python virtual environment and installs the needed packages, including the Docker swagger client.

error()
{
        echo 'An error occurred when attempting to setup the Python virtual environment and install/upgrade the required packages.'
        exit 1
}

main(){
echo 'This script automatically creates a Python virtual environment and installs the needed packages for Insight. Ensure you have Docker installed.'
read -p "Download the latest Fuzzwork SDE database? Required for new installs. [y/n]" resp
case $resp in
        'y')
                sde_dowload=true;;
        'n')
                sde_download=false;;
        *)
                echo "Invalid response";
                error;;
esac
Script=$(readlink -f "$0")
SPath=$(dirname "$Script")
cd $SPath/..
python3 -m venv venv || error
source venv/bin/activate || error
pip3 install --upgrade setuptools
pip3 install --upgrade wheel
echo 'Request sudo for running Docker command.'
sudo docker run --rm -v ${PWD}:/local swaggerapi/swagger-codegen-cli generate -i "https://esi.tech.ccp.is/_latest/swagger.json" -l python -o /local/python-client || error
echo 'Request sudo to chown generated client to current user.'
sudo chown -R $USER:$USER python-client || error
cd python-client || error
python3 setup.py install || error
cd ..
rm python-client -R
pip3 install --upgrade -r requirements.txt
cp -n default-config.ini config.ini
if $sde_download; then
        wget -nc https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2.md5 || error
        wget -nc https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2 || error
        echo 'Running checksum.'
        md5sum -c sqlite-latest.sqlite.bz2.md5 || error
        echo 'Unzipping file.'
        bunzip2 -f sqlite-latest.sqlite.bz2 || error
        rm sqlite-latest.sqlite.bz2.md5
        rm sqlite-latest.sqlite.bz2
fi
echo "All set! Make sure to edit your 'config.ini' file and then you can start Insight with the 'insight_start.sh'
script in this directory. Run this script again to update the required packages and don't forget to run 'git pull' to
keep up with the latest Insight updates. It is recommended to use the 'dev' branch of Insight to get the latest and
stable features via 'git checkout dev'."
}
main
