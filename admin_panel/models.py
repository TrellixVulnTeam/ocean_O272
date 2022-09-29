from django.contrib.auth.models import User
from django.db import models
from community.models import questions, QuestionTags
from blog.models import Providers
from django.db.models import Sum



# Create your models here.

class LoggedIssue(models.Model):
    issue = models.CharField(unique=True, max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=0)

    def log_count(self):  # log count
        return LoggedIssue.objects.filter(issue=self.issue).count()

    def domain(self):  # tags
        # from community.models import QuestionTags
        quest =  questions.objects.get(uni=self.issue)
        return quest.domain

    def owner(self):  # owner name
        owner_detail = questions.objects.get(uni=self.issue)
        owner_id = owner_detail.owner
        return User.objects.get(pk=owner_id)

    def title(self):
        return questions.objects.get(uni=self.issue).title

    def date_reported(self):
        return questions.objects.get(uni=self.issue).created_at

    def stat(self):
        if self.status == 0:
            return "PENDING"
        elif self.status == 1:
            return "TO SEND"
        else:
            return f"UNKNOWN ({self.status})"


class LoggedIssueTransaction(models.Model):
    issue = models.CharField(max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField(default=0)
    title = models.CharField(max_length=100)
    body = models.TextField()

    def owner(self):
        return User.objects.get(pk=self.created_by)


class PendingEscalations(models.Model):
    provider = models.CharField(max_length=5)
    issue = models.CharField(unique=True, max_length=100)

    def quest(self):
        return questions.objects.get(uni=self.issue)



class TaskHD(models.Model): ## task model
    entry_uni = models.TextField()
    type = models.TextField()
    ref = models.TextField()
    owner = models.IntegerField(default=0)
    title = models.TextField()
    description = models.TextField()
    added_on = models.DateTimeField(auto_now=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=0)
    domain = models.ForeignKey('community.tags', on_delete=models.CASCADE)
    def owner_name(self):
        return User.objects.get(pk=self.owner).username

    def question(self):
        return questions.object.get(uni=self.ref)

    def provider(self):
        domain =  self.domain.provider
        return domain


# task transactions
class TaskTrans(models.Model):
    entry_uni = models.TextField()
    tran_title = models.TextField()
    tran_descr = models.TextField()
    created_on = models.DateTimeField(auto_now=True)
    owner = models.IntegerField(default=0)
    def owner_name(self):
        return User.objects.get(pk=self.owner)

# email models
class Emails(models.Model):
    sent_from = models.TextField()
    sent_to = models.TextField()
    subject = models.TextField()
    body = models.TextField()
    email_type = models.TextField()
    ref = models.TextField()
    scheduled_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(default=0)
    status_message = models.TextField(default='Scheduled')
    sent_on = models.DateTimeField(auto_now=True)


class Sales(models.Model):
    loc = models.CharField(max_length=3)
    mech_no = models.TextField()
    gross_sales = models.DecimalField(max_digits=60, decimal_places=2)
    tax = models.DecimalField(max_digits=60, decimal_places=2)
    discount = models.DecimalField(max_digits=60, decimal_places=2)
    net_sales = models.DecimalField(max_digits=60, decimal_places=2)
    day = models.TextField()
    place = models.TextField()
    loc_desc = models.TextField()


class NotificationGroups(models.Model):
    full_name = models.TextField()
    email_addr = models.TextField()
    mobile_number = models.TextField()
    group = models.ForeignKey('EmailGroup', on_delete=models.CASCADE,default=0)

class EmailGroup(models.Model):
    group_name = models.TextField()
    def_domain = models.ForeignKey('community.tags', on_delete=models.CASCADE)
    description = models.TextField()
    created_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)

    def clients(self):
        return NotificationGroups.objects.filter(group=self.pk).count()



# tax modal
class TaxMaster(models.Model):
    tax_code = models.CharField(unique=True,max_length=2)
    tax_description = models.TextField()
    tax_rate = models.DecimalField(max_digits=3, decimal_places=2)
    created_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=1)

class BankAccounts(models.Model):
    acct_name = models.CharField(unique=True,max_length=20)
    acct_serial = models.CharField(unique=True,max_length=12)
    acct_descr = models.TextField()
    created_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=1)

class SuppMaster(models.Model):
    company = models.TextField()
    contact_person = models.TextField(default='NULL')
    purch_group = models.TextField()
    origin = models.TextField()
    email = models.TextField()
    mobile = models.TextField()
    city = models.TextField()
    street = models.TextField()
    taxable = models.IntegerField(default=1)
    bank_acct = models.ForeignKey('BankAccounts',on_delete=models.CASCADE)
    created_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=1)

    def location(self):
        return f"{self.origin} - {self.city}"

class ProductGroup(models.Model):
    descr = models.TextField()

    created_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=1)

    def subgroups(self):
        return ProductGroupSub.objects.filter(group=self)
class ProductGroupSub(models.Model):
    group = models.ForeignKey('ProductGroup',on_delete=models.CASCADE)
    descr = models.TextField()

    created_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=1)

class ProductMaster(models.Model):
    group = models.ForeignKey('ProductGroup', on_delete=models.CASCADE)
    sub_group = models.ForeignKey('ProductGroupSub', on_delete=models.CASCADE)
    tax = models.ForeignKey('TaxMaster',on_delete=models.CASCADE)
    descr = models.TextField()
    shrt_descr = models.TextField()
    barcode = models.CharField(unique=True, max_length=255)
    supplier = models.ForeignKey('SuppMaster',on_delete=models.CASCADE)
    prod_img = models.FileField(upload_to=f'static/general/img/products/')


    created_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=1)

    def stock(self):
        if ProductTrans.objects.filter(product=self).aggregate(Sum('tran_qty'))['tran_qty__sum'] is None:
            return 0
        else:
            return ProductTrans.objects.filter(product=self).aggregate(Sum('tran_qty'))['tran_qty__sum']

class PackingMaster(models.Model):
    code = models.CharField(max_length=3,unique=True)
    descr = models.TextField()

    created_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=1)

class ProductPacking(models.Model):
    product = models.ForeignKey('ProductMaster',on_delete=models.CASCADE)
    packing_un = models.ForeignKey('PackingMaster',on_delete=models.CASCADE)
    pack_qty = models.DecimalField(max_digits=60, decimal_places=2)
    packing_type = models.CharField(default='U',max_length=1)

    created_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=1)

class ProductTrans(models.Model):
    doc = models.CharField(max_length=2)
    doc_ref = models.TextField()
    product = models.ForeignKey('ProductMaster',on_delete=models.CASCADE)
    tran_qty = models.DecimalField(max_digits=65, decimal_places=2)

    created_by = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)



