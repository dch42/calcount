#!/bin/sh

declare script_name="calcount"
declare personal_bin="/Users/$USER/bin"
declare hidden_dir="/Users/$USER/.$script_name"
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
    echo export PATH="$personal_bin:\$PATH" >> /Users/$USER/$cfg
}

 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
###############################################################
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

printf "\nAttempting installation of script '$script_name'...\n\n"

echo "Installing requirements..."
eval pip3 install -r requirements.txt

[ -n $ZSH_VERSION ] && 
cfg=".zprofile"

[[ ! -d $personal_bin ]] && 
make_dir ||
printf "'$personal_bin' exists...\n"

grep -q "$personal_bin" /Users/$USER/$cfg && 
printf "'$personal_bin' already in \$PATH...\n" ||
add_to_path

printf "\nInstalling $script_name...\n"
chmod +x ./${script_name}.py &&
cp ./${script_name}.py $personal_bin/$script_name &&
printf "${grn}[SUCCESS]${reset} Script $script_name installed at '$personal_bin/$script'!\n\n" ||
printf "${red}[ERROR]${reset} Something went wrong...\n" exit 1

exit 0
