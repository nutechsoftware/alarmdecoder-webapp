#Download and install the latest OpenCV
type wget > /dev/null 2>&1 || { echo >&2 "wget command not found. Aborting."; exit 1; }
type unzip > /dev/null 2>&1 || { echo >&2 "unzip command not found. Aborting."; exit 1; }
type make > /dev/null 2>&1 || { echo >&2 "make command not found. Aborting."; exit 1; }

version="$(wget -q -O - http://sourceforge.net/projects/opencvlibrary/files/opencv-unix | egrep -m1 -o 'opencv-unix/[0-9](\.[0-9]+\-*[a-z0-9]*)+' | cut -c13-)"
echo "Installing OpenCV" $version
echo "Installing Dependencies"
sudo apt-get update
sudo apt-get install cmake checkinstall
mkdir OpenCV
cd OpenCV
ret_code = $?

if [ $ret_code != 0 ]
then
    echo "Unable to execute command, exiting"
    exit 1
fi
echo "Downloading OpenCV" $version
wget -O OpenCV-$version.zip http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/$version/opencv-"$version".zip/download

ret_code = $?

if [ $ret_code != 0 ]
then
    echo "Unable to execute wget command, exiting"
    exit 1
fi

echo "Installing OpenCV" $version
unzip OpenCV-$version.zip
ret_code = $?

if [ $ret_code != 0 ]
then
    echo "Unable to execute unzip command, exiting"
    exit 1
fi

cd opencv-$version
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D WITH_TBB=ON -D BUILD_PYTHON_SUPPORT=ON -D BUILD_opencv_java=OFF ..
ret_code = $?

if [ $ret_code != 0 ]
then
    echo "cmake failed exiting"
    exit 1
fi

make -j2

ret_code = $?

if [ $ret_code != 0 ]
then
    echo "Failed during make, exiting"
    exit 1
fi

sudo checkinstall
sudo sh -c 'echo "/usr/local/lib" > /etc/ld.so.conf.d/opencv.conf'
sudo ldconfig
echo "OpenCV" $version "ready to be used"
