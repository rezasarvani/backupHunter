import argparse
import tldextract
import json
import os
import sys
import re
import datetime


config_exist = os.path.exists("configs.json")

if not config_exist:
    print("[-] Failed to find configs.json")
    sys.exit(0)

else:
    config = open("configs.json", "r", encoding="utf-8", errors="ignore")
    config = json.load(config)


parser = argparse.ArgumentParser(description="Backup Killer: Find Backup Files On Target Web Application.")

parser.add_argument("-u", "--url",
                    help="Enter your target url.",
                    default=False)

parser.add_argument("-o", "--output",
                    help="Enter your output name.",
                    default="cli")

parser.add_argument("-v", "--verbose",
                    action="store_true",
                    help="Show more verbose debug messages.",
                    default=False)

parser.add_argument("-q", "--quite",
                    action="store_true",
                    help="Suppress All Info/Debug Messages.",
                    default=False)

options = parser.parse_args()

if not options.url:
    print("[-] Please Enter A Valid URl")
    sys.exit(0)

if "http" not in options.url:
    print("[-] Please Enter Your Target Address With Schema (http|https)")
    sys.exit(0)

def verbose_print(message):
    if options.verbose and not options.quite:
        print(message)

def message_print(message):
    if not options.quite:
        print(message)

def current_time():
    c_time = str(datetime.datetime.now())
    return c_time[:19]

def domain_name_backup(domain):
    wordlist = config["backupfile_extensions"]
    schema = "https" if "https://" in domain else "http"
    parsed_domain = tldextract.extract(domain)
    extracted_domain = parsed_domain.domain
    extracted_tld = parsed_domain.suffix
    extracted_subdomain = parsed_domain.subdomain
    # sub.google.com | google.com
    final_address = f"{extracted_subdomain}.{extracted_domain}.{extracted_tld}"
    final_address = final_address[1:] if final_address[0] == "." else final_address
    # sub.google | google
    domain_subdomain = f"{extracted_subdomain}.{extracted_domain}"
    domain_subdomain = domain_subdomain[1:] if domain_subdomain[0] == "." else domain_subdomain
    single_domain_tld = f"{extracted_domain}.{extracted_tld}"

    input_list = [
        final_address,
        domain_subdomain,
        f"www.{domain_subdomain}",
        f"www.{final_address}",
        extracted_domain,
        single_domain_tld
    ]
    output_set = set()

    for address in input_list:
        for word in wordlist:  # ['.rar', '.zip', '.7z']
            if "www.www" in address:
                continue
            output_set.add(f"{schema}://{final_address}/{address}{word}")

    return output_set

def check_url(domain):
    domain = domain.replace("https://", "")
    domain = domain.replace("http://", "")
    domain_apart = domain.split("/")
    domain_apart = [part for part in domain_apart if len(part) > 0]
    if len(domain_apart) > 1:
        return True
    return False

def backup_extract(url):
    url = url if url[-1] != "/" else url[:-1]
    url = re.sub(r"\?.*", "", url)
    domain_backup_extensions = config["backupfile_extensions"]
    backup_extensions = config["extensions"]
    wordlist = set(domain_backup_extensions + backup_extensions)
    output_set = set()

    for word in wordlist:
        output_set.add(f"{url}{word}")

    return output_set


verbose_print(f"[DBUG] Backup Killer Engine Started. ({current_time()})")
input_domain = options.url
verbose_print(f"[DBUG] Working On [{input_domain}]. ({current_time()})")

domain_backup_list = domain_name_backup(input_domain)

if not check_url(input_domain):
    backup_list = set()
else:
    backup_list = backup_extract(input_domain)

final_output = set.union(domain_backup_list, backup_list)

if options.output.lower() == "cli":
    verbose_print(f"[DBUG] Printing Output To STDOUT. ({current_time()})")
    for word in final_output:
        print(word)
else:
    verbose_print(f"[DBUG] Saving Output Into [{options.output}]. ({current_time()})")
    file_handle = open(options.output, "w", encoding="utf-8", errors="ignore")
    for word in final_output:
        file_handle.write(f"{word}\n")
    file_handle.close()
    message_print(f"[+] File Saved To: {options.output}")
verbose_print(f"[*] Backup Killer Finished It's Job. [{current_time()}]")