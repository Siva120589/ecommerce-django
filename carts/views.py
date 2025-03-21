from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
# Create your views here.


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)  # get the product
    # If the user is authenticated
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            # color = request.POST['color']
            # size = request.POST['size']
            # return HttpResponse(color)
            # print(color, size)

            for item in request.POST:
                key = item
                value = request.POST[key]
                print(key, value)

                try:
                    variation = Variation.objects.get(
                        product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                    # print(product_variation)
                except:
                    pass

        cart_item_exists = CartItem.objects.filter(
            product=product, user=current_user).exists()
        if cart_item_exists:
            print("user_cart_item_exists")
            cart_item = CartItem.objects.filter(
                product=product, user=current_user)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            print(ex_var_list)
            if product_variation in ex_var_list:
                print("user_product_variation_already_exists")
                print(ex_var_list)
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                cart_item = CartItem.objects.get(product=product, id=item_id)
                cart_item.quantity += 1
                cart_item.save()

            else:
                print("user_product_variation_does not_exists")
                item = CartItem.objects.create(
                    product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            print("user_cart_item_does_not_exists")
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user,
            )
            if len(product_variation) > 0:
                print("user_product_variation exist")
                print(product_variation)
                print(len(product_variation))
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
                cart_item.save()
            else:
                print("user_product_variation does not exist")
        # return HttpResponse(cart_item.quantity)
        # exit()
        return redirect('cart')
    else:
        print("if it is not authenticated or logged in")
        product_variation = []
        if request.method == 'POST':
            # color = request.POST['color']
            # size = request.POST['size']
            # return HttpResponse(color)
            # print(color, size)

            for item in request.POST:
                key = item
                value = request.POST[key]
                print(key, value)

                try:
                    variation = Variation.objects.get(
                        product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                    # print(product_variation)
                except:
                    pass

        try:
            # get the cart using the cart_id present in the session
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()

        cart_item_exists = CartItem.objects.filter(
            product=product, cart=cart).exists()
        if cart_item_exists:
            print("cart_item_exists")
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            print(ex_var_list)
            if product_variation in ex_var_list:
                print("product_variation_already_exists")
                print(ex_var_list)
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                cart_item = CartItem.objects.get(product=product, id=item_id)
                cart_item.quantity += 1
                cart_item.save()

            else:
                print("product_variation_does not_exists")
                item = CartItem.objects.create(
                    product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            print("cart_item_does_not_exists")
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )
            if len(product_variation) > 0:
                print("product_variation exist")
                print(product_variation)
                print(len(product_variation))
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
                cart_item.save()
            else:
                print("product_variation does not exist")
        # return HttpResponse(cart_item.quantity)
        # exit()
        return redirect('cart')


def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(
                product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(
                product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(
            product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(
            product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(
                user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass  # just ignore

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)


@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(
                user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass  # just ignore

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/checkout.html', context)
