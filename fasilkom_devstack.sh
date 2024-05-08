if [ -z "$1" ]; then
    echo "Please enter SUDO_PASS as the first argument"
    exit
fi

sudo env "RETRY=$RETRY" SUDO_PASS=$1 ./devstack.sh immanuel01@kawung.cs.ui.ac.id:12122 admin@10.119.106.21 admin@10.119.106.22
