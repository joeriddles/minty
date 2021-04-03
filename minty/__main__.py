from . import minty


if __name__ == '__main__':
    mint_sitemap_index = 'https://www.mintyteeth.com/sitemap_index.xml'
    urls = minty.find_sitemap_urls(mint_sitemap_index)
    eggs = minty.find_eggs(urls)
    minty.download_eggs(eggs)
