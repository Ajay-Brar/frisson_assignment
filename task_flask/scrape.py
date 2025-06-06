import requests
from bs4 import  BeautifulSoup
import os

save_images = 'Images/'
if not os.path.exists(save_images):
  os.makedirs(save_images)


query = 'avengers'
url = f"https://www.google.com/search?client=opera-gx&hs=N05&sca_esv=76076938c4eddbf2&q={query}&udm=2&fbs=AIIjpHxU7SXXniUZfeShr2fp4giZ1Y6MJ25_tmWITc7uy4KIetxLMeWi1u_d0OMRvkClUba76WL62NDKV-tuv6_wPYBC9v7ob7zIjaDzKC7u3qUzfD7e7YM11gPmU080OmUCW2ra6dnp670CRAaKtkLzGbsTDSqnsqGdRqpRgn7m8J8sRSSZQGr1gsZNygXo3gegFkXRGx97PLV94iHXkSHBuVAPRbU0rg&sa=X&ved=2ahUKEwiMo4jp2tSNAxW8dmwGHYz0MpEQtKgLegQICBAB&biw=722&bih=707&dpr=1.25"

response = requests.get(url)
response.status_code
response.content # for html source/content

soup = BeautifulSoup(response.content,'html.parser')
image_tags = soup.find_all('img')[1:]


# print(image_tags)


i = 0
for image in image_tags:
  image_url = image['src']
  image_data = requests.get(image_url).content
  with open(os.path.join(save_images,f'{i}.jpeg'),'wb') as file:
    file.write(image_data)
  i+=1