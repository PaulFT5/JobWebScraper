def get_experience_level(soup):
    return soup.find(class_="hover:text-ink").get_text().split()[0]

def get_work_type(soup):
    soup = soup.find("div", class_="ml-6").get_text()
    return soup.split(";")[0]

def get_company_logo(soup):
    a_tag = soup.find("a", href="#company-widget-box")
    if not a_tag:
        return None
    img_tag = a_tag.find("img")
    if not img_tag:
        return None
    return img_tag.get("src")

#def get_description(soup):