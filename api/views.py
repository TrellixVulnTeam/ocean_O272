import hashlib
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from fpdf import FPDF

from .ApiClass import *

from admin_panel.models import Notifications, AuthToken, Locations, SuppMaster, ProductMaster, ProductTrans, \
    ProductPacking
import json

from inventory.models import PoHd, PoTran, PriceCenter, GrnHd, DocAppr, GrnTran

# Create your views here.
api_response = {
    'status': 505,
    'response': 'PROCEDURE ERROR'
}


def console(str=''):
    print()
    print(str)
    print()


def get_notification(user):
    if User.objects.filter(pk=user).count() == 1:
        notifications = Notifications.objects.filter(owner=User.objects.get(pk=user))
        if notifications.count() > 0:
            api_response['status'] = 200
            read = Notifications.objects.filter(owner=User.objects.get(pk=user), read=1)
            my_notif = [

            ]
            not_read = Notifications.objects.filter(owner=User.objects.get(pk=user), read=0)
            my_notifications = Notifications.objects.filter(owner=User.objects.get(pk=user)).order_by('-pk')[:5]

            for my_n in my_notifications:
                # 1 = success, 2 = information, 3 = warning, 4 = errpr
                icon = ''
                n_type = my_n.type
                if n_type == 1:
                    icon = 'bi-check-circle text-success'
                elif n_type == 2:
                    icon = 'bi-info-circle text-info'
                elif n_type == 3:
                    icon = 'bi-exclamation-circle text-warning'
                else:
                    icon = 'bi-exclamation-circle text-danger'

                this_x = {
                    'title': my_n.title,
                    'type': my_n.type,
                    'descr': my_n.descr,
                    'status': my_n.read,
                    'icon': icon
                }
                my_notif.append(this_x)

            message = {
                'r_count': read.count(),
                'n_read': not_read.count(),
                'notifications': my_notif
            }
            api_response['response'] = message
        else:
            api_response['response'] = 'There is None'
        return JsonResponse(api_response, safe=False)
    else:
        return HttpResponse("USER NOT FOUND")


