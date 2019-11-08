from .thumb import alldrivedata
def categories_processor(request):
 categories = alldrivedata()
 warn = False
 for category in categories:
     if category[3]>=0.9:
         warn = True
 return {'categories': categories, 'warning':warn}