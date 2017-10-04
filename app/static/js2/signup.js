
$(document).ready(function(){
    $('.datepicker').pickadate({
        selectYears: 100,
        max: new Date(new Date().setFullYear(new Date().getFullYear() - 13 ))
    });
    orgSignUp.setupGooglePlaces()
    orgSignUp.doSignUpStartUp()

    var uploadCoverImage = function() {
        orgSignUp.uploadCoverImage(this,'createOrgCover')
    }

    var uploadLogoImage = function() {
        orgSignUp.uploadLogoImage(this,'createOrgLogo')
    }

    $("#createOrgCoverImage").off("change", uploadCoverImage)
    $("#createOrgCoverImage").on("change", uploadCoverImage)
    $("#createOrgLogoImage").off("change", uploadLogoImage)
    $("#createOrgLogoImage").on("change", uploadLogoImage)

    $("#navSupport").click(function() {
        orgUtil.showSupportModal()
    })

    $("#navContact").click(function() {
        orgUtil.showSupportModal()
    })

    $(document).ready(function() {
        $('input#input_text, textarea#textarea1').characterCounter();
    });
});


var OrgSignUp = function() {
    this.streetAddress = {}
    this.logoImageUrl = ""
    this.coverImageUrl = ""
}

OrgSignUp.prototype.doLogout = function() {
    var self = this
    if(orgSignIn.isValidAccessToken()) {
        api.deleteCookie('accessToken')
    }
    localOrgData = {}
    window.location.href = "/org.html"
}

OrgSignUp.prototype.doSignUpStartUp = function() {
    var self = this
    if(!orgSignIn.isValidAccessToken()) {
        $("#navSignOut").hide()
        return
    }

    orgSignIn.getOrgUserData(
        function() {
            if(localOrgData.user.status == 5) { //ORG_ACCOUNT_CREATED
                if(!localOrgData.user.emailVerified) {
                    self.showEmailVerify()
                }
                else {
                    self.showOrgInfo()
                }
            }
            else if(localOrgData.user.status == 6) { //ORG_ACCOUNT_INFO_APPLIED
                self.showBankAccountAdd()
            }
            else if(localOrgData.user.status == 7) { //ORG_ACCOUNT_BANK_ACCOUNT_LINKED
                self.showOrgVerification()
            }
            else if(localOrgData.user.status == 8) { //ORG_VERIFICATION_DONE
                self.finishScreen()
            }
            else if(localOrgData.user.status == 0) { //LIVE
                window.location.href = "/org.html"
            }
        },
        function(error) {
            toastr.error(genericError)
        }
    )
}

OrgSignUp.prototype.setupGooglePlaces = function() {
    var self = this
    var autocomplete = new google.maps.places.Autocomplete($("#createOrgAddress")[0], {country: "us", types: ["address"]})
    google.maps.event.addListener(autocomplete, 'place_changed', function() {
        var place = autocomplete.getPlace();
        place.address_components.forEach(function(address) {
            self.streetAddress[address.types[0]] = address.short_name
        })
         self.streetAddress = {
             "street1"   : self.streetAddress.street_number + " " + self.streetAddress.route,
             "city"      : self.streetAddress.locality,
             "zip"       : self.streetAddress.postal_code,
             "state"     : self.streetAddress.administrative_area_level_1,
             "country"   : self.streetAddress.country
         }
    });
}

//OrgSignUp.prototype.showCreateAccount = function() {
//
//}

OrgSignUp.prototype.showEmailVerify = function() {
    var self = this
    $("#navSignOut").show()
    self.verifyEmailScreen()
    $("#currEmail").text(localOrgData.user.email)
    $("#accountCreateStepTwo").show();
    $("#accountCreateStepOne").hide();
}

OrgSignUp.prototype.showOrgInfo = function() {
    var self = this
    $("#navSignOut").show()
    $('#accountCreate').collapse('hide')
    $('#orgInfo').collapse('show')
}

OrgSignUp.prototype.showBankAccountAdd = function() {
    var self = this
    $("#navSignOut").show()
    $('#accountCreate').collapse('hide')
    $('#bankInfo').collapse('show')
    $("#orgInfo").hide();
}

OrgSignUp.prototype.showOrgVerification = function() {
    $("#navSignOut").show()
    $('#accountCreate').collapse('hide')
    $('#bankInfo').collapse('hide')
    $("#verifyOrganization").collapse('show');
}