@csrf_exempt
def api_call(request, module, crud):
    global f_name, api_body
    response = {
        'status': 505,
        'message': "No Module "
    }
    try:
        api_body = json.loads(request.body)
    except Exception as e:
        pass

    if module == 'notif':
        user = api_body['user']
        return get_notification(user=user)

    elif module == 'auth':  # authentication model queried
        api_token = crud  # api access token

        token_filter = AuthToken.objects.filter(token=api_token)  # filter for token existence

        if token_filter.count() == 1:  # if there is token
            token_d = AuthToken.objects.get(token=api_token)
            username = token_d.user.username
            password = token_d.user.password

            # login
            user = authenticate(request, username=username, password=password)

            try:
                # check if user is valid
                if hasattr(user, 'is_active'):
                    auth_login(request, user)
                    # Redirect to a success page.
                    return redirect('home')
                else:
                    messages.error(request,
                                   f"There is an error logging in, please check your credentials again or contact "
                                   f"Administrator")
                    return redirect('login')

            except Exception as e:
                messages.error(request, f"There was an error {e}")
                return redirect('login')

        else:
            return HttpResponse('INVALID TOKEN')

    # purchase order
    elif module == 'po':
        # save new po header
        if crud == 'newHd':
            data = api_body
            location = data['location']
            supplier = data['supplier']
            remarks = data['remarks']
            owner = User.objects.get(pk=data['owner'])
            taxable = data['taxable']

            response['status'] = 200
            response['message'] = data

            # save po hd
            try:
                PoHd(loc=Locations.objects.get(pk=location), supplier=SuppMaster.objects.get(pk=supplier),
                     remark=remarks, created_by=owner, taxable=taxable).save()
                response['message'] = PoHd.objects.all().last().pk
                response['status'] = 200

            except Exception as e:
                response['status'] = 505
                response['message'] = str(e)

        # save new po transaction
        elif crud == 'newTran':
            data = api_body
            entry_no = data['entry_no']

            line = data['line']

            barcode = data['barcode']
            if ProductMaster.objects.filter(barcode=barcode).exists():

                product = ProductMaster.objects.get(barcode=barcode)

                packing = ProductPacking.objects.get(pk=data['packing'])
                qty = data['qty']
                total_qty = data['total_qty']
                un_cost = data['un_cost']
                tot_cost = data['tot_cost']
                pack_qty = data['pack_qty']

                try:
                    PoTran(entry_no=PoHd.objects.get(pk=entry_no), line=line, product=product, packing=packing,
                           qty=qty, total_qty=total_qty, un_cost=un_cost, tot_cost=tot_cost, pack_qty=pack_qty).save()
                    response['status'] = 200
                    response['message'] = "Data Saved"

                except Exception as e:
                    response['status'] = 505
                    response['message'] = str(e)

            else:
                response['message'] = "Product Does Not Exist"

        # get po transaction
        elif crud == 'get':
            data = api_body
            entry = data['entry']

            meg = {}

            if PoHd.objects.filter(pk=entry).exists():
                # if po exist
                hd = PoHd.objects.get(pk=entry)

                header = {
                    'header': {
                        'entry_no': hd.pk,
                        'loc_code': hd.loc.code,
                        'loc_descr': hd.loc.descr,
                        'supp_pk': hd.supplier.pk,
                        'supp_descr': hd.supplier.company,
                        'remark': hd.remark,
                        'entry_date': hd.created_on,
                        'owner': hd.created_by.first_name,
                        'pk': hd.pk
                    }
                }

                # get trans
                trans = {
                    'trans': {
                        'count': 0,
                        'transactions': []
                    }
                }

                if PoTran.objects.filter(entry_no=entry).exists():

                    transactions = PoTran.objects.filter(entry_no=entry)
                    trans['trans']['count'] = transactions.count()

                    for transaction in transactions:
                        p_packing = {
                            'pk': transaction.packing.pk,
                            'pack_qty': transaction.packing.pack_qty,
                            'packing_type': transaction.packing.packing_type,
                            'code': transaction.packing.packing_un.code,
                            'descr': transaction.packing.packing_un.descr,

                        }
                        this_trans = {
                            'line': transaction.line,
                            'product_descr': transaction.product.descr,
                            'product_barcode': transaction.product.barcode,
                            'packing': p_packing,
                            'qty': transaction.qty,
                            'total_qty': transaction.total_qty,
                            'un_cost': transaction.un_cost,
                            'tot_cost': transaction.tot_cost
                        }
                        trans['trans']['transactions'].append(this_trans)

                        # navigators
                        next_count = PoHd.objects.filter(pk__gt=hd.pk).count()
                        prev_count = PoHd.objects.filter(pk__lt=hd.pk).count()

                        if prev_count > 0:
                            prev = PoHd.objects.all().filter(pk__lt=hd.pk)
                            for x in prev:
                                prev_p = str(x.pk)
                        else:
                            prev_p = 0

                        if next_count > 0:
                            next_po = PoHd.objects.all().filter(pk__gt=hd.pk)[:1]
                            for y in next_po:
                                next_p = str(y.pk)
                        else:
                            next_p = 0

                        nav = {
                            'nav': {
                                'status': hd.status,
                                'next_count': next_count,
                                'next_id': next_p,
                                'prev_count': prev_count,
                                'prev_id': prev_p
                            }
                        }

                        cost = {
                            'cost': {
                                'taxable': hd.taxable,
                                'taxable_amt': PoTran.objects.filter(entry_no=hd.pk).aggregate(Sum('tot_cost'))[
                                    'tot_cost__sum'],
                                'tax_nhis': 0.00,
                                'tax_gfund': 0.00,
                                'tax_covid': 0.00,
                                'tax_vat': 0.00,
                                'tax_amt': 0.00,
                                'levies': 0.00
                            }
                        }

                        if cost['cost']['taxable'] == 1:
                            # calculate taxesx
                            taxable_amt = cost['cost']['taxable_amt']
                            cost['cost']['tax_covid'] = round(Decimal(taxable_amt) * Decimal(0.01), 2)
                            cost['cost']['tax_nhis'] = round(Decimal(taxable_amt) * Decimal(0.025), 2)
                            cost['cost']['tax_gfund'] = round(Decimal(taxable_amt) * Decimal(0.025), 2)

                            levies = cost['cost']['tax_covid'] + cost['cost']['tax_nhis'] + cost['cost']['tax_gfund']
                            cost['cost']['levies'] = levies
                            new_tot_amt = taxable_amt + levies

                            cost['cost']['tax_vat'] = round(Decimal(new_tot_amt) * Decimal(0.125), 2)
                            cost['cost']['tax_amt'] = round(levies + cost['cost']['tax_vat'], 2)

                        meg.update(header)
                        meg.update(trans)
                        meg.update(nav)
                        meg.update(cost)

                        response['status'] = 200
                        response['message'] = meg

                else:
                    response['status'] = 404
                    response['message'] = "No Transactions"




            else:
                # if no po, return 404 and response message
                response['status'] = 404
                response['message'] = "Po Entry Not Found"

    # grn
    elif module == 'grn':
        if crud == 'newHd':

            try:
                supplier = api_body['supplier']
                location = api_body['location']
                type = api_body['type']
                taxable_amt = api_body['taxable_amt']
                tax_amt = api_body['tax_amt']
                tot_amt = api_body['tot_amt']
                remark = api_body['remark']
                owner = User.objects.get(pk=api_body['owner'])
                tax = api_body['taxable']
                ref = api_body['ref']
                GrnHd(type=type, supplier=SuppMaster.objects.get(pk=supplier),
                      loc=Locations.objects.get(pk=location), taxable=tax, created_by=owner,ref=ref).save()
                response['message'] = GrnHd.objects.all().last().pk
                response['status'] = 200
            except Exception as e:
                response['status'] = 505
                response['message'] = str(e)

        if crud == 'newTran':
            data = api_body
            entry_no = data['entry_no']

            line = data['line']

            barcode = data['barcode']
            if ProductMaster.objects.filter(barcode=barcode).exists():

                product = ProductMaster.objects.get(barcode=barcode)

                packing = ProductPacking.objects.get(pk=data['packing'])
                qty = data['qty']
                total_qty = data['total_qty']
                un_cost = data['un_cost']
                tot_cost = data['tot_cost']
                pack_qty = data['pack_qty']

                try:
                    GrnTran(entry_no=GrnHd.objects.get(pk=entry_no), line=line, product=product, packing=packing,
                           qty=qty, total_qty=total_qty, un_cost=un_cost, tot_cost=tot_cost, pack_qty=pack_qty).save()
                    response['status'] = 200
                    response['message'] = "Data Saved"

                except Exception as e:
                    response['status'] = 505
                    response['message'] = str(e)

            else:
                response['message'] = "Product Does Not Exist"



    # products master
    elif module == 'product':
        if crud == 'get_product':
            barcode = api_body['barcode']

            if ProductMaster.objects.filter(barcode=barcode).exists():
                response['status'] = 200
                pd = ProductMaster.objects.get(barcode=barcode)
                stock = ProductTrans.objects.filter(product=pd.pk).aggregate(Sum('tran_qty'))['tran_qty__sum']
                if PriceCenter.objects.filter(product=pd.pk, price_type=0).exists():
                    cost_price = PriceCenter.objects.get(product=pd.pk, price_type=0).price
                else:
                    cost_price = 0.00
                if PriceCenter.objects.filter(product=pd.pk, price_type=1).exists():
                    issue_price = PriceCenter.objects.get(product=pd.pk, price_type=1).price
                else:
                    issue_price = 0.00

                prod_pack = []

                if ProductPacking.objects.filter(product=pd).exists():
                    pack = ProductPacking.objects.filter(product=pd)
                    for p in pack:
                        this_p = {
                            'pack_type': p.packing_type,
                            'pack_qty': p.pack_qty,
                            'pack_code': p.packing_un.code,
                            'pack_descr': p.packing_un.descr,
                            'pk': p.pk
                        }
                        prod_pack.append(this_p)
                        print(this_p)

                prod_grp = {
                    'group': pd.group.descr, 'sub_group': pd.sub_group.descr,
                }

                product = {
                    # group details
                    'group': prod_grp,

                    # tax details
                    'tax': {'tax_code': pd.tax.tax_code, 'tax_descr': pd.tax.tax_description,
                            'tax_rate': pd.tax.tax_rate, },

                    # supplier details
                    'supplier': {'sup_company': pd.supplier.company, 'sup_pk': pd.supplier.pk, },

                    # product details
                    'prod_details': {'barcode': pd.barcode, 'prod_descr': pd.descr, 'prod_sht_descr': pd.shrt_descr,
                                     'prod_img': pd.prod_img.url, 'pk': pd.pk, },

                    # others
                    'others': {'stock': stock, 'cost_price': cost_price, 'issue_price': issue_price, },

                    # packing
                    'prod_pack': prod_pack

                }
                response['message'] = product

            else:
                response['status'] = 505
                response['message'] = "Product Does Not Exist"

    # general
    elif module == 'general':
        if crud == 'print':
            doc = api_body['doc']
            entry_no = api_body['entry_no']

            if doc == 'po':
                res = GetPo(entry_no)
                status = res['status']
                message = res['message']

                if status == 200:

                    trans = message['trans']['transactions']
                    header = message['header']
                    prices = message['cost']
                    p_status = message['p_status']

                    tax = 'NO'
                    if prices['taxable'] == 1:
                        tax = "YES"

                    pdf = FPDF('L', 'mm', 'A4')
                    pdf.add_page()
                    pdf.set_margin(10)
                    # header

                    pdf.set_font('Arial', 'BU', 25)
                    pdf.cell(280, 5, "PURCHASE ORDER", 0, 1, 'C')
                    pdf.ln(10)
                    pdf.set_font('Arial', 'B', 10)
                    pdf.cell(30, 5, "Entry : ", 0, 0, 'L')
                    pdf.set_font('Arial', '', 8)
                    pdf.cell(150, 5, header['entry_no'], 0, 0, 'L')

                    pdf.set_font('Arial', 'B', 10)
                    pdf.cell(35, 5, "Date : ", 0, 0, 'L')
                    pdf.set_font('Arial', '', 8)
                    pdf.cell(30, 5, str(header['entry_date']), 0, 1, 'L')

                    pdf.set_font('Arial', 'B', 10)
                    pdf.cell(30, 5, "Created By : ", 0, 0, 'L')
                    pdf.set_font('Arial', '', 8)
                    pdf.cell(150, 5, header['owner'], 0, 0, 'L')

                    pdf.set_font('Arial', 'B', 10)
                    pdf.cell(35, 5, "Location : ", 0, 0, 'L')
                    pdf.set_font('Arial', '', 8)
                    pdf.cell(30, 5, header['loc_descr'], 0, 1, 'L')

                    pdf.set_font('Arial', 'B', 10)
                    pdf.cell(30, 5, "Supplier : ", 0, 0, 'L')
                    pdf.set_font('Arial', '', 8)
                    pdf.cell(150, 5, header['supp_descr'], 0, 0, 'L')

                    pdf.set_font('Arial', 'B', 10)
                    pdf.cell(35, 5, "Taxable : ", 0, 0, 'L')
                    pdf.set_font('Arial', '', 8)
                    pdf.cell(30, 5, tax, 0, 1, 'L')

                    pdf.set_font('Arial', 'B', 10)
                    pdf.cell(30, 5, "Remarks : ", 0, 0, 'L')
                    pdf.set_font('Arial', '', 8)
                    pdf.cell(30, 5, header['remark'], 0, 0, 'L')

                    pdf.cell(120, 5, '', 0, 0, 'L')
                    pdf.set_font('Arial', 'B', 10)
                    pdf.cell(35, 5, "Inv Amount : ", 0, 0, 'L')
                    pdf.set_font('Arial', '', 8)
                    pdf.cell(30, 5, str(prices['taxable_amt']), 0, 1, 'L')

                    pdf.cell(180, 5, '', 0, 0, 'L')
                    pdf.set_font('Arial', 'B', 10)
                    pdf.cell(35, 5, "Tax Amount : ", 0, 0, 'L')
                    pdf.set_font('Arial', '', 8)
                    pdf.cell(30, 5, str(prices['tax_amt']), 0, 1, 'L')

                    pdf.cell(180, 5, '', 0, 0, 'L')
                    pdf.set_font('Arial', 'B', 10)
                    pdf.cell(35, 5, "Total Amount : ", 0, 0, 'L')
                    pdf.set_font('Arial', '', 8)
                    pdf.cell(30, 5, str(Decimal(prices['tax_amt']) + Decimal(prices['taxable_amt'])), 0, 1, 'L')

                    pdf.ln(10)

                    pdf.set_font('Arial', 'B', 8)
                    # table head
                    pdf.cell(10, 5, "Line", 1, 0, 'L')
                    pdf.cell(60, 5, "Barcode", 1, 0, 'L')
                    pdf.cell(70, 5, "Description", 1, 0, 'L')
                    pdf.cell(25, 5, "Packing", 1, 0, 'L')
                    pdf.cell(25, 5, "Pack Quantity", 1, 0, 'L')
                    pdf.cell(20, 5, "Quantity", 1, 0, 'L')
                    pdf.cell(30, 5, "Cost", 1, 0, 'L')
                    pdf.cell(40, 5, "Total Cost", 1, 1, 'L')

                    pdf.set_font('Arial', '', 6)
                    for transaction in trans:
                        pdf.cell(10, 5, f"{transaction['line']}", 1, 0, 'L')
                        pdf.cell(60, 5, f"{transaction['product_barcode']}", 1, 0, 'L')
                        pdf.cell(70, 5, f"{transaction['product_descr']}", 1, 0, 'L')
                        pdf.cell(25, 5, f"{transaction['packing']['code']}", 1, 0, 'L')
                        pdf.cell(25, 5, f"{transaction['packing']['tran_pack_qty']}", 1, 0, 'L')
                        pdf.cell(20, 5, f"{transaction['qty']}", 1, 0, 'L')
                        pdf.cell(30, 5, f"{transaction['un_cost']}", 1, 0, 'L')
                        pdf.cell(40, 5, f"{transaction['tot_cost']}", 1, 1, 'L')

                    # auth
                    pdf.ln(20)
                    pdf.set_left_margin(55)
                    pdf.set_font('Arial', 'I', 10)
                    pdf.cell(40, 10, f"{header['owner']}", 1, 0, 'C')

                    pdf.set_left_margin(205)
                    pdf.cell(40, 10, f"{p_status['approved_by']}", 1, 1, 'C')

                    pdf.set_font('Arial', 'B', 12)
                    pdf.set_left_margin(55)
                    pdf.cell(40, 10, f"Prepared By", 0, 0, 'C')

                    pdf.set_left_margin(205)
                    pdf.cell(40, 10, f"Approved By", 0, 1, 'C')

                    md_mix = f"{status}{message['header']['entry_no']}"
                    hash_object = hashlib.md5(md_mix.encode())
                    f_name = hash_object.hexdigest()
                    f_name = header['entry_no']

                    pdf.output(f'static/general/docs/{f_name}.pdf', 'F')

                    resp = {
                        'status': 200,
                        'file': f'/static/general/docs/{f_name}.pdf'
                    }

                else:
                    resp = res
                return JsonResponse(resp, safe=False)

        # get suppliers
        elif crud == 'getSuppliers':
            s_r = []
            suppliers = SuppMaster.objects.all()
            for supp in suppliers:
                this_sup = {
                    'company': supp.company,
                    'contact_person': supp.contact_person,
                    'purch_group': supp.purch_group,
                    'email': supp.email,
                    'mobile': supp.mobile,
                    'pk': supp.pk,

                }
                s_r.append(this_sup)

            response['message'] = s_r
            response['status'] = 200

        # get locations
        elif crud == 'getLocs':
            l_r = []
            locations = Locations.objects.all()
            for location in locations:
                this_loc = {
                    'pk':location.pk,
                    'code': location.code,
                    'descr': location.descr
                }
                l_r.append(this_loc)
            response['message'] = l_r
            response['status'] = 200

        # get product packing
        elif crud == 'prodPack':
            pk = api_body['pk']

            if ProductPacking.objects.filter(pk=pk).count() == 1:
                packing = ProductPacking.objects.get(pk=pk)
                response['status'] = 200
                response['message'] = {
                    'product': {
                        'barcode': packing.product.barcode
                    },
                    'packing_un': {
                        'code': packing.packing_un.code, 'descr': packing.packing_un.descr
                    },
                    'pack_qty': packing.pack_qty,
                    'packing_type': packing.packing_type
                }
            else:
                response['status'] = 404
                response['message'] = "Packing Not Found"

    elif module == 'doc_approve':
        document = api_body['doc']
        entry = api_body['entry']
        user = api_body['user']
        doc_found = 0
        doc_setup = {
            'grn': GrnHd.objects.filter(pk=entry),
            'po': PoHd.objects.filter(pk=entry)
        }

        if document in doc_setup:

            doc = doc_setup[document]
            if doc.count() == 1:
                response['status'] = 200
                for docx in doc:
                    doc_key = docx.pk
                    if DocAppr.objects.filter(doc_type=document, entry_no=doc_key).exists():
                        response['message'] = "Document already approved"
                    else:

                        DocAppr(entry_no=doc_key, doc_type=document,
                                approved_by=User.objects.get(pk=user)).save()  # approval
                        # transaction
                        docx.status = 1
                        docx.save()  # make approved

                        response['message'] = "Approved"

            else:
                response['status'] = 404
                response['message'] = f"{document} entry {entry} not found: COUNT {doc.count()}"




        else:
            response['message'] = f"UNKNOWN DOCUMENT TYPE {document}"

    return JsonResponse(response, safe=False)


def index(request):
    return HttpResponse("NO OPRION")
