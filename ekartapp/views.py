from django.shortcuts import render,redirect
from .models import Product,Orders,OrderUpdate,Contact
from math import ceil
from django.contrib import messages
import ast
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
# Create your views here.
def index(request):
    allProds=[]
    catprods=Product.objects.values('category','id')
    cats={item['category'] for item in catprods}
    print(cats)
    for cat in cats:
        prod=Product.objects.filter(category=cat)
        n=len(prod)
        nSlides=n//4 + ceil((n/4)-(n//4))
        print(nSlides)
        allProds.append([prod,range(1,nSlides),nSlides])
    
    print(allProds)
    params={"allProds":allProds}
    return render(request,'index.html',params)

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method=="POST":
        name=request.POST.get("name")
        email=request.POST.get("email")
        desc=request.POST.get("desc")
        pnumber=request.POST.get("pnumber")
        print(name,email)
        myquery=Contact(name=name,email=email,desc=desc,phonenumber=pnumber)
        myquery.save()
        messages.info(request,"we will get back to you soon..")
        return render(request,"contact.html")
    return render(request,'contact.html')

def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('/authapp/login') 
    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amt')
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2','')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')  

        # logic to update stock and save profit amount in database table Order
        profit=[]
        dataitems=ast.literal_eval(items_json)
        for i in dataitems.values():
            # print(i[0],i[1],i[2]) stock,productname,amount
            getProductname=Product.objects.get(product_name=i[1])
            profitamount=int(i[2])*int(i[0])-int(getProductname.actualprice)*int(i[0])
            profit.append(profitamount)
            getProductname.stock=getProductname.stock-int(i[0])
            getProductname.save()
        
        # final order the items
        profit=sum(profit)
        Order = Orders(items_json=items_json,name=name,amount=amount, email=email, address1=address1,address2=address2,city=city,state=state,zip_code=zip_code,phone=phone,profit=profit)
        Order.save()        
        update = OrderUpdate(order_id=Order.order_id,update_des="the order has been placed")
        update.save()

        #update the order id payment status in database orders tables 
        id = Order.order_id
        oid=str(id)
        filter1= Orders.objects.filter(order_id=oid)
        for post1 in filter1:
                post1.oid=oid
                post1.amountpaid="CASH ON DELIVERY"
                post1.paymentstatus="UN PAID"
                post1.save()

        # email_subject="Ordered Placed Guvi"
        # message=f' Hello {name}\nYour Ordered is Placed with order id {oid}\n\n\nOrdered Items are\n{items_json}\n\nTotal Amount to be Paid {amount}\n we will soon deliver your ordered on below address\n\nAddress:\n{address1}\n{address2}\n{city}\n{state}\n{zip_code}\n{phone}\n\nYou can track your orders at http://127.0.0.1:8000/profile'
        # email_message = EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email])
        # email_message.send()
        messages.success(request,"Order is placed....")
        return redirect('/profile')
    return render(request,'checkout.html')

def profile(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('/authapp/login') 
    current_user=request.user.username
    print(current_user)
    items=Orders.objects.filter(email=current_user)
    rid=""
    for i in items:
        myid=i.oid
        rid=myid

    try:
        status=OrderUpdate.objects.filter(order_id=int(rid))
        context={"items":items,"status":status}
        return render(request,"profile.html",context)

    except:
        pass
    return render(request,"profile.html")

def search(request):
    query=request.GET['search']
 
    if len(query)>78:
        allProds=Product.objects.none()
    else:
        allProdsTitle=Product.objects.filter(product_name__icontains=query)
        allProdsContent1=Product.objects.filter(category__icontains=query)
        allProdsContent2=Product.objects.filter(desc__icontains=query)
        allProds=allProdsTitle.union(allProdsContent1).union(allProdsContent2)

    if allProds.count()== 0:
        messages.warning(request,"No Search Results")

    # print(allProds)
    params={'allProds':allProds,'query':query}   
    return render(request,"search.html",params)

def cancelorder(request,id):
    d=Orders.objects.get(order_id=id) 
    u=OrderUpdate.objects.get(order_id=id) 
    d.delete()
    u.delete()
    messages.error(request,"Order Cancelled Successfully")
    return redirect("/profile")


@login_required
@permission_required('ekartapp.read_product', raise_exception=True)
def dashboard(request):
    prods=Product.objects.all()
    totalProducts=len(prods)
    context={"prods":prods,"total":totalProducts}
    return render(request,"dashboard.html",context)

@login_required 
@permission_required('ekartapp.add_product', raise_exception=True)
def addProduct(request):
    if request.method=="POST":
        pname=request.POST.get('pname') 
        pimage=request.FILES['pimage']
        pcategory=request.POST.get('pcategory') 
        pscategory=request.POST.get('pscategory') 
        pdesc=request.POST.get('pdesc') 
        pprice=request.POST.get('pprice')
        pstock=request.POST.get('pstock')
        papprice=request.POST.get('paprice')
        query= Product(product_name=pname,category=pcategory,subcategory=pscategory,price=pprice,desc=pdesc,image=pimage,stock=pstock,actualprice=papprice)
        query.save()
        messages.info(request," Added Product Successfully")   
        return redirect("/dashboard")
    return render(request,"addProduct.html")


@login_required 
@permission_required('ekartapp.delete_product', raise_exception=True)
def deleteProduct(request,id):   
    p=Product.objects.get(id=id) 
    p.delete()
    messages.warning(request,"Product Deleted Successfully")
    return redirect('/dashboard')

@login_required 
@permission_required('ekartapp.edit_product', raise_exception=True)
def editProduct(request,id):   
    d=Product.objects.get(id=id)
    context={"d":d}
    if request.method=="POST":    
        try:
            pname=request.POST.get('pname') 
            pimage=request.FILES['pimage']
            pcategory=request.POST.get('pcategory') 
            pscategory=request.POST.get('pscategory') 
            pdesc=request.POST.get('pdesc') 
            pprice=request.POST.get('pprice')
            pstock=request.POST.get('pstock')
            papprice=request.POST.get('paprice')
            edit=Product.objects.get(id=id) 
            edit.product_name=pname
            edit.category=pcategory
            edit.subcategory=pscategory
            edit.price=pprice
            edit.desc=pdesc
            edit.image=pimage
            edit.stock=pstock
            edit.actualprice=papprice
            edit.save()
        except:
            pname=request.POST.get('pname') 
            pcategory=request.POST.get('pcategory') 
            pscategory=request.POST.get('pscategory') 
            pdesc=request.POST.get('pdesc') 
            pprice=request.POST.get('pprice')
            pstock=request.POST.get('pstock')
            papprice=request.POST.get('paprice')
            edit=Product.objects.get(id=id) 
            edit.product_name=pname
            edit.category=pcategory
            edit.subcategory=pscategory
            edit.price=pprice
            edit.desc=pdesc
            edit.stock=pstock
            edit.actualprice=papprice
            edit.save()
            # pimage=request.POST.get('pimagelink')
        
        messages.info(request," Updated Product Successfully....")   
        return redirect("/dashboard")
    return render(request,"editProduct.html",context)
