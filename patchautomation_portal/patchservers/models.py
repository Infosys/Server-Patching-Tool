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

from django.db import models
# Create your models here.

class Instance(models.Model):
    id = models.AutoField(primary_key=True)
    lot = models.TextField()
    appid = models.TextField()
    appname = models.TextField()


        
class ServerPatchDetails(models.Model):
    id = models.IntegerField(primary_key=True)
    uploadid = models.TextField(blank=True, null=True)
    runid = models.TextField(blank=True, null=True)
    hostname = models.TextField(blank=True, null=True)
    #ipaddress = models.CharField(max_length=255)
    state = models.TextField(blank=True, null=True)
    action = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    defaultuser = models.TextField(blank=True, null=True)
    defaultpass = models.TextField(blank=True, null=True)
    osmake= models.TextField(blank=True, null=True)
    osversion= models.TextField(blank=True, null=True)
    latestpatch=models.TextField(blank=True, null=True)   
    #update_date = models.DateTimeField(default= timezone.now)
    instance = models.ForeignKey(Instance, on_delete=models.DO_NOTHING,null=True)
    created_date = models.DateTimeField(auto_now_add=True)    
    update_date = models.DateTimeField(auto_now=True)
    uptime = models.TextField(blank=True, null=True)
   
class ServerPatchDetailsAudit(models.Model):
    id = models.IntegerField(primary_key=True)
    event = models.TextField(blank=True, null=True)
    uploadid = models.TextField(blank=True, null=True)
    runid = models.TextField(blank=True, null=True)
    hostname = models.TextField(blank=True, null=True)
    #ipaddress = models.CharField(max_length=255)
    state = models.TextField(blank=True, null=True)
    action = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    defaultuser = models.TextField(blank=True, null=True)
    defaultpass = models.TextField(blank=True, null=True)
    osmake= models.TextField(blank=True, null=True)
    osversion= models.TextField(blank=True, null=True)
    latestpatch=models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)    
    update_date = models.DateTimeField(auto_now=True)
    #update_date = models.DateTimeField(default=timezone.now)  
    instance= models.TextField(blank=True, null=True)

class ServerDetailsAudit(models.Model):
    id = models.IntegerField(primary_key=True)
    event = models.TextField(blank=True, null=True)
    uploadid = models.TextField(blank=True, null=True)
    runid = models.TextField(blank=True, null=True)
    hostname = models.TextField(blank=True, null=True)
    #ipaddress = models.CharField(max_length=255)
    state = models.TextField(blank=True, null=True)
    action = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    crref=models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)    
    update_date = models.DateTimeField(auto_now=True)
    #update_date = models.DateTimeField(default=timezone.now)  
    instance= models.TextField(blank=True, null=True)

class SkippedServers(models.Model):
    id = models.IntegerField(primary_key=True)
    uploadid = models.TextField(blank=True, null=True)
    hostname = models.TextField(blank=True, null=True)
    old_uploadid = models.TextField(blank=True, null=True)

class Upload_runid(models.Model):
    id = models.IntegerField(primary_key=True)
    uploadid = models.TextField(blank=True, null=True)
    runid = models.TextField(blank=True, null=True)
    action= models.TextField(blank=True, null=True)
    
class Uploadmaster(models.Model):
    id = models.AutoField(primary_key=True) 
    uploadid = models.TextField(blank=True, null=True)
    uploadedby  = models.TextField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