OrgSignUp.prototype.finishScreen = function() {
    $("#navSignOut").show()
    $('#accountCreate').collapse('hide')
    $('#verifyOrganization').collapse('hide')
    $('#accountCreateComplete').collapse('show')
}


OrgSignUp.prototype.startEmailVerify = function() { //STEP ONE
    var self = this
    self.startSignUp()
    self.verifyEmailScreen()
}

OrgSignUp.prototype.verifyOrgInfo = function() {
    var self = this
    self.moreOrgInfo()
}

OrgSignUp.prototype.verifyMoreOrgInfo = function() {
    var self = this
    self.checkMoreOrgInfo()
}


OrgSignUp.prototype.startSignUp = function() { //SCREEN 1
    var self = this
    var email = utils.getElementValueTrimmed('createOrgEmail')
    var name = utils.getElementValueTrimmed('createOrgName')
    var pass = utils.getElementValueTrimmed('createOrgPassword')
    var repeat_pass = utils.getElementValueTrimmed('createOrgRPassword')
    orgUtil.resetInputError()
    toastr.remove()
    if(!utils.validateEmail(email)) {
        orgUtil.setInputError("createOrgEmail","Invalid email")
        return
    }

    if(name == "") {
        orgUtil.setInputError("createOrgName","Name cannot be empty")
        return
    }
    if(pass == "") {
        orgUtil.setInputError("createOrgPassword","Password cannot be empty")

        return
    }
    if(utils.checkPassStrength(pass) == "weak" && pass != "" && pass == repeat_pass) {
        orgUtil.setInputError("createOrgPassword","Weak password, please add numbers or special characters to it")
        return
    }
    if(pass != repeat_pass) {
        orgUtil.setInputError("createOrgRPassword","Passwords don't match")
        return
    }
    if($("#createTOSBox").prop('checked') == false) {
          toastr.error("Please Accept PayBee's TOS")
        return
    }


    var reqData = {
        'p' : JSON.stringify({
            'email': email,
            'password': pass,
            'name': name,
            }
        )
    }
    api.makeApiRequest({
        type: "orgSignUp",
        data: reqData,
        success: function(respData) {
            if(typeof(respData) != 'undefined' && typeof(respData.access_token != 'undefined')) {
                orgSignIn.setAccessTokenCookie(respData.access_token)
                orgSignIn.getOrgUserData(
                    function() {
                        $("#currEmail").text(localOrgData.user.email)
                        $("#accountCreateStepTwo").show();
                        $("#accountCreateStepOne").hide();
                    },
                    function(error) {
                        toastr.warning("rippity rip")
                    }
                )
            }
            else {
                toastr.error("Something went wrong in respData function")
            }
        },
        error: function(error) {
            if(error.errorCode == "UserAlreadyExist") {
                orgUtil.setInputError("createOrgEmail","Account with this Email already exist, please try signing in")
                $("#accountExistsLoginRow").show()
            }
            else if(error.errorCode == "InvalidEmail") {
                 orgUtil.setInputError("createOrgEmail","Invalid Email Id")
            }
            else {
                toastr.error(genericError)
            }
        }
    })
}


