#!/bin/sh

declare script_name="cals"
declare ext="py"
declare cfg=".bash_profile"

declare grn="\e[0;92m"
declare red="\e[0;91m"
declare reset="\e[0m"

function make_dir {
    printf "Creating dir $personal_bin...\n" && 
    mkdir $personal_bin
    }

function add_to_path {
    printf "Adding '$personal_bin' to \$PATH in $cfg...\n" & 
    echo export PATH="$personal_bin:\$PATH" >> $home/$cfg
}

printf "\nAttempting installation of script '$script_name'...\n\n"

[[ -f './requirements.txt' ]] && 
echo "Installing requirements..." &&
eval pip3 install -r requirements.txt

case $OSTYPE in 
    "darwin"*) declare home="/Users/$USER" ;;
    "linux"*) declare home="/home/$USER" ;;
esac

declare personal_bin="$home/bin"

[ -n $ZSH_VERSION ] && 
cfg=".zprofile"

[[ ! -d $personal_bin ]] && 
make_dir ||
printf "\n${grn}[OK]${reset} '$personal_bin' exists...\n"

grep -q "$personal_bin" $home/$cfg && 
printf "${grn}[OK]${reset} '$personal_bin' already in \$PATH...\n" ||
add_to_path

printf "\nInstalling '$script_name'...\n"
chmod +x ./${script_name}.$ext &&
cp ./${script_name}.$ext $personal_bin/$script_name &&
printf "\n${grn}[SUCCESS]${reset} Script '$script_name' installed at '$personal_bin/$script_name'!\n\n" ||
printf "\n${red}[ERROR]${reset} Something went wrong...\n" exit 1

exit 0