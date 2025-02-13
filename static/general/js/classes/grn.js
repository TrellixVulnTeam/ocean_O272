

class Grn {
    SaveNew(){

        swal_success('SAVING GRN TRANSACTION')
        /*
        * VALIDATE GRN ENTRIES
        * MAKE SURE SUPPLIER IS SELECTED AND EXIST
        * VALIDATE LOCATION
        * VALID TYPE AND REFERENCE
        * VALIDATE TAX COMPONENT
        * VALIDATE REMARKS*/

        let tran_list = $('#tbody tr').length
        let supplier,loc,type,ref,taxable_amt,tax_amt,tot_amt,remark,err_count,err_msg
        supplier = $('#supplier').val()
        loc = $('#loc').val()
        type = $('#type').val()
        ref = $('#ref').val()
        taxable_amt = $('#invoice_amt').val()
        tax_amt = $('#tax_amt').val()
        tot_amt = $('#tot_amt').val()
        remark = $('#remark').val()
        err_msg = ""
        err_count = 0

        if(
            supplier.length < 1 ||
            loc.length < 1 ||
            type.length < 1 ||
            ref.length < 1 ||
            taxable_amt.length < 1 ||
            tax_amt.length < 1 ||
            tot_amt.length < 1 ||
            remark.length < 1
        ){
            err_count ++
            err_msg = "Invalid HEater"
        }

        if(err_count > 0)
        {
            swal_response('','',err_msg)
        } else  {

            if(tran_list > 0)
            {
                let tran_err_count = 0
                let tran_err_msg = 'error%% '
                for (let i = 1; i <= tran_list ; i++) {

                        let row,barcode,descr,packing,pack_descr,tran_qty,un_cost,tot_cost
                        row = $(`#row_${i}`)
                        barcode = $(`#barcode_${i}`)
                        descr = $(`#descr_${i}`)
                        packing = $(`#packing_${i}`)
                        pack_descr = $(`#pack_descr_${i}`)
                        tran_qty = $(`#tran_qty_${i}`)
                        un_cost = $(`#un_cost_${i}`)
                        tot_cost = $(`#tot_cost_${i}`)

                        if(tran_qty.val() <= 0){
                        tran_err_count ++
                        tran_err_msg += `<p>Line ${i} quantity is invalid</p>`
                        }
                        if(un_cost.val() <= 0){
                            tran_err_count ++
                            tran_err_msg += `<p>Line ${i} unit cost is invalid</p>`
                        }
                        if(tot_cost.val() <= 0){
                            tran_err_count ++
                            tran_err_msg += `<p>Line ${i} total cost is invalid</p>`
                        }

                }

                if(tran_err_count <= 0){
                    let data = {
                'supplier':supplier,
                'location':loc,
                'type':type,
                'taxable_amt':taxable_amt,
                'tax_amt':tax_amt,
                'tot_amt':tot_amt,
                'remark':remark,
                'taxable':$('#taxable').val(),
                'owner':$('#mypk').val(),
                'ref':$('#ref').val()
            }
                    console.table(data)

                    let status,message,grnhd = JSON.parse(apiv2('grn','newHd',data))
                    status = grnhd['status']
                    message = grnhd['message']
                    console.table(grnhd)
                    if(status === 200)
                    {
                        
                        let entry_no = message
                        for (let i = 1; i <= tran_list ; i++) {

                            let row, barcode, descr, packing, pack_descr, tran_qty, un_cost, tot_cost,pack_qty
                            row = $(`#row_${i}`)
                            barcode = $(`#barcode_${i}`)
                            descr = $(`#descr_${i}`)
                            packing = $(`#packing_${i}`)
                            pack_descr = $(`#pack_descr_${i}`)
                            tran_qty = $(`#tran_qty_${i}`)
                            un_cost = $(`#un_cost_${i}`)
                            tot_cost = $(`#tot_cost_${i}`)
                            pack_qty = $(`#pack_qty_${i}`)

                            let data = {
                                "entry_no":entry_no,
                                "line":i,
                                "barcode":barcode.text(),
                                "packing":packing.val(),
                                'pack_qty':pack_qty.val(),
                                "qty":tran_qty.val(),
                                "total_qty":packing.val() *  tran_qty.val() ,
                                "un_cost":un_cost.val(),
                                "tot_cost":tot_cost.val()
                            }

                            let exe = apiv2('grn','newTran',data)
                            console.table(data)
                            console.table(JSON.parse(exe))


                        }
                        // location.href = '/inventory/grn/'

                    } else {
                        error_handler(`error%%${message}`)
                    }

                }






            } else {
                error_handler(`error%%Cannot save empty document`)
            }

        }



        // start validations
        // let supp_req = apiv2('')

    }