OrgSignUp.prototype.verifyEmailScreen = function(){
    var self = this
    $("#editEmail").off("click")
    $("#editEmail").click(function() {
        $("#changeEmailModel").appendTo('html').modal('show');
        orgUtil.setInputVal("changeNewEmail", localOrgData.user.email)
        $("#changeNewEmailButton").off("click")
        $("#changeNewEmailButton").click(function() {
            var email = utils.getElementValueTrimmed("changeNewEmail") || ""
            if(email == "") {
                orgUtil.setInputError("changeNewEmail","Empty email")
            }
            if(utils.validateEmail(email) == false) {
                if(!utils.validateEmail(email)) {
                    orgUtil.setInputError("changeNewEmail","Invalid email")
                }
                return false
            }

            if(email.toLowerCase() == localOrgData.user.email) {
                orgUtil.setInputError("changeNewEmail","No change")
                return false
            }

            var params = {"email": email}
            api.makeApiRequest({
                type: "orgUpdate",
                data: {'p' : JSON.stringify(params),"access_token": orgSignIn.getAccessToken()},
                success: function(response) {
                    orgSignIn.getOrgUserData(
                        function(){
                            $("#currEmail").text(localOrgData.user.email)
                            $("#changeEmailModel").modal('hide');
                            toastr.success("Email sent, check your inbox")
                        },
                        function() {
                            toastr.error(genericError)
                        }
                    )
                },
                error: function(error) {
                    if(error.errorCode == "InvalidEmail") {
                        orgUtil.setInputError("changeNewEmail","Invalid email")
                    } else if(error.errorCode == "UserAlreadyExist") {
                        orgUtil.setInputError("changeNewEmail","Email already in use")
                    } else {
                        toastr.error(genericError)
                    }
                    return false
                },
                expired: function() { orgSignIn.onInValidAccessToken() },
                extend: function() { orgSignIn.extendCookieLife() }
            })
            return false
        })
    })

    $("#resendVEmail").off("click")
    $("#resendVEmail").click(function() {
        api.makeApiRequest({
            type: "verifyEmail",
            data: {"access_token": orgSignIn.getAccessToken()},
            success: function(response) {
                toastr.success("Email verification has been resent to" + localOrgData.user.email)
            },
            error: function(error) {
                toastr.error("Error in sending verification email, try again later")
            },
            expired: function() { orgSignIn.onInValidAccessToken() },
            extend: function() { orgSignIn.extendCookieLife() }
        })
    })

    $("#nextVEmail").off("click")
    $("#nextVEmail").click(function(){
        orgSignIn.getOrgUserData(
            function() {
                if(localOrgData.user.emailVerified) {
                    $('#accountCreate').collapse('hide')
                    $('#orgInfo').collapse('show')
                }
                else {
                    toastr.error("Email Not Verified Yet")
                    return
                }
            },
            function(error) {
                toastr.warning("Something went wrong")
                return
            }
        )
    })
} //SCREEN 2

OrgSignUp.prototype.uploadCoverImage = function(selectedImage, imageDisplay) {
    var self = this
    orgUtil.uploadImage({
        onSuccess: function(imageUrl) {
            self.coverImageUrl = imageUrl
        },
        onError: function(error) {
            if(error.errorMessage != ""
            && error.errorMessage != undefined) {
                toastr.error(error.errorMessage)
            }
            else {
                toastr.error(genericError)
            }
        },
        access_token: orgSignIn.getAccessToken(),
        selectedImage: selectedImage,
        imageDisplay: imageDisplay,
        imageUsage:  "accountCoverImage"
    })
}

OrgSignUp.prototype.uploadLogoImage = function(selectedImage, imageDisplay) {
    var self = this
    orgUtil.uploadImage({
        onSuccess: function(imageUrl) {
            self.logoImageUrl = imageUrl
        },
        onError: function(error) {
            if(error.errorMessage != ""
            && error.errorMessage != undefined) {
                toastr.error(error.errorMessage)
            }
            else {
                toastr.error(genericError)
            }
        },
        access_token: orgSignIn.getAccessToken(),
        selectedImage: selectedImage,
        imageDisplay: imageDisplay,
        imageUsage:  "accountLogo"
    })
}

OrgSignUp.prototype.moreOrgInfo = function() {
    var self = this

    var handle = utils.getElementValueTrimmed('createOrgHandle')
    var website = utils.getElementValueTrimmed('createOrgWebsite')
    var purpose = utils.getElementValueTrimmed('createOrgMission')
    var description = utils.getElementValueTrimmed('createOrgDescription')

    orgUtil.resetInputError()

    if(handle == "") {
        orgUtil.setInputError("createOrgHandle","Handle cannot be empty")
        return
    }

    if(handle.length > 12) {
        orgUtil.setInputError("createOrgHandle","Handle too long, 12 or less")
        return
    }


    var handleRegex = /^[a-zA-Z][a-zA-Z0-9_\-]+/
    if(!handleRegex.test(handle)){
        orgUtil.setInputError("createOrgHandle","Handle can only contain a-z, 0-9, _ and -, must start with letter")
        return
    }
    
    if(website == "") {
        orgUtil.setInputError("createOrgWebsite","Invalid Website")
        return
    }

    if(purpose == "") {
        orgUtil.setInputError("createOrgMission","Purpose cannot be empty")
        return
    }


    var params = {"handle": handle, "purpose": purpose,"url" : website,"desc": description, "imageUrl": self.coverImageUrl , "logoUrl": self.logoImageUrl }
     $('#orgPostSignupError').hide()
     api.makeApiRequest({
         type: "orgAddInfo",
         data: {'p' : JSON.stringify(params),"access_token": orgSignIn.getAccessToken()},
         success: function(resultObj) {
             $('#bankInfo').collapse('show')
             $("#orgInfo").hide();
         },
         error: function(error) {
             switch(error.errorCode) {
                 case "HandleAlreadyExist":
                     orgUtil.setInputError("createOrgHandle","Handle already taken, choose another")
                     break
                 case "OrgPurposeTooLong":
                      orgUtil.setInputError("createOrgMission","Purpose too long, maxlength: 127")
                      break
                 case "OrgDescTooLong":
                     orgUtil.setInputError("createOrgDescription","Description too long")
                     break
                 case "InvalidHandle":
                     orgUtil.setInputError("createOrgHandle","Invalid Handle")
                     break
                 case "EmptyHandle":
                     orgUtil.setInputError("createOrgHandle","Handle cannot be empty")
                     break
                 case "HandleTooLong":
                     orgUtil.setInputError("createOrgHandle","Handle max length should be 12")
                     break
                 default:
                     toastr.error("Something went wrong")
                     break
             }
         },
         expired: function() { orgSignIn.onInValidAccessToken() },
         extend: function() { orgSignIn.extendCookieLife() }
     })

} //SCREEN 3

