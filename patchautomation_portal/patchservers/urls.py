"""Copyright 2018 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE. """

# pages/urls.py

from django.urls import path
from patchservers import views

urlpatterns = [
    path('invokempa/<str:uploadid>/<str:operation>',views.invokempa, name="invokempa"),
    path('downloadrun/<str:uploadid>',views.downloadrun, name="downloadrun"),
    path("getdump/<str:appname>",views.getdump, name="getdump"),
    path("index/", views.home, name='home'),
    path("overview/", views.overview, name='overview'),
    path("", views.serverpatchdetails_list, name="serverpatchdetails_list"),
    path("home/", views.serverpatchdetails_index, name="serverpatchdetails_index"),
    path("<int:id>/", views.serverpatchdetails_detail, name="serverpatchdetails_detail"),
    path('upload/', views.upload_task,name="upload_task"), 
    path('Import_excel',views.Import_excel,name="Import_excel"),
    path('trackresult/',views.trackresult_task,name="trackresult_task"),
    path('trackresult/<str:uploadid>/<str:result>',views.trackresult_task,name="trackresult_task"),
    path('invokeplaywright/',views.invokeplaywright,name="invokeplaywright"),
    path('list/',views.list_server_patch_details,name="list_server_patch_details"),    
    path('trackupload/',views.trackupload_task,name="trackupload_task"),    
    path('dashboard/',views.dashboard,name="dashboard"),
    path('download_template/', views.download_template, name='download_template'),
    path('new_application/',views.add_application,name="new_application"),
]