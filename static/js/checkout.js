$(document).ready(function () {
    $("#payWithRazorpay").click(function (e) {
        console.log("im g=here");
        e.preventDefault();

        var first_name = $("[name='first_name']").val();
        var last_name = $("[name='last_name']").val();
        var email = $("[name='email']").val();
        var address = $("[name='addressSelected']").val();
        var phone = $("[name='phone']").val();
        var address_line_1 = $("[name='address_line_1']").val();
        var address_line_2 = $("[name='address_line_2']").val();
        var city = $("[name='city']").val();
        var state = $("[name='state']").val();
        var country = $("[name='country']").val();
        var zip_code = $("[name='zip_code']").val();
        var token = $("[name='csrfmiddlewaretoken']").val();
        var grand_total = $("[name='grand_total']").val();
        var couponCode = $("[name='couponCode']").val();
        var couponDiscount = $("[name='couponDiscount']").val();
        var amountToBePaid = $("[name='amountToBePaid']").val();

        if (
            first_name == "" ||
            last_name == "" ||
            email == "" ||
            phone == "" ||
            address_line_1 == "" ||
            city == "" ||
            state == "" ||
            country == "" || 
            zip_code == ""

        ) {
            swal("alert", "All fields are mandatory", "error");
            return false;
        } else {
            $.ajax({
                method: "GET",
                url: "/order/proceed_to_pay/",
                contentType: "application/json",
                success: function (response) {
                    console.log(response, amountToBePaid);
                    console.log(homely.settings.API_KEY)
                    var options = {
                        
                        key: homely.settings.API_KEY, 
                        // Enter the Key ID generated from the Dashboard
                        amount: response.amountToBePaid * 100, //response.total_price *100 , // Amount is in currency subunits. Default currency is INR. Hence, 50000 refers to 50000 paise
                        currency: "INR",
                        name: "Rahul K",
                        description: "Thank you",
                        image: "https://info.homely.mx/images/logos/homely.png",
                        handler: function (responseb) {
                       
                            console.log("56");
                            data = {
                                'first_name': first_name,
                                'last_name': last_name,
                                'email': email,
                                'phone': phone,
                                'address_line_1': address_line_1,
                                'address_line_2': address_line_2,
                                'city': city,
                                'state': state,
                                'addressSelected': address,
                                'country': country,
                                'zip_code': zip_code,
                                'payment_method': "Paid by Razorpay",
                                'payment_id': responseb.razorpay_payment_id,
                                'csrfmiddlewaretoken': token,
                                'amountToBePaid': amountToBePaid,
                                'couponCode': couponCode,
                                'couponDiscount': couponDiscount,
                                'grand_total': grand_total

                            };
                            console.log(grand_total)
                            $.ajax({
                                method: "POST",
                                url: "/order/place_order/",
                                data: data,
                                success: function (responsec) {
                                    swal("Congratulations!", responsec.status, "success").then(
                                        (value) => {
                                            console.log("93");
                                            window.location.href =
                                                "/order/order-complete/" +
                                                "?payment_id=" +
                                                data.payment_id;
                                        }
                                    );

                                },
                            });
                            console.log("why not"); 
                        },
                        prefill: {

                            email: email,
                            contact: phone,
                        },
                        notes: {
                            address: "Homely Furnitures",
                        },
                        theme: {
                            color: "#3399cc",
                        },
                    };
                    var rzp1 = new Razorpay(options);
                    rzp1.open();
                },
            });
        }
    });
})