OrgSignUp.prototype.addBankAccount = function() {
    var linkHandler = Plaid.create({
        selectAccount: true,
        env: api.getPlaidEnv(),
        clientName: 'PayBee Inc.',
        key: '4f83c65b3165d55570c3f52e504129',
        product: 'auth',
        onLoad: function() {
            // The Link module finished loading.
        },
        onSuccess: function(public_token, metadata) {
            var reqData = {
                'plaid_token': public_token,
                'plaid_account_id': metadata.account_id,
                'access_token': orgSignIn.getAccessToken()
            }

            api.makeApiRequest({
                type: "orgAddBankAccount",
                data: reqData,
                success: function(respData) {
                    $('#bankInfo').collapse('hide')
                    $("#verifyOrganization").collapse('show');
                },
                error: function(error) {
                    toastr.error("Error in adding bank account")
                },
                expired: function() { orgSignIn.onInValidAccessToken() },
                extend: function() { orgSignIn.extendCookieLife() }
            })
        },
        onExit: function() {
            console.log("exit")
        },
    });
    linkHandler.open();
}

OrgSignUp.prototype.showRoutingDialogue =function() {
    var self = this

    orgUtil.resetInputError("routing-number")
    orgUtil.resetInputVal("routing-number")

    orgUtil.resetInputError("account-number")
    orgUtil.resetInputVal("account-number")

    $('#bankAccountConnect').modal('show');
    $("#addBankRoutingButton").off("click")
    $("#addBankRoutingButton").click(function(e) {
        self.addBankAccountRouting()
    })
}

OrgSignUp.prototype.addBankAccountRouting = function() {
    Stripe.setPublishableKey(api.getStripePublishableKey())
    var routingNumber = $("#routing-number").val()
    var accountNumber = $("#account-number").val()

    if(!Stripe.bankAccount.validateRoutingNumber(routingNumber, 'US')) {
        orgUtil.setInputError("routing-number", "Invalid Routing Number")
        return
    }
    if(!Stripe.bankAccount.validateAccountNumber(accountNumber, 'US')) {
        orgUtil.setInputError("account-number", "Invalid Account Number")
        return
    }

    Stripe.bankAccount.createToken(
    {
      country: "US",
      currency: "USD",
      routing_number: $("#routing-number").val(),
      account_number: $("#account-number").val(),
    },
    function stripeResponseHandler(status, response) {
        if (response.error) {
            toastr.error(response.error.message + "try again")
        }
        else {
            api.makeApiRequest({
                type: "orgAddBankAccount",
                data: {
                    'bankAccountToken': response.id,
                    'access_token': orgSignIn.getAccessToken()
                },
                success: function(respData) {
                    $('#bankAccountConnect').modal('hide');
                    $('#bankInfo').collapse('hide')
                    $("#verifyOrganization").collapse('show');
                },
                error: function(error) {
                    toastr.error("Error in adding account")
                },
                expired: function() { orgSignIn.onInValidAccessToken() },
                extend: function() { orgSignIn.extendCookieLife() }
            })
        }
    });
}

