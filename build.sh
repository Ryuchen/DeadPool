#!/usr/bin/env bash
echo "epoch num is `git rev-list HEAD | wc -l`"

mkdir -p dest/home/soft/Deadpool
mkdir -p dest/home/soft/monit/conf/monit.d
mkdir -p dest/usr/lib/systemd/system/
mkdir -p dest/etc/logrotate.d/

base_dir="/home/soft/Deadpool"
mkdir -p $base_dir
virtualenv $base_dir/venv --no-download --no-site-packages
source $base_dir/venv/bin/activate
pip install -r requirements.txt --trusted-host repo --index-url https://mirrors.aliyun.com/pypi/simple/


for target in apps bin common config contrib deadpool $base_dir/venv requirements.txt README.md
do
    cp -r ${target} dest/home/soft/Deadpool/
done

cp conf.d/systemd/* dest/usr/lib/systemd/system/
cp conf.d/monit/* dest/home/soft/monit/conf/monit.d/
cp conf.d/logrotate/* dest/etc/logrotate.d/
chmod 644 dest/etc/logrotate.d/deadpool.logrotate

cd dest

/usr/local/bin/fpm -s dir -t rpm -n deadpool -v `basename ${CI_BUILD_REF_NAME}` \
                   --rpm-digest md5 \
                   --rpm-group goldeneye \
                   --architecture noarch \
                   --epoch `git rev-list HEAD | wc -l` \
                   --iteration `git rev-list HEAD | wc -l` \
                   --exclude .git \
                   --exclude install \
                   --before-install ../install/pre-install \
                   --after-install ../install/pos-install \
                   --before-upgrade ../install/pre-upgrade \
                   --after-upgrade ../install/pos-upgrade \
                   --description `date +'%Y-%m-%dT%H:%M:%S'` \
                   --chdir . home etc usr
