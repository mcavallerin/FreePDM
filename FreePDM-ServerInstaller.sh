!# /bin/bash
# :copyright: Copyright 2022 by the FreePDM team
# :license: MIT License.

printf "Welcome to the server Installer from FreePDM:\n"

# TODO: Create install Conf file
# TODO: Install ssh-server
# TODO: Install Web-server - Optional
# TODO: Install SQL-server
# TODO: Install LDAP-server - Optional
# TODO: Install Other dependencies

printf "There are a set of (optional )dependencies that are configured now. This dependecies are:
- A SSH server
- A web server (Optional)
- A SQL server
- A LDAP server (Optional)\n"

sleep 1

# Add line about check for existing server
printf "Do you want to install a Webserver? (y / n)\n"

read installwebserver

if [[ $installwebserver == "y" ]]; then
	printf "What backend do you want to install? (1 - 2)\n
1 - Apache Httpd
2 - Nginx\n"

	read webserverc  # webserver case

	if [[ $webserverc == "" ]]; then
		webserverc=1
		printf "http server was emtpty and is replaced by it's default"
	fi

	# python webserver default has to be choosen!
	printf "What python web backend do you want to install? (1 - 4)\n
1 - Django
2 - Pyramid (Default)
3 - Falcon
4 - WebPy\n"

	read webserverpythonc  # webserver python case

	if [[ $webserverpythonc == "" ]]; then
		webserverpythonc=2
		printf "python web server was emtpty and is replaced by it's default"
	fi

	printf "What is your server name?\n"

	read webservername

	printf "What is your (web )server_domain OR IP address? (default something like web.somename.com)\n"

	read webhostname

	# maybe something about admin + password, ports etc
elif [[ $installwebserver == "n" ]]; then
	:
else
	printf "$installwebserver is not 'y' OR 'n'.\n"
fi

# Add line about check for existing server
printf "What SQL server do you want to install? (1 - 3)\n
1 - MySQL
2 - SQLite
3 - PostgreSQL(default)\n"

read sqlserverc  # sqlserver case

if [[ $sqlserverc == "" ]]; then
	sqlserverc=3
	printf "SQL server was emtpty and is replaced by it's default\n"
fi

read -p "Enter SQL Username:" sqlservername

printf "What is your (sql )server_domain OR IP address? (default something like sql.somename.com)\n"

read sqlhostname

# maybe something about admin + password, ports etc

# Add line about check for existing server
printf "Do you want to install a LDAP server? (y / n)\n"

read installldapserver

if [[ $installldapserver == "y" ]]; then
	printf "What LDAP server do you want to install? (1 - 4)\n
1 - open LDAP (Default)
2 - Apache DS
3 - openDJ
4 - 389 Directory server\n"

	read ldapserverc

	if [[ $ldapserverc == "" ]]; then
		ldapserverc=1
		printf "LDAP server was emtpty and is replaced by it's default"
	fi

	read -p "Enter LDAP Username:" ldapusername

	# read -sp "Enter LDAP Password:" ldappw1  # Silent
	read -n "Enter LDAP Password:" ldappw1  # With asterix

	read -n "Re-enter LDAP Password:" ldappw2  # With asterix

elif [[ $installldapserver == "n" ]]; then
	:
else
	printf "$installldapserver is not 'y' OR 'n'.\n"
fi

# Show cofiguration summery


# from here start installing
printf "Installing start within a few seconds\n"

sleep 3

printf "Update repositories.\n"
sudo apt update
# printf "Upgrade repositories.\n"  # upgrade don't work yet
# sudo apt upgrade

# Install of a SSH server
testcommand="ssh"
packages="openssh-server"
# if ! [[ $(command -v $the_command) &> /dev/null ]]; then
if ! [[ $(command -v $testcommand) ]]; then
  printf "$testcommand could not be found.\n$packages shall be installed. \n"
	sudo apt install -y $packages
	exit
else
	printf "$packages already installed\n"
fi

# Install of a webserver