    retrievePo(po_number){
        let po_req = apiv2('po','get',{"entry":po_number})
        let po_response = JSON.parse(po_req)

        if(po_response['status'] === 200)
        {
            // there is response
            let response = po_response['message']
            let header,cost,trans
            header = response['header']
            console.table(header)
            cost = response['cost']
            trans = response['trans']

            // load header
            $('#type').val("PO")
            $('#ref').val(header['entry_no'])
            $('#invoice_amt').val(cost['taxable_amt'] - cost['tax_amt'])
            $('#tot_amt').val(cost['taxable_amt'])
            $('#tax_amt').val(cost['tax_amt'])

            let  tax_htm= ''
            if(cost['taxable'] === 1)
            {
                tax_htm= `<option value="1" selected>YES</option><option value="0">NO</option>`
            } else {
                tax_htm = `<option value="1" >YES</option><option selected value="0">NO</option>`
            }
            $('#taxable').html(tax_htm)

            // get suppliers
            let sup_req,sup_resp,supp_stat,supp_msg
            sup_req = apiv2('general','getSuppliers','none')
            sup_resp = JSON.parse(sup_req)
            supp_stat = sup_resp['status']
            supp_msg = sup_resp['message']
            let sopt = ''
            if(supp_stat === 200)
            {
                // there is suppler
                for (let i = 0; i < supp_msg.length; i++) {
                    let s = supp_msg[i]
                    console.table(s)
                    let company = s['company']

                    let pk = s['pk']

                    if(header['supp_pk'] === pk)
                    {
                        sopt += `<option selected value="${pk}" >${company}</option>`
                    } else
                    {
                        sopt += `<option value="${pk}" >${company}</option>`
                    }
                }
            }
            $('#supplier').html(sopt)

            // location
            let loc_req,loc_res,loc_stat,loc_msg,loc_row = ''
            loc_req = apiv2('general','getLocs','nonw')
            loc_res = JSON.parse(loc_req)
            loc_stat = loc_res['status']
            loc_msg = loc_res['message']

            if(loc_stat === 200)
            {
                // there is suppler
                for (let i = 0; i < loc_msg.length; i++) {
                    let s = loc_msg[i]
                    console.table(s)
                    let loc_code = s['code']
                    let pk = s['pk']
                    let descr = s['descr']

                    if(header['loc_code'] === descr)
                    {
                        loc_row += `<option selected value="${pk}" >${loc_code} - ${descr}</option>`
                    } else
                    {
                        loc_row += `<option value="${pk}" >${loc_code} - ${descr}</option>`
                    }
                }
            }

            $('#loc').html(loc_row)
            $('#remark').val(header['remark'])

            // fill trans FillTranList
            let tran_count, tran_list
            tran_count = trans['count']
            tran_list = trans['transactions']
            if(tran_count > 0)
            {
                // load grn trans from po
                console.log("TRAN LIST")
                console.table(tran_list)
                let row = ''
                for (let i = 0; i < tran_list.length; i++)
                {
                    let tran = tran_list[i]
                    let line,packing,barcode,descr,qty,tot_cost,un_cost,pack_code,pack_qty,packing_option,pack_pk
                    line = tran['line']

                    packing = tran['packing']
                    pack_pk = packing['pk']
                    pack_code = packing['pack_code']
                    pack_qty = packing['pack_qty']

                    barcode = tran['product_barcode']
                    descr = tran['product_descr']
                    qty = tran['qty']
                    tot_cost = tran['tot_cost']
                    un_cost = tran['un_cost']
                    let sn = line

                    // get product details
                    let product = JSON.parse(apiv2('product','get_product',{'barcode':barcode}))['message']
                    let prod_pack = product['prod_pack']
                    let packoptions = ''

                    console.table(product)

                    for (let j = 0; j < prod_pack.length; j++) {
                        let p_pack = prod_pack[j]
                        let p_pk = p_pack['pk']
                        let p_code = p_pack['pack_code']
                        let p_type = p_pack['pack_type']


                        if (p_pk === pack_pk)
                        {
                            packoptions += `<option selected value="${p_pk}">${p_type} - ${p_code}</option>`
                        } else
                        {
                            packoptions += `<option value="${p_pk}">${p_type} - ${p_code}</option>`
                        }

                    }

                    console.log('product details')
                    console.table(prod_pack)
                    console.log('product details')


                    // get packing
                    packing_option = ''


                    row += `<tr id="row_${sn}">
                                <td>${sn} <input type="hidden" id="pack_${sn}" value=""> </td>
                                <td id="barcode_${sn}">${barcode}</td>
                                <td id="descr_${sn}">${descr}</td>
                                <td><select onchange="productMaster.TranPack(this.value,${sn});productMaster.TranRowCalc('${sn}')" name="" id="packing_${sn}" class="anton-form-tool form-control-sm">${packoptions}</select></td>
                                <td><input type="number" readonly style="width: 50px" value="${pack_qty}" id="pack_qty_${sn}"></td>
                                <td><input type="number" onchange="productMaster.TranRowCalc('${sn}')" style="width: 100px" class="anton-form-tool form-control-sm" id="tran_qty_${sn}" value="${qty}"></td>
                                
                                <td><input type="number" onchange="productMaster.TranRowCalc('${sn}')" style="width: 100px"  class="anton-form-tool form-control-sm" id="un_cost_${sn}" value="${un_cost}"></td>
                                <td><input readonly type="number" style="width: 100px"  class="anton-form-tool form-control-sm" id="tot_cost_${sn}" value="${tot_cost}"></td>
                            </tr>`

                }

                $('#tbody').html(row)

            } else
            {
                swal_response('THERE IS NO FISH')
            }






            // console.table(response)
            $('#po').modal('hide')
        } else
        {
            // wrong response

        }
    }

}

const grn = new Grn()