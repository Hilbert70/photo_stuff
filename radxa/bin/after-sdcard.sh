#! /bin/bash

echo "Done mounting" > /root/done_mounting

mkdir -p ~/keys

if [ ! -f "/root/keys/pwdPrivKey.pem" ]; then
	openssl genrsa -out /root/keys/pwdPrivKey.pem 2048
	openssl rsa -in /root/keys/pwdPrivKey.pem -out /root/keys/pwdPubKey.pem -outform PEM -pubout
	chmod 0600 /root/keys/pwdPrivKey.pem
fi

mkdir -p /mnt/sdcard/keys

if [ ! -f /mnt/sdcard/keys/pwdPubKey.pem ]; then
	cp ~/keys/pwdPubKey.pem /mnt/sdcard/keys/pwdPubKey.pem 


	#example for encripting the password
	echo 'echo "password" | openssl rsautl -encrypt -inkey /mnt/sdcard/keys/pwdPubKey.pem -pubin  -out pwd.dat' > /mnt/sdcard/encrypt-password-example.sh
	chmod +x /mnt/sdcard/encrypt-password-example.sh
fi

old_ifs="$IFS"
IFS='
'

Cardssids=()
Cardpwds=()
# get ssid's on the card
for ssid in `ls /mnt/sdcard/ssids`; do
    Cardssids+=( $ssid )
    password=$(openssl rsautl -decrypt -inkey keys/pwdPrivKey.pem -in /mnt/sdcard/ssids/$ssid)
    Cardpwds+=( $password )
done

# test
#for i in ${Cardssids[@]}; do
#  echo $i
#done

nmssids=()
for ssid in `nmcli -f name c show| grep -v NAME | sort | uniq`; do
    nmssids+=( $(echo $ssid | tr -d " ") )
done
#nmssids+=( bla bal )

# do some cross checking
for i in ${!Cardssids[@]}; do                                                                    
    for j in ${!nmssids[@]}; do
	if [ "${Cardssids[$i]}" == "${nmssids[$j]}" ] ; then
	    # remove from both lists
	    unset "nmssids[$j]"
	    unset "Cardssids[$i]"
	    unset "Cardpwds[$i]"
	fi
    done
done

#refresh ssid scan, somehow this is needed

nmcli dev wifi >/dev/null

# remove ssids not in the Cardsssids list from the networkmanager
for j in ${!nmssids[@]}; do
    echo "remove from nm:" \"${nmssids[$j]}\"
    nmcli c delete "${nmssids[$j]}"
done

# add to network manager list
for j in ${!Cardssids[@]}; do
    echo "add to nm:" \"${Cardssids[$j]}\"
    nmcli dev wifi connect "${Cardssids[$j]}" password "${Cardpwds[$j]}"
done


IFS=$old_ifs

nmcli -f ssid dev wifi | grep -v SSID| grep -v "\-\-"|sort | uniq > /mnt/sdcard/ssid-list


# Do sshd check

if [ `cat /mnt/sdcard/sshd` == 1 ] ; then
    systemctl status ssh| grep active
    if [ $? == 1 ] ; then
	systemctl start ssh
	systemctl enable ssh
	echo "sshd already activating" > /mnt/sdcard/sshd-status
    else
	echo "sshd already active" > /mnt/sdcard/sshd-status
    fi
else
    systemctl stop ssh
    systemctl disable ssh
    echo "sshd already inactivated" > /mnt/sdcard/sshd-status
fi

systemctl status ssh >> /mnt/sdcard/sshd-status