if [[ $installwebserver == "y" ]]; then

	case $webserverc in
		1)
			# https://ubuntu.com/tutorials/install-and-configure-apache#1-overview
			webserver="Apache httpd"
			testcommand="apache2"  # should also work with apachectl -v
			packages="apache2"
			;;
		2)
			# https://ubuntu.com/tutorials/install-and-configure-nginx#1-overview
			webserver="Nginx"
			testcommand="nginx"
			packages="nginx"
			;;
		3)
			# https://www.hostinger.com/tutorials/how-to-install-tomcat-on-ubuntu/
			webserver="Appache tomcat"  # Java
			testcommand=""
			packages=""
				;;
	esac

	printf "The following Web server shall be installed: $webserver."
	sleep 1

	if ! [[ $(command -v $testcommand) ]]; then
	  printf "$testcommand could not be found.\n$packages shall be installed. \n"
		sudo apt install -y $packages
		exit
	else
		printf "$packages already installed \n"
	fi

	# If statement for IPaddres has always same length and set of dots on same place

	case $webserverpythonc in
		# Make use of package manager OR Virtual Environment...?
		1)
			# https://www.digitalocean.com/community/tutorials/how-to-install-the-django-web-framework-on-ubuntu-20-04
			webserver="Django"
			testcommand=""  # "django-admin --version"
			packages=""  # "python3-django"
			;;
		2)
			# https://www.digitalocean.com/community/tutorials/how-to-use-the-pyramid-framework-to-build-your-python-web-app-on-ubuntu
			webserver="Pyramid"
			testcommand=""
			packages=""
			;;
		3)
			# https://www.digitalocean.com/community/tutorials/how-to-deploy-falcon-web-applications-with-gunicorn-and-nginx-on-ubuntu-16-04
			webserver="Falcon"
			testcommand=""
			packages=""
			;;
		4)
			webserver="WebPy"
			testcommand=""
			packages=""  # "python-webpy"
			;;
	esac

	# if ! (( command -V $testcommand )); then  #
	# 	printf "$testcommand could not be found.\n$packages shall be installed. \n"
	# 	sudo apt install -y $packages
	# 	exit
	# else
	# 	printf "$packages already installed \n"
	# fi

	printf "The following Python Web server shall be installed: $webserverpython."
	sleep 1

fi


# install of SQL server

# Check if SQL server already exist. if yes  add database to existing server?
# work only with selected sql server

case $sqlserverc in
	1)
		sqlserver="MySQL"
		testcommand="mysql"
		packages="mysql-server"
		;;
	2)
		sqlserver="SQLite"
		testcommand="sqlite3"  # can also be sqlite3 --version
		packages="sqlite3"
		;;
	3)
		# https://www.geeksforgeeks.org/install-postgresql-on-linux/
		# https://sqlserverguides.com/postgresql-installation-on-linux/
		sqlserver="postgreSQL"
		testcommand="postgres"
		packages="postgresql postgresql-contrib"

		# from: https://www.postgresql.org/download/linux/debian/
		# Create the file repository configuration:
		printf "Add postgreSQL repository to list.\n"
		sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'

		# Import the repository signing key:
		wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
		;;
esac

printf "The following SQL server shall be installed: $sqlserver.\n"

printf "Update packages.\n"
sudo apt-get update

if ! [[ $(command -v $testcommand) ]]; then
	printf "$testcommand could not be found.\n$packages shall be installed. \n"
	sudo apt install -y $packages
	exit
else
	printf "$packages already installed \n"
fi

# install LDAP server

if [[ $installldapserver == "y" ]]; then

	case $ldapserverc in
		# Basically all are Java implementations except 389 directory service
		1)
			# https://www.howtoforge.com/how-to-install-openldap-on-debian-11/
			ldapserver="open LDAP"
			testcommand="slapd"  # https://serverfault.com/questions/839948/how-to-check-the-version-of-openldap-installed-in-command-line
			packages="slapd ldap-utils"
			;;
		2)
			ldapserver="Apache DS"
			testcommand=""
			packages="apacheds"
			;;
		3)
			# https://backstage.forgerock.com/docs/opendj/2.6/install-guide/
			ldapserver="OpenDJ"
			testcommand=""
			packages=""
			;;
		4)
			# https://directory.fedoraproject.org/docs/389ds/howto/howto-debianubuntu.html
			ldapserver="389 Directory server"
			testcommand=""
			packages="termcap-compat apache2-mpm-worker"
			;;
	esac

	printf "The following LDAP server shall be installed: $ldapserver."
	sleep 1
fi

if ! [[ $(command -v $testcommand) ]]; then
	printf "$testcommand could not be found.\n$packages shall be installed. \n"
	sudo apt install -y $packages
	exit
else
	printf "$packages already installed \n"
fi

# Install other dependecies