OrgSignUp.prototype.showCardReader = function() {
    var $form = $('#payment-form');
    var linkButton = $("#linkAccountDC")
    var cardNumberInput = $("#cardNumber")
    var expiryInput     = $("#cardExpiry")
    var cvcInput        = $("#cardCVC")
    var paymentErrorRow = $("#payment-errors")
    var paymentError    = $("#paymentErrorText")

    var showError = function(errorStr) {
        paymentError.text(errorStr)
        paymentErrorRow.show()
    }

    var resetError = function() {
        paymentError.text("")
        paymentErrorRow.hide()
    }

    var resetForm = function() {
        orgUtil.resetInputVal("cardNumber")
        orgUtil.resetInputVal("cardExpiry")
        orgUtil.resetInputVal("cardCVC")
    }

    resetForm()
    resetError()

    $("#linkAccountDC").on('click', function(e) {
        e.preventDefault()
        if (!validator.form()) {
            return;
        }

        linkButton.html('Validating <i class="fa fa-spinner fa-pulse"></i>').prop('disabled', true)
        Stripe.setPublishableKey(api.getStripePublishableKey())

        var expiry = expiryInput.payment('cardExpiryVal');
        var ccData = {
            number: cardNumberInput.val().replace(/\s/g,''),
            cvc: cvcInput.val(),
            currency: "usd",
            exp_month: expiry.month,
            exp_year: expiry.year
        };

        Stripe.card.createToken(ccData, function stripeResponseHandler(status, response) {
            if (response.error) {
                linkButton.html('Try again').prop('disabled', false)
                showError(response.error.message)
            } else {
                linkButton.html('Processing <i class="fa fa-spinner fa-pulse"></i>');
                resetError()
                if(response.card.funding != "debit") {
                    linkButton.html('Try again').prop('disabled', false);
                    showError("Not a debit card")
//                    orgUtil.setInputError("cardNumber", "Not a debit card")
                    return
                }

                api.makeApiRequest({
                    type: "orgAddBankAccount",
                    data: {'debitCardToken': response.id,'access_token': orgSignIn.getAccessToken()},
                    success: function(respData) {
                        $('#cardReader').modal('hide');
                        $('#bankInfo').collapse('hide')
                        $("#verifyOrganization").collapse('show');
                    },
                    error: function(error) {
                        linkButton.html('There was a problem').removeClass('success').addClass('error');
                        showError('Try refreshing the page and trying again.');
                    },
                    expired: function() { orgSignIn.onInValidAccessToken() },
                    extend: function() { orgSignIn.extendCookieLife() }
                })
            }
        });
    })

    /* Fancy restrictive input formatting via jQuery.payment library*/
    cardNumberInput.payment('formatCardNumber');
    cvcInput.payment('formatCardCVC');
    expiryInput.payment('formatCardExpiry');

    /* Form validation using Stripe client-side validation helpers */
    jQuery.validator.addMethod("cardNumber", function(value, element) {
        return this.optional(element) || Stripe.card.validateCardNumber(value);
    }, "Please specify a valid credit card number.");

    jQuery.validator.addMethod("cardExpiry", function(value, element) {
        /* Parsing month/year uses jQuery.payment library */
        value = $.payment.cardExpiryVal(value);
        return this.optional(element) || Stripe.card.validateExpiry(value.month, value.year);
    }, "Invalid expiration date.");

    jQuery.validator.addMethod("cardCVC", function(value, element) {
        return this.optional(element) || Stripe.card.validateCVC(value);
    }, "Invalid CVC.");

    var validator = $form.validate({
        rules: {
            cardNumber: {
                required: true,
                cardNumber: true
            },
            cardExpiry: {
                required: true,
                cardExpiry: true
            },
            cardCVC: {
                required: true,
                cardCVC: true
            }
        },
        highlight: function(element) {
            $(element).closest('.form-control').removeClass('success').addClass('error');
        },
        unhighlight: function(element) {
            $(element).closest('.form-control').removeClass('error').addClass('success');
        },
        errorPlacement: function(error, element) {
            $(element).closest('.form-group').append(error);
        }
    });

    var paymentFormReady = function() {
        if (cardNumberInput.hasClass("success") &&
            expiryInput.hasClass("success") &&
            cvcInput.val().length > 1) {
            return true;
        } else {
            return false;
        }
    }

    linkButton.prop('disabled', true);
    var readyInterval = setInterval(function() {
        if (paymentFormReady()) {
            linkButton.prop('disabled', false);
            clearInterval(readyInterval);
        }
    }, 250);

    $('#cardReader').modal('show');
}

