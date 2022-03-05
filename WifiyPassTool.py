# # to use windows commands
# # to use regex
import subprocess
import re


def initVars():
    """
    This function init the main vars of the program.

    :return:
    command_output =the output of wifi profiles-system command.
    profile_names= all the wifi profiles that was found by the system command.
    wifi_list= an empty list to store all the profiles.
    """
    # use command shell from python.
    command_output = subprocess.run(["netsh", "wlan", "show", "profile"], capture_output=True).stdout.decode()

    # We imported the re module so that we can make use of regular expressions. We want to find all the Wifi names which is always listed after "ALL User Profile     :". In the regular expression we create a group of all characters until the return escape sequence (\r) appears.
    profile_names = (re.findall("All User Profile     : (.*)\r", command_output))

    # We create an empty list outside of the loop where dictionaries with all the wifi ssid and passwords will be saved.
    wifi_list = list()
    return wifi_list, profile_names, command_output


def main():
    deal_with_wifi_profiles()


def export_pass_to_file(wifi_list):
    """
    This function prints and export all the profiles to an text file.

    :return:
    none
    """
    for x in range(len(wifi_list)):
        print(wifi_list[x])
    ##Write the contents of the wifi ssids and passwords to file
    with open('wifi.txt', 'w+') as fh:
        for x in wifi_list:
            fh.write(f"SSID: {x['ssid']}\nPassword: {x['password']}\n")


def deal_with_wifi_profiles():
    """
    This function deals with all the profiles was found by system command, store them into an dictionary if was found,
    and activate the file export function.

    :return:
    none
    """
    wifi_list, profile_names, command_output = initVars()

    # If we didn't find profile names we didn't have any wifi connections, so we only run the part to check for the details of the wifi and whether we can get their passwords in this part.
    if len(profile_names) != 0:
        for name in profile_names:
            # Every wifi connection will need its own dictionary which will be appended to the wifi_list
            wifi_profile = dict()
            # We now run a more specific command to see the information about the specific wifi connection and if the Security key is not absent we can possibly get the password.
            profile_info = subprocess.run(["netsh", "wlan", "show", "profile", name],
                                          capture_output=True).stdout.decode()
            # We use a regular expression to only look for the absent cases so we can ignore them.
            if re.search("Security key           : Absent", profile_info):
                continue
            else:
                # Assign the SSID of the wifi profile to the dictionary
                wifi_profile["ssid"] = name
                # These cases aren't absent and we should run them "key=clear" command part to get the password
                profile_info_pass = subprocess.run(["netsh", "wlan", "show", "profile", name, "key=clear"],
                                                   capture_output=True).stdout.decode()
                # Again run the regular expressions to capture the group after the : which is the password
                password = re.search("Key Content            : (.*)\r", profile_info_pass)
                # Check if we found a password in the regular expression. All wifi connections will not have passwords.
                if password == None:
                    wifi_profile["password"] = None
                else:
                    # We assign the grouping (Where the password is contained) we are interested to the password key in the dictionary.
                    wifi_profile["password"] = password[1]
                # We append the wifi information to the wifi_list
                wifi_list.append(wifi_profile)

    export_pass_to_file(wifi_list)


if __name__ == '__main__':
    main()
