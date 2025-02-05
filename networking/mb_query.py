from lxml import html
import requests
from pathlib import Path

mb_url = "https://mb.srb2.org"
mb_link = mb_url
maps_sublink = mb_link + "/forums/maps.23/"
characters_sublink = mb_link + "/forums/characters.25/"
lua_sublink = mb_link + "/forums/lua.26/"
misc_sublink = mb_link + "/forums/miscellaneous.27/"
assets_sublink = mb_link + "/forums/assets.29/"

# Oh so sneaky:
headers = {'User-Agent':
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
               'AppleWebKit/537.36 (KHTML, like Gecko) '
               'Chrome/39.0.2171.95 Safari/537.36'}


class Mod:
    def __init__(self, name, thread_url):
        self.mb_base_url = mb_url
        self.name = name
        self.thread_base_url = thread_url
        self.description = None
        self.download_button_url = None
        self.url = self.mb_base_url + self.thread_base_url
        self.html = None

    def get_html(self):
        url = self.url
        response = requests.get(url,
                                stream=True,
                                headers=headers)
        response.raw.decode_content = True
        self.html = html.parse(response.raw)
        return self.html

    def set_download_button_link(self):
        mod_page_response = requests.get(self.url, stream=True, headers=headers)
        mod_page_response.raw.decode_content = True
        mod_page = html.parse(mod_page_response.raw)
        download_button_url = mod_page.xpath(
            '//a[@class="button--cta resourceDownload button button--icon button--icon--download"]/@href')
        self.download_button_url = self.mb_base_url + download_button_url[0]
        return self.download_button_url

    def get_download_urls(self):
        download_urls = {}
        response = requests.get(self.download_button_url, stream=True, headers=headers)
        response.raw.decode_content = True
        download_page = html.parse(response.raw)
        if "Choose file…" in download_page.xpath('//h1[@class="p-title-value"]/text()'):
            for url in download_page.xpath('//a[@class="button button--icon button--icon--download"]/@href'):
                download_name = download_page.xpath(
                    '//a[@href="{}"]/ancestor::div[@class="contentRow-main"]/h3/text()'.format(url))
                download_urls[download_name[0]] = self.mb_base_url + url
        # Only 1 download URL:
        else:
            download_urls["Download"] = self.download_button_url
        return download_urls

    def get_description(self):
        print("get_mod_description")
        if not self.html:
            self.get_html()
        self.description = '\n'.join(self.html.xpath(
            '//div[@class="bbWrapper"]/text()'))
        return self.description


def get_mods(addons_subforum_url):
    """
    Gets a list of all mods from addons subforum URL
    :param download_url: The URL of the SRB2 MB sub-forum to search
    :return: Returns a list containing Mod class instances
    """
    last_page = False
    mod_list = []
    mod_links = []
    mod_names = []
    page_counter = 1
    previous_data = None
    # Iterate through pages grabbing thread names and their links:
    while not last_page:
        tree = get_addons_page_html(addons_subforum_url, page_counter)
        current_mod_links = get_list_of_thread_links(tree)
        current_mod_names = get_list_of_thread_names(tree)
        if current_mod_names == previous_data:
            # This works because if you go past the real number of pages,
            #   the MB will send you back to the last valid page,
            #   making you get the same data twice
            last_page = True
        else:
            mod_names.extend(current_mod_names)
            mod_links.extend(current_mod_links)
        previous_data = current_mod_names
        page_counter += 1

    # Make our list of mods
    for index in range(len(mod_names)):
        mod = Mod(mod_names[index], mod_links[index])
        mod_list.append(mod)

    return mod_list


def get_addons_page_html(url, page_num):
    """
    SRB2 MB is broken up into subforums that sometimes have multiple pages.
    This function returns the html tree for a specified page.
    :param url: The base download_url for the subforum, not including the specific page.
    :param page_num: The page number as an integer
    :return: HTML tree: the results of html.parse(requests.get(download_url))
    """
    response = requests.get(url + "?page={}".format(str(page_num)),
                            stream=True,
                            headers=headers)
    response.raw.decode_content = True
    return html.parse(response.raw)


def get_mod_by_name(name, mod_list):
    for mod in mod_list:
        if mod.name == name:
            return mod
    return Mod("blank", "blank")  # Return a blank mod so functions that rely on this function don't crash


def get_list_of_thread_names(parsed_html):
    """
    Get list of all thread names from a page on the MB
    :param request_response: The results of html.parse(response.raw)
    :return: List containing all thread names on the page
    """
    return parsed_html.xpath('.//div[@class="structItem-title"]/*[@data-tp-primary="on"]/text()')


def get_list_of_thread_links(parsed_html):
    return parsed_html.xpath('.//div[@class="structItem-title"]/*[@data-tp-primary="on"]/@href')


def is_downloadable(url):
    """
    Does the url contain a downloadable resource
    """
    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    return True


def download_mod(base_path, download_url):
    # TODO: apparently https://.../download isn't the actual download URL! It crashes this function.
    # NOTE the stream=True parameter below
    with requests.get(download_url, stream=True, headers=headers) as r:
        filename = r.headers.get("Content-Disposition").split("filename=")[1]
        filepath = base_path + filename.replace('"', '')
        r.raise_for_status()
        # Create path if it doesn't already exist:
        Path(filepath).mkdir(parents=True, exist_ok=True)
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                # if chunk:
                f.write(chunk)
    return filepath


def extract_mod(filepath):
    extracted_files = []  # full filepaths
    return extracted_files

# TODO: remove these testing links:
# https://mb.srb2.org/addons/v4-0-1-patch-sound-warning-tails-dolls-forest-v4-0-1.3580/version/7617/download?file=75204
# https://mb.srb2.org/addons/v4-0-1-patch-sound-warning-tails-dolls-forest-v4-0-1.3580/version/7617/download?file=75205
