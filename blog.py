

def blog_post(title,bloglink,imagelink,blogdate):
    data = f'''<a href="{bloglink}" style="text-decoration:none;"><div class="card mb-3 text-danger bg-light" style="max-width: 70%;position:relative;left:15%;">
  <img src="{imagelink}" class="card-img-top" alt="..." style="height:300px;">
  <div class="card-body">
    <h5 class="card-title" style="font-size:3rem;">{title}</h5>
    <br>
    <p class="card-text"><small class="text-secondary">{blogdate}</small></p>
  </div></div></a><br><br>'''
    return data

titles = ['Importance of Data Quality.','Impact of Missing Values.']
blog_links = ['/blog/article1.html?user={{htmlData.user}}','/blog/article2.html?user={{htmlData.user}}']
image_links = ['/static/images/Untitled.png','/static/images/Untitled.png']
blog_dates = ['feb 26,2023','feb 26,2023']
blogdata = ''
for idx in range(len(titles)):
    data_ = blog_post(titles[idx],blog_links[idx],image_links[idx],blog_dates[idx])
    blogdata = blogdata+data_

