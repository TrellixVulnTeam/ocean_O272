from django import forms

from admin_panel.models import ProductMaster, ProductPacking, Locations, TicketHd, Files


class NewProduct(forms.ModelForm):
    class Meta:
        model = ProductMaster
        exclude = ['created_on', 'edited_on', 'status', 'created_by','price_center']


class NewProductPacking(forms.ModelForm):
    class Meta:
        model = ProductPacking
        exclude = ['created_on', 'edited_on', 'status', 'created_by']


class NewLocation(forms.ModelForm):
    class Meta:
        model = Locations
        exclude = ['created_on', 'edited_on', 'status', 'created_by']


class SearchForm(forms.Form):
    query = forms.CharField(max_length=200)


class NewArticle(forms.Form):
    page_title = forms.CharField(max_length=200)
    article_desc = forms.CharField(max_length=5000)
    meta = forms.CharField(max_length=100)
    post_img = forms.ImageField()


class EdArticle(forms.Form):
    page_title = forms.CharField(max_length=200)
    article_desc = forms.CharField(max_length=5000)
    meta = forms.CharField(max_length=100)
    uni = forms.CharField(max_length=100)


class LogIn(forms.Form):
    username = forms.CharField(max_length=200)
    password = forms.CharField(max_length=200)
    next = forms.CharField(max_length=200)


class SignUp(forms.Form):
    first_name = forms.CharField(max_length=200)
    last_name = forms.CharField(max_length=200)
    email = forms.EmailField()
    password = forms.CharField(max_length=200)
    mobile = forms.CharField(max_length=200)


class NewTicket(forms.ModelForm):
    class Meta:
        model = TicketHd
        exclude = ['created_on', 'edited_on', 'status']


class UploadFIle(forms.ModelForm):
    class Meta:
        model = Files
        exclude = ['created_on', 'edited_on']