OrgSignUp.prototype.checkMoreOrgInfo = function() {
    var self = this
    var address = utils.getElementValueTrimmed('createOrgAddress')
    var ein = utils.getElementValueTrimmed('createOrgEIN')
    var repFirstName = utils.getElementValueTrimmed('createOrgRepFN')
    var repLastName = utils.getElementValueTrimmed('createOrgRepLN')
    var repSSN = utils.getElementValueTrimmed('createOrgRepSSN')

    orgUtil.resetInputError()

    if(address == "") {
        orgUtil.setInputError("createOrgAddress","Address cannot be empty")
        return
    }

    if(ein == "") {
            orgUtil.setInputError("createOrgEIN","Tax ID not entered")
            return
        }

    if(repFirstName == "") {
        orgUtil.setInputError("createOrgRepFN","Representative name cannot be empty")
        return
    }

    if(repLastName == "") {
        orgUtil.setInputError("createOrgRepLN","Representative name cannot be empty")
        return
    }
    if(repSSN == "") {
        orgUtil.setInputError("createOrgRepSSN","SSN cannot be empty")
        return
    }
    else if(repSSN.length < 4) {
         orgUtil.setInputError("createOrgRepSSN","Not enough digits")
         return
     }
    else if(repSSN.length > 4) {
         orgUtil.setInputError("createOrgRepSSN","Too many digits")
         return
    }

     var DOBDateObj = $("#createOrgRepDOB").data("pickadate").get("select")

     if(DOBDateObj == null) {
         orgUtil.setInputError("createOrgRepDOB", "Please select date of birth")
         return
     }

     var reqData = {
             "access_token": orgSignIn.getAccessToken(),
             "p" : JSON.stringify({
                 "addressLine1"  : self.streetAddress.street1,
                 "addressLine2"  : "",
                 "addressCity"   : self.streetAddress.city,
                 "addressState"  : self.streetAddress.state,
                 "addressZipCode": self.streetAddress.zip,
                 "orgTaxId"      : ein,
                 "DOBday"        : DOBDateObj.obj.getDate(),
                 "DOBMonth"      : DOBDateObj.obj.getMonth() + 1,
                 "DOBYear"       : DOBDateObj.obj.getFullYear(),
                 "ARLFirstName"  : repFirstName,
                 "ARLastName"    : repLastName,
                 "ArSSNLast4"    : repSSN
             })
         }

     api.makeApiRequest({
         type: "orgVerification",
         data: reqData,
         success: function(respObj){
             $('#verifyOrganization').collapse('hide')
             $('#accountCreateComplete').collapse('show')
         },
         error: function(error){
             switch(error.errorCode) {
                 case "InvalidAddressStreet":
                 case "EmptyAddressStreet":
                     orgUtil.setInputError("createOrgAddress","Invalid Address")
                     break
                 case "InvalidAddressCity":
                 case "EmptyAddressCity":
                     orgUtil.setInputError("createOrgAddress","Invalid City")
                     break
                 case "EmptyAddressState":
                 case "InvalidAddressState":
                     orgUtil.setInputError("createOrgAddress","Invalid State")
                     break
                 case "EmptyAddressZipCode":
                 case "InvalidAddressZipCode":
                     orgUtil.setInputError("createOrgAddress","Invalid ZIP")
                     break
                 case "EmptyTaxId":
                 case "InvalidTaxId":
                     orgUtil.setInputError("createOrgEIN","Invalid TaxID")
                     break
                 case "InvalidFirstName":
                 case "EmptyFirstName":
                     orgUtil.setInputError("createOrgRepFN","Invalid First Name")
                     break
                 case "EmptyLastName":
                 case "InvalidLastName":
                     orgUtil.setInputError("createOrgRepLN","Invalid Last Name")
                     break
                 case "InvalidDate":
                 case "InvalidMonth":
                 case "InvalidYear":
                     orgUtil.setInputError("createOrgRepDOB","Invalid DOB")
                     break
                 case "InvalidLast4SSN":
                 case "EmptyLast4SSN":
                     orgUtil.setInputError("createOrgRepSSN","Invalid Last 4 Digits of SSN")
                     break
                 case "InvalidBusinessName":
                     //todo: will need to handle as special case.
                 default:
                     toastr.error(error.errorCode)
             }
         },
         expired: function() { orgSignIn.onInValidAccessToken() },
         extend: function() { orgSignIn.extendCookieLife() }
     })
} //SCREEN 5


var orgSignUp = new OrgSignUp()
