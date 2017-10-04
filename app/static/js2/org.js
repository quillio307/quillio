
function setPageState(stateStr) {
    $("#state").text(stateStr)
}

function getPageState() {
    return $("#state").html()
}

function pushState(stateStr) {
    var stateObj = {page: stateStr}
    history.pushState(stateObj, "", "#" + stateStr);
}

function getPopState(event) {
    if(event.originalEvent.state != undefined && event.originalEvent.state != null) {
        return event.originalEvent.state.page
    } else {
        return
    }
}

$(window).on("popstate", function(event) {
    var upcoming = getPopState(event)
    var last = getPageState()
    if(upcoming == undefined || upcoming == null) {
        return
    }

    switch(upcoming) {
        case "dashboard":
            orgMain.switchWindow("sideMenuDashboardA", false)
            break
        case "account":
            orgMain.switchWindow("sideMenuAccountA", false)
            break
        case "campaign":
            orgMain.switchWindow("sideMenuPPA", false)
            break
        case "reportTransfers":
            orgMain.switchWindow("sideMenuTransfersA", false)
            break
        case "reportCharts":
            orgMain.switchWindow("sideMenuChartsA", false)
            break
        case "reportCampaigns":
            orgMain.switchWindow("sideMenuCampaignsA", false)
            break
        case "reportDonors":
            orgMain.switchWindow("sideMenuDonorsA", false)
            break
        case "reportUnsettled":
            orgMain.switchWindow("sideMenuUnsettledA", false)
            break
        case "legal":
            orgMain.switchWindow("sideMenuLegalA", false)
            break
        case "help":
            orgMain.switchWindow("sideMenuHelpA", false)
            orgMain.setHeading("Help")
            break
        case "volunteers":
            orgMain.switchWindow("sideMenuVolunteersA", false)
            break
    }
});

$(document).ready(function() {
    $("#sideMenuDashboardA").click(function() {
        orgMain.switchWindow("sideMenuDashboardA", true)
    });
    $("#sideMenuAccountA").click(function() {
        orgMain.switchWindow("sideMenuAccountA", true)
    });
    $("#sideMenuPPA").click(function() {
        orgMain.switchWindow("sideMenuPPA", true)
    });
    $("#sideMenuTransfersA").click(function() {
         orgMain.switchWindow("sideMenuTransfersA", true)
    });
    $("#sideMenuChartsA").click(function() {
         orgMain.switchWindow("sideMenuChartsA", true)
    });
    $("#sideMenuCampaignsA").click(function() {
         orgMain.switchWindow("sideMenuCampaignsA", true)
    });

    $("#sideMenuDonorsA").click(function() {
         orgMain.switchWindow("sideMenuDonorsA", true)
    });

    $("#sideMenuUnsettledA").click(function() {
         orgMain.switchWindow("sideMenuUnsettledA", true)
    });

    $("#sideMenuLogoutA").click(function() {
        orgMain.doLogout()
    });
    $("#sideMenuLegalA").click(function() {
        orgMain.switchWindow("sideMenuLegalA", true)
        orgMain.setHeading("Legal")
    });
    $("#sideMenuHelpA").click(function() {
        orgMain.switchWindow("sideMenuHelpA", true)
        orgMain.setHeading("Help")
    });
    $("#sideMenuVolunteersA").click(function() {
        orgMain.switchWindow("sideMenuVolunteersA", true)
    });

    var qsParams = utils.getUrlVars()
    if(qsParams["demo"] != undefined && qsParams["demo"] == "demo") {
        var params = {'email': "demo@paybee.io", 'password': "demotest1"}
        api.makeApiRequest({
            type: "orgSignIn",
            data: {'p' : JSON.stringify(params)},
            success: function(result) {
                orgSignIn.setAccessTokenCookie(result.access_token)
                orgMain.doStartup()
            }
        })
    } else {
        orgMain.doStartup()
    }

    $("#goToSignup").click(orgSignIn.redirectToSignUp)
    $("#accountUpdateButton").click(function() {
        orgMain.updateOrgInfo()
    });

    $("#downloadQRCode").click(function() {
//        orgMain.downloadQrCode("downloadImage", "")
        var pledgeUrl = window.location.hostname + "/@" + localOrgData.user.handle
        orgMain.setupQRDownload("org", localOrgData.user.id, pledgeUrl, localOrgData.user.handle)
    });

    $('#qrPreviewModel').on('shown.bs.modal', function () {
        $(this).find('.modal-dialog')
            .css({
                'position': 'relative',
                'display': 'table',
                'overflow-y': 'auto',
                'overflow-x': 'auto',
                'width': 'auto'
                });
    });

    $("#cpForm").submit( function(form) {
        orgSignIn.ChangePassword()
        form.preventDefault();
    });

    $("#addNewCampaign").click(function() {
        manageCampaign.addNewCampaign()
    });

    //////////////////////////
    $("#signInButton").click(function(){
        orgSignIn.doSignIn()
    })

    $("#forgotPassword").click(function() {
        orgSignIn.forgotPassword()
    })

    $('.datepicker').pickadate({
        formatSubmit: 'yyyy/mm/dd',
        selectMonths: 12,
        selectYears: 10,
        selectMonth: 'picker__select--month',
        selectYear: 'picker__select--year'
    });

    $('.mdb-select').material_select()

    $("#selectCoverImage").change(function() {
        orgMain.uploadOrgImage(this,'accountUserImage')
    })

    $("#selectedLogo").change(function() {
        orgMain.uploadLogoImage(this,'accountLogo')
    })

    $("#navSupport").click(function() {
        orgUtil.showSupportModal()
    })

    $("#navContact").click(function() {
        orgUtil.showSupportModal()
    })

    $("#testDownload").click(function(){
        var pledgeUrl = window.location.hostname + "/@" + localOrgData.user.handle
        orgMain.setupQRDownload("org", localOrgData.user.id, pledgeUrl, localOrgData.user.handle)
    })
});

var OrgMain = function() {
    this.logoImageUrl = ""
    this.orgCoverImage = ""
    this.donorList = []
    this.filteredVolunteerList = []
}

OrgMain.prototype.hideAll = function() {
    $("#dashboard").hide()
    $("#campaigns").hide()
    $("#campaignDetails").hide();
    $("#account").hide()
    $("#legal").hide()
    $("#help").hide()
    $("#volunteer").hide()
    $("#transfers").hide()
    $("#charts").hide()
    $("#campaignReport").hide()
    $("#allCampaignsReport").hide()
    $('#campaignDetailsReport').hide();
    $("#newCampaign").hide()
    $("#donors").hide()
    $("#unsettled").hide()
}

OrgMain.prototype.switchWindow = function(destination, push) {
    var self = this
    switch(destination) {
        case "sideMenuDashboardA" :
            setPageState("dashboard")
            if(push) {
                pushState("dashboard")
            }
            self.showDashboard()
            $("#sideMenuDashboardA").addClass("active")
            return
        case "sideMenuAccountA" :
            setPageState("account")
            if(push) {
                pushState("account")
            }
            self.showAccountManage()
            $("#sideMenuAccountA").addClass("active")
            return
        case "sideMenuPPA" :
            setPageState("campaign")
            if(push) {
                pushState("campaign")
            }
            manageCampaign.showCampaignManage()
            $("#sideMenuPPA").addClass("active")
            return
        case "sideMenuTransfersA" :
             setPageState("reportTransfers")
             if(push) {
                 pushState("reportTransfers")
             }
             self.showTransfers()
             return
        case "sideMenuChartsA" :
            setPageState("reportCharts")
            if(push) {
                pushState("reportCharts")
            }
            self.showCharts()
            return

        case "sideMenuDonorsA":
            setPageState("reportDonors")
            if(push) {
                pushState("reportDonors")
            }
            self.showDonors()
            return

        case "sideMenuUnsettledA":
            setPageState("reportUnsettled")
            if(push) {
                pushState("reportUnsettled")
            }
            self.showUnsettledDonations()
            return

        case "sideMenuCampaignsA" :
            setPageState("reportCampaigns")
            if(push) {
                pushState("reportCampaigns")
            }
            self.showCampaignsReport()
            return
        case "sideMenuLegalA" :
            setPageState("legal")
            if(push) {
                pushState("legal")
            }
            this.hideAll()
            $("#legal").show()
            $("#sideMenuLegalA").addClass("active")
            return
        case "sideMenuHelpA":
            setPageState("help")
            if(push) {
                pushState("help")
            }
            this.hideAll()
            $("#help").show()
            $("#sideMenuHelpA").addClass("active")
            return
        case "sideMenuVolunteersA":
            setPageState("volunteers")
            if(push) {
                pushState("volunteers")
            }
            self.showVolunteerManage()
            $("#sideMenuVolunteersA").addClass("active")
            return
        default:
            return
    }
}

OrgMain.prototype.downloadQrCode = function(divId, fileNameExt) {
    var element = $('#' + divId)
    var getCanvas
    html2canvas(element, {
        onrendered: function (canvas) {
            $("#previewImage").html(canvas);
            getCanvas = canvas;
            var imageData = getCanvas.toDataURL("image/png", 1.0);
            // Now browser starts downloading it instead of just showing it
            var newData = imageData.replace(/^data:image\/png/, "data:application/octet-stream");
            $('#qrPreviewModel').modal('show');
            $("#imageToPrint").attr("src",newData)
            $("#btn-Convert-Html2Image").attr("download", localOrgData.user.handle + fileNameExt + ".png").attr("href", newData);
        }
    });
}

OrgMain.prototype.doStartup = function() {
    var self = this
    if(!orgSignIn.isValidAccessToken()) {
        localOrgData = {}
        orgUtil.showLoginModel()
    }
    else {
        orgSignIn.getOrgUserData(
            function() {
                if(localOrgData.user.status != 0) {
                    api.redirectToSignUp()
                    return
                }
                self.showDashboard()
            },
            function(error) {
                self.doLogout()
            }
        )
    }
}

OrgMain.prototype.doLogout = function() {
    var self = this
    if(orgSignIn.isValidAccessToken()) {
        api.deleteCookie('accessToken')
    }
    localOrgData = {}
    orgUtil.showLoginModel("Login again")
}

OrgMain.prototype.setHeading = function(heading) {
    $("#pageHeading").text(heading)
}

OrgMain.prototype.showDashboard = function() {
    var self = this
    self.setHeading("Dashboard")
    if(localOrgData == {}) {
        self.doStartup()
    }

    $('#orgUserImage').attr("src", localOrgData.user.imageUrl)
    $('#orgQRCode').attr("src","/api/qr_code" + "?payee=" + localOrgData.user.id)
    $('#orgUserName').text(localOrgData.user.name)
    $('#orgPurpose').text(localOrgData.user.purpose)
    $('#orgDescription').text(localOrgData.user.desc)
    var pledgeUrl = "//" + window.location.hostname + "/@" + localOrgData.user.handle
    $('#orgQrCodeLink').attr("href", pledgeUrl)
    $('#orgPayUrl').attr("href", pledgeUrl)
    $('#orgPayUrl').text(window.location.hostname + "/@" + localOrgData.user.handle)
    $('#orgUrl').text(localOrgData.user.url);
    $('#orgPledgedAmount').text('Pledges: $' + localOrgData.user.pledgedAmountTo.toFixed(2))
    $('#orgReceivedAmount').text('Received: $'+ localOrgData.user.paidAmountTo.toFixed(2))

    if(typeof(localOrgData.user.url) == "undefined" || localOrgData.user.url == "") {
        $('#orgUrl').text("")
    }
    else {
        var orgUrl = localOrgData.user.url
        if(!orgUrl.startsWith("www")) {
            orgUrl = "www." + orgUrl
        }
        else {
            var orgDisplayUrl = orgUrl
        }
        $('#orgUrl').attr("href",orgUrl)
        $('#orgUrl').text(orgDisplayUrl)
    }

    self.hideAll()
    self.showRecentTransactions()
    $('#dashboard').show()
    $("#sideMenuDashboard").attr("class", "panel active")

    $("#createNewCampaignDashboard").click(function() {
        manageCampaign.showCampaignManage()
    })
}

OrgMain.prototype.dateTimeString = function(date) {
    return (new moment(new Date(date*1000))).format("YYYY/MM/DD h:mm a")
}

OrgMain.prototype.dateString = function(date) {
    return (new moment(new Date(date*1000))).format("YYYY/MM/DD")
}


OrgMain.prototype.donationStatus = function(status) {
    if(status == 1)
        return "Pledged";
    else
        return "Donated";
}

OrgMain.prototype.showRecentTransactions = function() {
    if(!$.isArray(localOrgData.user.userTransactions)
        || localOrgData.user.userTransactions.length < 1) {
            $("#recentTransaction").html("<tr style='height: 100px'><td></td><td class='text-center purple-text'>No donations yet:(</td><td></td></tr>")
            return
    }

    var status = "Donated";
    if ( $.fn.DataTable.isDataTable( "#recentTransaction" ) ) {
         var oTable = $("#recentTransaction").dataTable();
         oTable.fnClearTable();
         oTable.fnAddData(localOrgData.user.userTransactions);
         oTable.fnDraw();
    }
    else {
        $("#recentTransaction").dataTable({
            data: localOrgData.user.userTransactions,
            autoWidth: false,
            order: [[ 4, "desc" ]],
            dom: "Btfip",
            buttons: [{extend: 'excel', text: 'Export', title : 'Recent Transactions'}],
            columns: [
                {
                    "data": "payer.image",
                    "width": "10%",
                    "orderable" : false,
                    "render" : function (data, type, row) {
                        return '<img height="50" class="img-rounded" src="'+data+'"/>'
                    }
                },
                {
                    "data": "payer.name",
                    "width": "15%"
                },
                {
                    "data": "payee.selectedCampaign",
                    "width": "15%",
                    "render": function(selectedCampaign) {
                        if(selectedCampaign != undefined) {
                            return selectedCampaign.name
                        }
                        else {
                            return ""
                        }
                    }
                },
                {
                    "data": "status",
                    "width": "15%" ,
                    "render": function(status){
                        return OrgMain.prototype.donationStatus(status);
                    }
                },
                {
                    "data": "updated",
                    "sType": "date",
                    "width": "15%" ,
                    "render": function(data,type, row )
                    {
                        return OrgMain.prototype.dateTimeString(row.updated);
                    }
                },
                {
                    "data": "amount",
                    "width": "15%"
                }
            ]
        })
    }
}

OrgMain.prototype.showUnsettledDonations = function() {
    var self = this
    $("#pageHeading").text("Unsettled Donations")
    self.hideAll()
    $("#unsettled").show()
    api.makeApiRequest({
        type: "getUnsettledDonations",
        data: {"access_token": orgSignIn.getAccessToken()},
        success: function(donationArray) {
//            self.donorList = donorArray
            if(!$.isArray(donationArray)
                || donationArray.length < 1) {
                $("#unsettledList").html("<tr style='height: 100px'><td></td><td class='text-center purple-text'>No unsettled donations:)</td><td></td></tr>")
                return
            }
            if ($.fn.DataTable.isDataTable("#unsettledList")) {
                 var oTable = $("#unsettledList").dataTable()
                 oTable.fnClearTable()
                 oTable.fnAddData(donationArray)
                 oTable.fnDraw()
            }
            else {
                $("#unsettledList").dataTable({
                    data: donationArray,
                    autoWidth: false,
                    order: [[ 4, "desc" ]],
                    dom: "Btfip",
                    buttons: [{extend: 'excel', text: 'Export', title : 'donorList'}],
                    columns: [
                        {
                            "data": "volunteerInfo.name",
                            "width": "15%"
                        },
                        {
                            "data": "payer.name",
                            "width": "15%"
                        },
                        {
                            "data": "amount",
                            "width": "15%",
                            "render": function(amount) {
                                return "$" + amount.toFixed(2)
                            }
                        },
                        {
                            "data": "method",
                            "width": "15%",
                            "render": function(method, type, row) {
                                if(row.checkFrontImageUrl != ""
                                    || row.checkBackImageUrl != ""
                                    || row.volunteerAcceptMemo != "") {
                                    var showDetailId = "methodDetail_" + row.id
                                    return method + " <a class='blue-text' id='" + showDetailId + "' onclick='orgMain.showUnsettledDetail(this)'>(detail)</a>"
                                } else {
                                    return method
                                }
                            }
                        },
                        {
                            "data": "date",
                            "sType": "date",
                            "width": "15%" ,
                            "render": function(date, type, row ) {
                                return OrgMain.prototype.dateTimeString(date);
                            }
                        },
                        {
                            "data": "id",
                            "width": "15%",
                            "render": function(id, type, row, meta ) {
                                var buttonId = "settle_" + id
                                return "<button id='"
                                    + buttonId
                                    + "' onclick='orgMain.SettleDonation(this)'"
                                    + "class='btn btn-sm btn-info'>Confirm</button>"
                            }
                        }
                    ]
                })
            }
        },
        error: function(error) {
            toastr.error(genericError)
        },
        expired: function() { orgSignIn.onInValidAccessToken() },
        extend: function() { orgSignIn.extendCookieLife() }
    })
}

OrgMain.prototype.showUnsettledDetail = function(link) {
    var self = this
    var donationId = link.id.split("_")[1] || ""
    $("#unsettledDetail").modal("show")

    api.makeApiRequest({
        type: "transaction",
        data: {"access_token": orgSignIn.getAccessToken(), "tid": donationId},
        success: function(donationDetail) {
            $("#donationMemo").text(donationDetail.volunteerAcceptMemo)
            api.makeApiRequest({
                type: "getCheckImageUrls",
                data: {"tid": donationDetail.id, "access_token": orgSignIn.getAccessToken()},
                success: function(response) {
                    $("#checkFront").prop("src", response.frontImage)
                    $("#checkBack").prop("src", response.backImage)
                },
                error: function(error) {
                    toastr.error(genericError)
                }
            })
        },
        error: function(error) {
            toastr.error(genericError)
        },
        expired: function() { orgSignIn.onInValidAccessToken() },
        extend: function() { orgSignIn.extendCookieLife() }
    })
}

OrgMain.prototype.SettleDonation = function(button) {
    var self = this
    var donationId = button.id.split("_")[1] || ""
    api.makeApiRequest({
        type: "settleVolunteerDonation",
        data: {"access_token": orgSignIn.getAccessToken(), "id": donationId},
        success: function() {
            toastr.success("Confirmation recorded")
            $("#" + button.id).prop('disabled', true)
        },
        error: function(error) {
            toastr.error("Confirmation failed, try again")
        },
        expired: function() { orgSignIn.onInValidAccessToken() },
        extend: function() { orgSignIn.extendCookieLife() }
    })
}

OrgMain.prototype.showDonors = function() {
    var self = this
    $("#pageHeading").text("Donors")
    self.hideAll()
    $("#donors").show()

    api.makeApiRequest({
        type: "donors",
        data: {"access_token": orgSignIn.getAccessToken()},
        success: function(donorArray) {
            self.donorList = donorArray
            if(!$.isArray(donorArray)
                || donorArray.length < 1) {
                $("#donorList").html("<tr style='height: 100px'><td></td><td class='text-center purple-text'>No donors yet:(</td><td></td></tr>")
                return
            }
            if ($.fn.DataTable.isDataTable("#donorList")) {
                 var oTable = $("#donorList").dataTable()
                 oTable.fnClearTable()
                 oTable.fnAddData(donorArray)
                 oTable.fnDraw()
            }
            else {
                $("#donorList").dataTable({
                    data: donorArray,
                    autoWidth: false,
                    order: [[ 5, "desc" ]],
                    dom: "Btfip",
                    buttons: [{extend: 'excel', text: 'Export', title : 'donorList'}],
                    columns: [
                        {
                            "data": "payer.image",
                            "width": "10%" ,
                            "orderable" : false,
                            "render" : function (data, type, row) {
                                return '<img height="50" class="img-rounded" src="'+data+'"/>'
                            }
                        },
                        {
                            "data": "payer.name",
                            "width": "15%"
                        },
                        {
                            "data": "payer.email",
                            "width": "15%"
                        },
                        {
                            "data": "totalDonations",
                            "width": "15%",
                            "render": function(totalDonations) {
                                return "$" + totalDonations.toFixed(2)
                            }
                        },
                        {
                            "data": "numDonations",
                            "width": "15%",
                        },
                        {
                            "data": "lastDonated",
                            "sType": "date",
                            "width": "15%" ,
                            "render": function(data, type, row ) {
                                return OrgMain.prototype.dateTimeString(row.lastDonated);
                            }
                        },
                        {
                            "data": "details",
                            "width": "15%",
                            "render": function(data, type, row, meta ) {
                                var buttonId = "detail_" + meta.row
                                return "<button id='"
                                    + buttonId
                                    + "' onclick='orgMain.showDonorDetails(this)'"
                                    + "class='btn btn-sm btn-info'>details</button>"
                            }
                        }
                    ]
                })
            }
        },
        error: function(error) {
            toastr.error(genericError)
        },
        expired: function() { orgSignIn.onInValidAccessToken() },
        extend: function() { orgSignIn.extendCookieLife() }
    })
}

OrgMain.prototype.showDonorDetails = function(button) {
    var self = this
    var donorIndex = button.id.split("_")[1] || 0
    var donorInfo = self.donorList[donorIndex]

    $("#donorName").text(donorInfo.payer.name)
    $("#donorDetailModal").modal("show")
    if(!$.isArray(donorInfo.donations)
        || donorInfo.donations < 1) {
        $("#donorTransactions").html("<tr style='height: 100px'><td></td>"
                    + "<td class='text-center purple-text'>No donations yet:(</td><td></td></tr>")
        return
    }

    if ( $.fn.DataTable.isDataTable("#donorTransactions")) {
         var oTable = $("#donorTransactions").dataTable()
         oTable.fnClearTable()
         oTable.fnAddData(donorInfo.donations)
         oTable.fnDraw()
    }
    else {
        $("#donorTransactions").dataTable({
            data: donorInfo.donations,
            autoWidth: false,
            order: [[ 4, "desc" ]],
            dom: "Btfip",
            buttons: [{extend: 'excel', text: 'Export', title : 'donorTransactions'}],
            columns: [
                {
                    "data": "campaignName",
                    "width": "30%"
                },
                {
                    "data": "presetName",
                    "width": "25%"
                },
                {
                    "data": "status",
                    "width": "15%",
                    "render": function(data, type, row, meta ) {
                        return self.donationStatus(row.status)
                    }
                },
                {
                    "data": "amount",
                    "sType": "number",
                    "width": "15%",
                    "render": function(data, type, row ) {
                        return "$" + row.amount.toFixed(2)
                    }
                },
                {
                    "data": "date",
                    "width": "15%",
                    "sType": "date",
                    "render": function(data, type, row ) {
                        return OrgMain.prototype.dateString(row.date)
                    }
                }
            ]
        })
    }
}

var $lime = "#8CBF26",
    $red = "#f25118",
    $redDark = "#d04f4f",
    $blue = "#4e91ce",
    $green = "#3ecd74",
    $orange = "#f2c34d",
    $pink = "#E671B8",
    $purple = "#A700AE",
    $brown = "#A05000",
    $teal = "#4ab0ce",
    $gray = "#666",
    $white = "#fff",
    $textColor = $gray;

var COLOR_VALUES = [
    $red,
    $orange,
    $green,
    $blue,
    $teal,
    $redDark,
    $lime,
    $pink,
    $purple,
    $brown
];

OrgMain.prototype.showTransfers = function() {
    $("#pageHeading").text("Transfer report")
    this.hideAll()
    var self = this;
    $("#transfers").show();
    $('#transferPage').show();
    $('#transferDetailsPage').hide();

    $("#transStartDatePicker").off("change", startDateChanged)
    $("#transEndDatePicker").off("change", endDateChanged)

    var startDate = new Date(new Date().setMonth(new Date().getMonth() - 1 ))
    var endDate = new Date()
    $("#transStartDatePicker").data("pickadate").set('select', startDate)
    $("#transEndDatePicker").data("pickadate").set('select', endDate)

    updateTransferDataTable(startDate, endDate);

    var startDateChanged = function() {
        var dateObj = $("#transStartDatePicker").data("pickadate").get("select")
        if(dateObj != null) {
            startDate = dateObj.obj
        }
        updateTransferDataTable(startDate, endDate)
    }

    var endDateChanged = function() {
        var dateObj = $("#transEndDatePicker").data("pickadate").get("select")
        if(dateObj != null) {
            endDate = dateObj.obj
        }
        updateTransferDataTable(startDate, endDate)
    }

    $("#transStartDatePicker").on("change", startDateChanged)
    $("#transEndDatePicker").on("change", endDateChanged)

    function updateTransferDataTable(startDate, endDate){
        var params = {'startDate': Math.floor(startDate.getTime()/1000), 'endDate': Math.floor(endDate.getTime()/1000)}
        api.makeApiRequest({
            type: "payoutReport",
            data: {'p' : JSON.stringify(params),"access_token": orgSignIn.getAccessToken()},
            success: function(payoutReport) {
                if (payoutReport.payouts.length > 0){
                    $("#noTransactionData").hide();
                    $("#transferPage").show();
                    $("#campaignPieChartPage").hide();
                    $("#transferDetailsPage").hide();
                    $('#totalPayouts').text(payoutReport.payouts.length);
                    $('#totalPayoutAmount').text('$'+payoutReport.proceed);
                    $('#totalOrgFee').text('$'+payoutReport.orgFee);
                    $('#totalDonationAmount').text('$'+payoutReport.amount);
                    $('#pieChartButton').unbind('click').click(function() {
                        self.showCampaignDetails(payoutReport);
                    });

                    $("#data-chart-footer").text('');
                    var pieChartData = [],
                    campaigns = payoutReport.campaigns.sort(function(a, b){
                                    return a.proceed < b.proceed;
                    });
                    campaigns.forEach( function (campaign) {
                        var currentObject = {},
                        campaignName = "";
                        if (campaign.campaignData == null || campaign.campaignData == undefined)
                            campaignName = "Default"
                        else if (campaign.campaignData.name.length > 20)
                            campaignName = campaign.campaignData.name.substring(0, 17)+"..."
                        else
                            campaignName = campaign.campaignData.name

                        currentObject["key"] = campaignName
                        currentObject["values"] = [{ "x": 123, "y": campaign.proceed}]
                        pieChartData.push(currentObject)
                    });

                    setTimeout(function() {
                        var   pieSelect = d3.select("#sources-chart-pie"),
                        pieFooter = d3.select("#data-chart-footer");

                        function pieChartUpdate(d) {
                            d.disabled = !d.disabled;
                            d3.select(this)
                           .classed("disabled", d.disabled);
                            if (!pieChart.pie.values()(pieChartData).filter(function(d) { return !d.disabled }).length) {
                                pieChart.pie.values()(pieChartData).map(function(d) {
                                    d.disabled = false;
                                    return d;
                                });
                                pieFooter.selectAll('.control').classed('disabled', false);
                            }
                            d3.select("#sources-chart-pie svg").transition().call(pieChart);
                        }

                        nv.addGraph(function() {
                           for (var i = 0; i < pieChartData.length; i++){
                               pieChartData[i].y = (d3.sum(pieChartData[i].values, function(d){
                                   return d.y;
                               }))
                           }

                            var chart = nv.models.pieChartTotal()
                               .x(function(d) {return d.key })
                               .values(function(d) {return d })
                               .color(COLOR_VALUES)
                               .showLabels(false)
                               .showLegend(false)
                               .tooltipContent(function(key, y, e, graph) {
                                   return '<h4>' + key + '</h4>' + '<p>' +  y + '</p>'
                               })
                               .total(function(count){
                                   return "<div class='block text-center'>$" + Math.round(count * 100) / 100 + "</div>"
                               })
                               .donut(true);
                            chart.pie.margin({top: 10, bottom: -20});

                            var sum = d3.sum(pieChartData, function(d){
                               return d.y;
                            });

                            var pieChartDataFooter = pieChartData.slice(0,6);
                            pieFooter
                               .classed("controls", true)
                               .selectAll("div")
                               .data(pieChartDataFooter)
                               .enter().append("div")
                               .classed("control", true)
                               .style("border-left", function(d, i){
                                   return "20px solid " + COLOR_VALUES[i];
                               })
                               .html(function(d) {
                                   return "<div style='margin-left: 10px'><strong>$" + d.y + "</strong> - " + d.key + "</div>" ;
                               });

                            d3.select("#sources-chart-pie svg")
                               .datum([pieChartData])
                               .transition(500).call(chart);

//                            PjaxApp.onResize(chart.update);

                            pieChart = chart;

                            return chart;
                        });
                    }, 500);

                    if ( $.fn.DataTable.isDataTable("#allTransfers") ) {
                         var oTable = $("#allTransfers").dataTable();
                         oTable.fnClearTable();
                         if (payoutReport.payouts.length > 0) {
                            oTable.fnAddData(payoutReport.payouts);
                            oTable.fnDraw();
                         }
                     } else {
                           $("#allTransfers").DataTable({
                                data: payoutReport.payouts,
                                autoWidth: false ,
                                "iDisplayLength": 50,
                                'aaSorting': [[1, 'desc']],
                                dom: "Btip",
                                buttons: [{extend: 'excel', text: 'Export',title : 'AllTransfers'}],
                                "fnDrawCallback":function(){
                                if (Math.ceil((this.fnSettings().fnRecordsDisplay()) / this.fnSettings()._iDisplayLength) > 1) {
                                    $('.dataTables_paginate').css("display", "block");
                                    $('.dataTables_info').css("display", "block");
                                } else {
                                    $('.dataTables_paginate').css("display", "none");
                                    $('.dataTables_info').css("display", "none");
                                }
                                },
                                columns: [
                                    {
                                        "data": "id",
                                        "targets": 0,
                                        "visible": true
                                    },
                                    {
                                        "data": "dateCreated",
                                        "sType": "date",
                                        "render": function(data, type, row ) {
                                            return OrgMain.prototype.dateString(row.expectedDepositDate);
                                        }
                                    },
                                    {
                                        "data": "proceed",
                                        "render":function(data, type, row ){
                                            return "$"+row.proceed;
                                        },
                                        'orderable': true
                                    },
                                    {
                                        "data": "orgFee",
                                        "render":function(data, type, row ) {
                                            return "$"+row.orgFee
                                        },
                                        'orderable': true
                                    },
                                    {
                                        "data": "amount",
                                        "render": function(data, type, row )
                                        {
                                            return "$"+row.amount
                                        },
                                        'orderable': true
                                    },
                                    {
                                        "data": "status",
                                        'orderable': true
                                    }
                                ]
                              });

                            $('#allTransfers').off( 'click.rowClick' ).on('click.rowClick', 'td',  function() {
                                var dt = $("#allTransfers").DataTable();
                                var data = dt.row( $(this)).data();
                                self.showTransferDetails(data);
                            });
                     }

                 } else {
                    $("#noTransactionData").show();
                    $("#transferPage").hide();
                    $("#campaignPieChartPage").hide();
                    $("#transferDetailsPage").hide();
                 }
            },
            error: function(error) {
               toastr.error(genericError)
            },
            expired: function() { orgSignIn.onInValidAccessToken() },
            extend: function() { orgSignIn.extendCookieLife() }
        })
    }
}

OrgMain.prototype.showCharts = function() {
    $("#pageHeading").text("Report charts")

    var self = this;
    self.hideAll()
    $("#charts").show();

    function keyColor(d, i) {
        if (!window.colors){
            window.colors = function(){
                return d3.scale.ordinal().range(COLOR_VALUES);
            }();
        }
        return window.colors(d.key)
    }

    api.makeApiRequest({
        type: "biActivity",
        data: {"access_token": orgSignIn.getAccessToken(), type: "daily"},
        success: function(dailyActivityData) {
         setTimeout(function() {
          nv.addGraph(function() {
              var chart = nv.models.multiBarChart()
                  .margin({left: 30, bottom: 20, right: 0})
        //                      .color(keyColor)
        //                      .controlsColor([$white, $white, $white])
                  .showLegend(true);

              chart.yAxis
                  .showMaxMin(false)
                  .ticks(0)
                  .tickFormat(d3.format(',.f'));

              chart.xAxis
                  .showMaxMin(false)
                  .tickFormat(function(d) { return d3.time.format('%b %d')(new Date(d)) });

              d3.select('#sources-chart-bar svg')
                  .datum(dailyActivityData)
                  .transition().duration(500).call(chart);

              chart.update()
              barChart = chart;

              return chart;
          });
          }, 500);
        },
        error: function(error) {
            toastr.error(genericError)
        },
        expired: function() { orgSignIn.onInValidAccessToken() },
        extend: function() { orgSignIn.extendCookieLife() }
    })
}

OrgMain.prototype.showCampaignsReport = function() {
    var self = this;
    $("#pageHeading").text("Campaign Report")
    self.hideAll()
    $("#campaignReport").show();
    $("#allCampaignsReport").show();

    $("#donStartDatePicker").off("change", startDateChanged)
    $("#donEndDatePicker").off("change", endDateChanged)

    var startDate = new Date(new Date().setMonth(new Date().getMonth() - 1 ))
    var endDate = new Date()
    $("#donStartDatePicker").data("pickadate").set('select', startDate)
    $("#donEndDatePicker").data("pickadate").set('select', endDate)

    updateCampaignDataTable(startDate, endDate);

    var startDateChanged = function() {
        var dateObj = $("#donStartDatePicker").data("pickadate").get("select")
        if(dateObj != null) {
            startDate = dateObj.obj
        }
        updateCampaignDataTable(startDate, endDate)
    }

    var endDateChanged = function() {
        var dateObj = $("#donEndDatePicker").data("pickadate").get("select")
        if(dateObj != null) {
            endDate = dateObj.obj
        }
        updateCampaignDataTable(startDate, endDate)
    }


    $("#donStartDatePicker").on("change", startDateChanged)
    $("#donEndDatePicker").on("change", endDateChanged)

    function updateCampaignDataTable(startDate, endDate) {
        var params = {'startDate': Math.floor(startDate.getTime()/1000), 'endDate': Math.floor(endDate.getTime()/1000)}
        var campaignsTemplate = "<tr>\
            <td width='100%'>\
                <div class='row'>\
                    <div class='col-2' style='height: 100%; padding-right: 2px'>\
                        <!-- <strong> Campaign </strong> -->\
                        <div class='row'>\
                            <div class='col'>\
                                <img class='img-fluid' src='%campaignImage%' height='50' alt='Card image cap'>\
                                <div class='card-body text-center'>\
                                    <h6 class='card-title' style='margin-top: 1rem;'>%campaignName%</h6>\
                                    <h5 class='text-muted card-text' style='margin-bottom: 1rem;'>$%campaignProceed%</h5>\
                                    <div id='%detailButtonId%' onclick='orgMain.showCampaignReportDetails(this)' class='btn btn-info btn-sm'>Details</div>\
                                </div>\
                            </div>\
                        </div>\
                    </div>\
                    <div class='col' style='padding-left: 2px'>\
                        <!-- <strong> Preset options </strong> -->\
                        <ul class='list-group' style='box-shadow: none;'>\
                        %presetData%\
                        </ul>\
                    </div>\
                </div>\
            </td>\
        </tr>"
        var presetTemplate = "<li class='list-group-item d-flex justify-content-between align-items-center'>\
            %presetName%\
            <span class='text-muted h5-responsive'>$%presetProceed%</span>\
        </li>"

        var finalHtml = ""
        api.makeApiRequest({
            type: "campaignReport",
            data: {'p' : JSON.stringify(params),"access_token": orgSignIn.getAccessToken()},
            success: function(campaignReport) {
                if (campaignReport.campaigns.length > 0){
                    var allCampaigns= campaignReport.campaigns.sort(function(a, b){
                        return a.proceed < b.proceed;
                    });

                    allCampaigns.forEach(function(campaign, index) {
                        if (campaign.presets != null){
                            var campaignPresets = campaign.presets.sort(function(a, b){
                                    return a.proceed < b.proceed;
                            });
                            var presetHtml = ""
                            campaignPresets.forEach(function(preset, idx){
                                var presetData = {
                                    "%presetName%"              : preset.presetInfo.name,
                                    "%presetProceed%"            : preset.proceed
                                }

                                presetHtml += presetTemplate.replace(/%\w+%/g, function(all) {
                                    if(typeof(presetData[all]) != 'undefined')
                                        return presetData[all];
                                    else
                                        return all;
                                });
                            })
                        }
                        if (campaign.campaignData == null || campaign.campaignData == undefined) {
                            var campaignData = {
                                "%campaignImage%"           : "images/logo_placeholder.png",
                                "%campaignId%"              : campaign.campaignId,
                                "%campaignName%"            : "Default",
                                "%campaignProceed%"         : campaign.proceed,
                                "%presetData%"              : "NA",
                                "%detailButtonId%"          : "detail_" + campaign.campaignId
                            }
                        }
                        else {
                            var campaignData = {
                                "%campaignImage%"           : campaign.campaignData.imageUrl == null
                                                              || campaign.campaignData.imageUrl == undefined
                                                              || campaign.campaignData.imageUrl == ""
                                                              ? "images/logo_placeholder.png" : campaign.campaignData.imageUrl,
                                "%campaignId%"              : campaign.campaignId,
                                "%campaignName%"            : campaign.campaignData.name,
                                "%campaignProceed%"         : campaign.proceed,
                                "%presetData%"              : presetHtml,
                                "%detailButtonId%"          : "detail_" + campaign.campaignId
                            }
                        }

                        finalHtml += campaignsTemplate.replace(/%\w+%/g, function(all) {
                            if(typeof(campaignData[all]) != 'undefined')
                                return campaignData[all];
                            else
                                return all;
                        });
                    })
                    $("#allCampaignsReportTable").html(finalHtml);
                }
            },
            error: function(error) {
                toastr.error(genericError)
            },
            expired: function() { orgSignIn.onInValidAccessToken() },
            extend: function() { orgSignIn.extendCookieLife() }
        })
    }
}

OrgMain.prototype.showCampaignReportDetails = function(button) {
    var self = this
    var campaignId = button.id.split("_")[1] || ""

    var startDate = new Date(new Date().setMonth(new Date().getMonth() - 1 ))
    var endDate = new Date()

    var startDateObj = $("#donStartDatePicker").data("pickadate").get("select")
    if(startDateObj != null) {
        startDate = startDateObj.obj
    }

    var endDateObj = $("#donEndDatePicker").data("pickadate").get("select")
    if(endDateObj != null) {
        endDate = endDateObj.obj
    }

    var params = {
        'startDate': Math.floor(startDate.getTime()/1000),
        'endDate': Math.floor(endDate.getTime()/1000),
        "campaignId": campaignId
    }

    api.makeApiRequest({
        type: "campaignDonations",
        data: {"p": JSON.stringify(params), "access_token": orgSignIn.getAccessToken()},
        success: function(donations) {
            $("#campaignReportDetailModal").modal("show")
            if(!$.isArray(donations)
                || donations < 1) {
                return
            }

            $("#campaignReportName").text(donations[0].campaignName)
            if ( $.fn.DataTable.isDataTable("#campaignDonations")) {
                 var oTable = $("#campaignDonations").dataTable()
                 oTable.fnClearTable()
                 oTable.fnAddData(donations)
                 oTable.fnDraw()
            }
            else {
                $("#campaignDonations").dataTable({
                    data: donations,
                    autoWidth: false,
                    pageLength: 5,
                    order: [[ 5, "desc" ]],
                    dom: "tfipB",
                    buttons: [{extend: 'excel', text: 'Export', title : 'campaignDonations'}],
                    columns: [
                        {
                            "data": "payer.image",
                            "width": "10%",
                            "orderable" : false,
                            "render" : function (data, type, row) {
                                return '<img height="50" class="img-rounded" src="'+ data + '"/>'
                            }
                        },
                        {
                            "data": "payer.name",
                            "width": "15%"
                        },
                        {
                            "data": "presetName",
                            "width": "25%"
                        },
                        {
                            "data": "status",
                            "width": "10%",
                            "render": function(data, type, row, meta ) {
                                return self.donationStatus(row.status)
                            }
                        },
                        {
                            "data": "amount",
                            "sType": "number",
                            "width": "10%",
                            "render": function(data, type, row ) {
                                return "$" + row.amount.toFixed(2)
                            }
                        },
                        {
                            "data": "date",
                            "width": "15%",
                            "sType": "date",
                            "render": function(data, type, row ) {
                                return OrgMain.prototype.dateString(row.date)
                            }
                        },
                        {
                            "data": "method",
                            "width": "15%"
                        }
                    ]
                })
            }
        },
        error: function(error){
            toastr.error(genericError)
        },
        expired: function() { orgSignIn.onInValidAccessToken() },
        extend: function() { orgSignIn.extendCookieLife() }
    });
}

OrgMain.prototype.showCampaignDetails = function(payoutReport) {
    var allCampaigns = payoutReport.campaigns
    $('#transferPage').hide();
    $('#campaignPieChartPage').show();
    $('#campaignSDate').text(OrgMain.prototype.dateString(payoutReport.startDate)+" - ");
    $('#campaignEDate').text(OrgMain.prototype.dateString(payoutReport.endDate));

    var campaignsTemplate = "<tr>\
        <td width='100%'>\
            <div class='row'>\
                <div class='col-2' style='height: 100%; padding-right: 2px'>\
                    <strong> Campaign </strong>\
                    <div class='row'>\
                        <div class='col'>\
                            <img class='img-fluid' src='%campaignImage%' height='50' alt='Card image cap'>\
                            <div class='card-body text-center'>\
                                <h5 class='card-title' style='margin-top: 1rem;'>%campaignName%</h5>\
                                <h5 class='text-muted card-text' style='margin-bottom: 1rem;'>$%campaignProceed%</h5>\
                            </div>\
                        </div>\
                    </div>\
                </div>\
                <div class='col' style='padding-left: 2px'>\
                    <strong> Preset options </strong>\
                    <ul class='list-group' style='box-shadow: none;'>\
                    %presetData%\
                    </ul>\
                </div>\
            </div>\
        </td>\
    </tr>"

    var presetTemplate = "<li class='list-group-item d-flex justify-content-between align-items-center'>\
        %presetName%\
        <span class='text-muted h5-responsive'>$%presetProceed%</span>\
    </li>"

    var finalHtml = ""
    allCampaigns.forEach(function(campaign, index) {
        if (campaign.presets != null){
            var campaignPresets = campaign.presets.sort(function(a, b){
                    return a.proceed < b.proceed;
            });
            var presetHtml = ""
            campaignPresets.forEach(function(preset, idx){
                var presetData = {
                    "%presetName%"              : preset.presetInfo.name,
                    "%presetProceed%"            : preset.proceed
                }

                presetHtml += presetTemplate.replace(/%\w+%/g, function(all) {
                    if(typeof(presetData[all]) != 'undefined')
                        return presetData[all];
                    else
                        return all;
                });
            })
        }
        if (campaign.campaignData == null || campaign.campaignData == undefined) {
            var campaignData = {
                "%campaignImage%"           : "images/logo_placeholder.png",
                "%campaignId%"              : campaign.campaignId,
                "%campaignName%"            : "Default",
                "%campaignProceed%"         : campaign.proceed,
                "%presetData%"              : "NA"
            }
        }
        else {
            var campaignData = {
                "%campaignImage%"           : campaign.campaignData.imageUrl == null
                                              || campaign.campaignData.imageUrl == undefined
                                              || campaign.campaignData.imageUrl == ""
                                            ? "images/logo_placeholder.png" : campaign.campaignData.imageUrl,
                "%campaignId%"              : campaign.campaignId,
                "%campaignName%"            : campaign.campaignData.name,
                "%campaignProceed%"         : campaign.proceed,
                "%presetData%"              : presetHtml
            }
        }

        finalHtml += campaignsTemplate.replace(/%\w+%/g, function(all) {
            if(typeof(campaignData[all]) != 'undefined')
                return campaignData[all];
            else
                return all;
        });
    })
    $("#campaignBreakDown").html(finalHtml);

    $(".transferBreadCrumb").on('click', function(){
       $('#campaignPieChartPage').hide();
       $('#transferPage').show();
    });
}

OrgMain.prototype.showTransferDetails = function(detailsData) {
    $('#transferPage').hide();
    $('#transferDetailsPage').show();
    var params = {"payoutId" : detailsData.id, "access_token": orgSignIn.getAccessToken()}

    $('#transferDate').text(OrgMain.prototype.dateString(detailsData.expectedDepositDate));

    $('#totalTransferAmount').text('$'+detailsData.proceed);

    api.makeApiRequest({
        type: "getPayoutDonations",
        data: params,
        success: function(data) {
            if ($.fn.DataTable.isDataTable("#allDonations")) {
                 var oTable = $("#allDonations").dataTable();
                 oTable.fnClearTable();
                 if (data.length > 0) {
                    oTable.fnAddData(data);
                    $('#totalDonation').text(data.length);
                    oTable.fnDraw();
                 }
            }
            else {
                $('#totalDonation').text(data.length);
                $("#allDonations").DataTable({
                      data: data,
                      order: [[ 0, "desc" ]],
                      autoWidth: false ,
                      bSort: false,
                      dom: "Btip",
                      "fnDrawCallback":function(){
                          if (Math.ceil((this.fnSettings().fnRecordsDisplay()) / this.fnSettings()._iDisplayLength) > 1) {
                              $('.dataTables_paginate').css("display", "block");
                              $('.dataTables_info').css("display", "block");
                          } else {
                              $('.dataTables_paginate').css("display", "none");
                              $('.dataTables_info').css("display", "none");
                          }
                      },
                      buttons: [{extend: 'excel', text: 'Export', title: 'Transfer Details'}],
                      columns: [
                            { "data": "amount", "render": function(data,type, row){
                                                return "$"+ (row.amount-(row.orgFee+row.payBeeFee)) }},
                            { "data": "amount", "render": function(data,type, row){
                                                 return "$"+row.amount }},
                            { "data": "updated", "render": function(data,type, row ){
                                                 return OrgMain.prototype.dateString(row.created); }},
                            { "data": "orgFee", "render": function(data,type, row){
                                                  return "$"+row.orgFee }},
                            { "data": "payBeeFee", "render": function(data,type, row){
                                                  return "$"+row.payBeeFee }}
                      ]
                });

                $(".transferBreadCrumb").on('click', function() {
                    $('#transferDetailsPage').hide();
                    $('#transferPage').show();
                });
            }
        },
        error: function(error){
            toastr.error(genericError)
        },
        expired: function() { orgSignIn.onInValidAccessToken() },
        extend: function() { orgSignIn.extendCookieLife() }
    });
}

OrgMain.prototype.showVolunteerManage = function() {
    var self = this
    self.setHeading("Manage volunteers")
    this.hideAll()

    $("#volunteer").show()

    $('#addNewVolunteer').off('click')
    $('#addNewVolunteer').on('click', function() {
        $('#addVolunteerModel').modal('show')
    });

    var getVolunteerStatus = function(volunteer) {
        switch(volunteer.volunteerStatus) {
            case 1:
            if(volunteer.handle != "") {
                return "<div class='green'>Active</div>"
            } else {
                return "<div class='orange'>Pending setup</div>"
            }
            case 2: return "<div class='orange'> Pending accept</div>"
            case 3: return "<div class='red'>Deleted</div>"
            default: return "<div class='red'>Unknown</div>"
        }
    }

    var onVolunteerFilerChange = function() {
        self.showVolunteerManage()
    }
    $("#volunteerFilter").off("change", onVolunteerFilerChange)
    $("#volunteerFilter").change(onVolunteerFilerChange)

    var isShowingAllVolunteers = function() {
        if($("#volunteerFilter").prop("checked")) {
            return false
        }
        else {
            return true
        }
    }

    var activeVolunteerList = function(allVolunteers) {
        var filteredList = []
        allVolunteers.forEach(function(volunteer) {
            if(volunteer.volunteerStatus == 1 && volunteer.handle != "") {
                filteredList.push(volunteer)
            }
        })
        return filteredList
    }

    api.makeApiRequest({
        type: "getVolunteers",
        data: {"access_token": orgSignIn.getAccessToken()},
        success: function(volunteerList) {
            self.filteredVolunteerList = volunteerList
            if(!isShowingAllVolunteers()) {
                self.filteredVolunteerList = activeVolunteerList(volunteerList)
            }

            if($.isArray(self.filteredVolunteerList) && self.filteredVolunteerList.length > 0) {
                if ($.fn.DataTable.isDataTable("#volunteerList")) {
                    var oTable = $("#volunteerList").dataTable()
                    oTable.fnClearTable()
                    oTable.fnAddData(self.filteredVolunteerList)
                    oTable.fnDraw()
                }
                else {
                    $("#volunteerList").dataTable({
                        data: self.filteredVolunteerList,
                        autoWidth: false,
                        order: [[ 2, "desc" ]],
                        dom: "Btfip",
                        buttons: [{extend: 'excel', text: 'Export', title : 'volunteerList'}],
                        columns: [
                            {
                                "data": "imageUrl",
                                "width": "10%" ,
                                "orderable" : false,
                                "searchable": false,
                                "render" : function (data, type, row) {
                                    return '<img height="50" src="'+data+'"/>'
                                }
                            },
                            {
                                "data": "name",
                                "width": "15%"
                            },
                            {
                                "data": "donated",
                                "width": "15%",
                                "searchable": false,
                                "render": function(raised) {
                                    return "$" + raised.toFixed(2)
                                }
                            },
                            {
                                "data": "pledged",
                                "searchable": false,
                                "width": "15%",
                                "render": function(pledges) {
                                    return "$" + pledges.toFixed(2)
                                }
                            },
                            {
                                "data": "volunteerStatus",
                                "width": "15%",
                                "searchable": false,
                                "render": function(status, type, row) {
                                    return getVolunteerStatus(row)
                                }
                            },
                            {
                                "data": "volunteerStatus",
                                "width": "15%",
                                "searchable": false,
                                "orderable" : false,
                                "render": function(data, type, row, meta ) {
                                    var buttonId = "detail_" + meta.row
                                    var actionHtml =  "<div class='row justify-content-center'> <div class='col'>"
                                    if(row.volunteerStatus == 1 && row.handle != "") {
                                        actionHtml += "<button id='delete_"
                                            + meta.row
                                            + "' onclick='orgMain.volunteerAction(this)'"
                                            + " class='btn btn-sm  btn-danger waves-effect waves-light'>"
                                            + "delete </button>"
//                                            + "<button onclick='orgMain.volunteerAction(this)' id='details_"
//                                            + meta.row
//                                            + "' class='btn btn-sm btn-info waves-effect waves-light'>"
//                                            + "Details </button>"
                                    }
                                    else if(row.volunteerStatus == 2
                                        || (row.volunteerStatus == 1 && row.handle == "")) {
                                        actionHtml += "<button id='resend_"
                                            + meta.row
                                            + "' onclick='orgMain.volunteerAction(this)' "
                                            + " class='btn btn-sm btn-info waves-effect waves-light'>resend</button>"
                                    }
                                    else if(row.volunteerStatus == 3) {
                                        actionHtml += "<button id='activate_"
                                            + meta.row
                                            + "' onclick='orgMain.volunteerAction(this)'"
                                            + "class='btn btn-sm btn-info waves-effect waves-light'>activate</button>"
                                    }

                                    actionHtml += "</div></div>"
                                    return actionHtml
                                }
                            }
                        ]
                    })
                }
            }
            else {
                $("#volunteerList").html("<tr style='height: 100px'><td></td><td style='padding-top: 40px'\
                    class='text-center purple-text'>No volunteers added to this account</td><td></td></tr>")
            }
        },
        error: function(error) {
            toastr.error(genericError)
        },
        expired: function() { orgSignIn.onInValidAccessToken() },
        extend: function() { orgSignIn.extendCookieLife() }
    })
}

OrgMain.prototype.volunteerAction = function(actionItem) {
    var self = this
    var idSplit = actionItem.id.split("_")
    var action = idSplit[0]
    var volunteer = self.filteredVolunteerList[parseInt(idSplit[1])]
    switch(action) {
        case "delete":
            var reqData = {"ouid": volunteer.id, "access_token": orgSignIn.getAccessToken()}
            api.makeApiRequest({
                type: "deleteVolunteer",
                data: reqData,
                success: function(respData) {
                    toastr.success("Volunteer marked as deleted")
                    self.showVolunteerManage()
                },
                error: function(error) {
                    toastr.error(genericError)
                },
                expired: function() { orgSignIn.onInValidAccessToken() },
                extend: function() { orgSignIn.extendCookieLife() }
            })
            break
        case "activate":
        case "resend":
            var reqData = {
                "access_token": orgSignIn.getAccessToken(),
                "uid" : volunteer.userId
            }

            api.makeApiRequest({
                type: "addVolunteer",
                data: reqData,
                success: function(result) {
                    toastr.success("Volunteer email notification sent")
                    self.showVolunteerManage()
                },
                error: function(error) {
                    toastr.error(genericError)
                },
                expired: function() { orgSignIn.onInValidAccessToken() },
                extend: function() { orgSignIn.extendCookieLife() }
            })
            break
        default:
            toastr.error(genericError)
            break
    }
}

//OrgMain.prototype.showVolunteerManage = function() {
//     this.hideAll()
//
//     $("#volunteer").show()
//     $('#addNewVolunteer').on('click', function(){
//        $('#addVolunteerModel').modal('show');
//     });
//
//     var volunteerTemplate = "<tr>\
//         <td class='campaign-list-td'>\
//             <div class='row'>\
//                 <div class='col'>\
//                     <img src='%volunteerImage%' style='height: 150px;' class='img-fluid z-depth-0'>\
//                 </div>\
//             </div>\
//             <div class='row justify-content-center'>\
//                 <div class='col'>\
//                     <button id='%volunteerDeleteId%' class='btn btn-sm  btn-danger waves-effect waves-light'><i class='fa fa-close' aria-hidden='true'></i></button>\
//                     <button id='' class='btn btn-sm btn-info waves-effect waves-light'><i class='fa fa-bar-chart' aria-hidden='true'></i></button>\
//                 </div>\
//             </div>\
//         </td>\
//         <td class='campaign-list-td'>\
//             <div class='row'>\
//                 <h5><strong>%volunteerName%</strong></h5>\
//             </div>\
//             <div class='row'>\
//                 <div class='green' id='%volunteerStatusId%'>%volunteerStatus%</div>\
//             </div>\
//             <div class='row'>\
//                 Raised: $%volunteerDonations%\
//             </div>\
//             <div class='row'>\
//                 Pledged: $%volunteerPledges%\
//             </div>\
//             <div class='row'>\
//                 <button id='%volunteerDeleteId%' class='btn btn-success btn-sm'>Activate</button>\
//             </div>\
//         </td>\
//         <td class='campaign-list-td'>\
//             <div class='campaign-list-qrcode'>\
//                 <div class='row'>\
//                     <div id='downloadImage_5936e3a34388a70fbad4d87e' style='width:260px; height: 150px; margin: auto'>\
//                         <div class='row text-center'>\
//                             <img src='images/scan_donate_done.png' style='padding-bottom: 5px; margin: auto'>\
//                         </div>\
//                         <div class='row text-center' style='margin: auto; padding-bottom: 10px'>\
//                             <a href='%volunteerQrImageHref%' style='margin: auto'>\
//                                 <img class='image' src='%volunteerQrImageSrc%' style='margin: auto'>\
//                                 <img src='images/powered_paybee.png'>\
//                             </a>\
//                         </div>\
//                         <div class='row pp-qrcode-url'>\
//                             <div class='margin-top' style='margin: auto'>\
//                                 <small style='color: #666'>URL:\
//                                     <a href='%volunteerQrImageHref%' style='color: #666'>%volunteerDispUrl%</a>\
//                                 </small>\
//                             </div>\
//                         </div>\
//                     </div>\
//                 </div>\
//                 <div class='row justify-content-center'>\
//                     <div class='col text-center'>\
//                         <button id='download_5936e3a34388a70fbad4d87e' class='btn btn-sm btn-primary waves-effect waves-light'>Download</button>\
//                     </div>\
//                 </div>\
//             </div>\
//         </td>\
//     </tr>"
//
//    var self = this
//    self.setHeading("Volunteers")
//    api.makeApiRequest({
//        type: "getVolunteers",
//        data: {"access_token": orgSignIn.getAccessToken()},
//        success: function(volunteerList) {
//            if($.isArray(volunteerList) && volunteerList.length > 0) {
//                var finalHtml = ""
//                volunteerList.forEach(function(volunteer, index) {
//                    var volunteerData = {
//                        "%volunteerImage%"          : volunteer.imageUrl,
//                        "%volunteerName%"           : volunteer.name,
//                        "%volunteerDonations%"      : volunteer.donated.toFixed(2),
//                        "%volunteerPledges%"        : volunteer.pledged.toFixed(2),
//                        "%volunteerQrImageHref%"    : volunteer.qrUrl,
//                        "%volunteerQrImageSrc%"     : volunteer.qrImageUrl,
//                        "%volunteerStatusId%"       : "status_" + volunteer.id
//                    }
//
//                    var urlSplits = volunteer.qrUrl.split("//")
//                    if(urlSplits.length == 2) {
//                        volunteerData["%volunteerDispUrl%"] = urlSplits[1]
//                    }
//                    else {
//                        volunteerData["%volunteerDispUrl%"] = ""
//                    }
//
//                    if(volunteer.handle == "") {
//                        volunteerData["%hidden%"] = 'style="visibility: hidden"'
//                    }
//
//                    if(volunteer.volunteerStatus == 1) {
//                        volunteerData["%volunteerStatus%"]      = "active"
//                        volunteerData["%volunteerDeleteId%"]    = "delete_" + volunteer.id
//                        volunteerData["%button_action%"]        = "Delete"
//                    }
//                    else if(volunteer.volunteerStatus == 2) {
//                        volunteerData["%volunteerStatus%"]      = "pending"
//                        volunteerData["%button_action%"]        = ""
//                    }
//                    else if(volunteer.volunteerStatus == 3) {
//                        volunteerData["%volunteerStatus%"] = "deleted"
//                        volunteerData["%volunteerDeleteId%"]    = "add_" + volunteer.userId
//                        volunteerData["%button_action%"]        = "Activate"
//                    }
//                    else volunteerData["%volunteerStatus%"] = "unknown"
//
//                    finalHtml += volunteerTemplate.replace(/%\w+%/g, function(all) {
//                        if(typeof(volunteerData[all]) != 'undefined') return volunteerData[all];
//                        else return all;
//                    });
//                })
//                $("#volunteerList").html(finalHtml)
//                $("button[id^='delete_']").click(function(){
//                    var idToDelete = this.id.split("_")[1]
//                    var reqData = {"ouid":idToDelete, "access_token": orgSignIn.getAccessToken()}
//                    api.makeApiRequest({
//                        type: "deleteVolunteer",
//                        data: reqData,
//                        success: function(respData) {
//                            $("#" + "delete_" + idToDelete).hide()
//                            $("#status_" + idToDelete).text("Inactive")
//                        },
//                        error: function(error) {
//                            toastr.error(genericError)
//                        },
//                        expired: function() { orgSignIn.onInValidAccessToken() },
//                        extend: function() { orgSignIn.extendCookieLife() }
//                    })
//                })
//                $("button[id^='add_']").click(function() {
//                    var idToAdd = this.id.split("_")[1]
//                    var reqData = {
//                        "access_token": orgSignIn.getAccessToken(),
//                        "uid" : idToAdd
//                    }
//
//                    api.makeApiRequest({
//                        type: "addVolunteer",
//                        data: reqData,
//                        success: function(result) {
//                            $("#status_" + idToAdd).text("Pending")
//                            $("#" + "add_" + idToAdd).hide()
//                        },
//                        error: function(error) {
//                            toastr.error(genericError)
//                        },
//                        expired: function() { orgSignIn.onInValidAccessToken() },
//                        extend: function() { orgSignIn.extendCookieLife() }
//                    })
//                })
//            }
//            else {
//                $("#volunteerList").html("<tr style='height: 100px'><td></td><td style='padding-top: 40px'\
//                     class='text-center purple-text'>No volunteers added to this account</td><td></td></tr>")
////                $("#volunteerList").html("<div class='row text-center'>No volunteers added to this account</div>")
//            }
//        },
//        error: function(error) {
//            toastr.error(genericError)
//        },
//        expired: function() { orgSignIn.onInValidAccessToken() },
//        extend: function() { orgSignIn.extendCookieLife() }
//    })
//}

OrgMain.prototype.addVolunteer = function(e) {
    var self = this
    var email = utils.getElementValueTrimmed("volunteerEmail")

    if(email == "" ) {
        orgUtil.setInputError("volunteerEmail", "Please provide email id to add")
        return false
    }

    if(document.getElementById("volunteerEmail").checkValidity() == false) {
        orgUtil.setInputError("volunteerEmail", "Invalid Email")
        return false
    }

    var reqData = {
        "access_token": orgSignIn.getAccessToken(),
        "email" : email
    }

    api.makeApiRequest({
        type: "addVolunteer",
        data: reqData,
        success: function(result) {
            $('#addVolunteerModel').modal('toggle');
            self.showVolunteerManage()
        },
        error: function(error) {
            switch(error.errorCode) {
                case "InvalidEmail":
                    orgUtil.setInputError("volunteerEmail", "Invalid Email")
                    return false
                default:
                    toastr.error(genericError)
                    return false
            }
        },
        expired: function() { orgSignIn.onInValidAccessToken() },
        extend: function() { orgSignIn.extendCookieLife()}
    })

    if(e != undefined) {e.preventDefault()}
}

OrgMain.prototype.addValueToInput = function(inputElem, val) {
    if(val != undefined && val != "") {
        $("#" + inputElem).val(val)
        $("#" + inputElem + "Label").addClass("active")
    }
}

OrgMain.prototype.showAccountManage = function() {
    var self = this
    self.hideAll()
    self.setHeading("Manage Account")

    if(localOrgData.user.imageUrl != undefined && localOrgData.user.imageUrl != ""){
        $("#accountUserImage").attr('src', localOrgData.user.imageUrl)
    }

    if(localOrgData.user.logoUrl != undefined && localOrgData.user.logoUrl != "") {
        $("#accountLogo").attr('src', localOrgData.user.logoUrl)
    }

    self.addValueToInput("accountEmail", localOrgData.user.email)
    self.addValueToInput("accountMission", localOrgData.user.purpose)
    self.addValueToInput("accountUrl", localOrgData.user.url)
    self.addValueToInput("accountDescription", localOrgData.user.desc)
    self.addValueToInput("accountName", localOrgData.user.name)

    $("#accountUpdateButton").prop('disabled', true)

    var enableUpdateButton = function() {
        $("#accountUpdateButton").prop('disabled', false)
    }

    $('#accountEmail').off("change", enableUpdateButton)
    $('#accountEmail').change(enableUpdateButton)

    $('#accountName').off("change", enableUpdateButton)
    $('#accountName').change(enableUpdateButton)

    $('#accountMission').off("change", enableUpdateButton)
    $('#accountMission').change(enableUpdateButton)

    $('#accountUrl').off("change", enableUpdateButton)
    $('#accountUrl').change(enableUpdateButton)

    $('#accountDescription').off("change", enableUpdateButton)
    $('#accountDescription').change(enableUpdateButton)

    $("#account").show()
}


OrgMain.prototype.uploadOrgImage = function(selectedImage, imageDisplay) {
    var self = this
    orgUtil.uploadImage({
        onSuccess: function(imageUrl) {
            self.orgCoverImage = imageUrl
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

OrgMain.prototype.uploadLogoImage = function(selectedImage, imageDisplay) {
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

OrgMain.prototype.updateOrgInfo = function() {
    var self = this

    var params = {}
    var name = utils.getElementValueTrimmed("accountName")
    var email = utils.getElementValueTrimmed("accountEmail")
    var mission = utils.getElementValueTrimmed("accountMission")
    var url = utils.getElementValueTrimmed("accountUrl")
    var desc = utils.getElementValueTrimmed("accountDescription")

    var requiredUpdate = false
    if(email != localOrgData.user.email && utils.validateEmail(email)) {
        params["email"] = email
        requiredUpdate = true
    }
    if(name != "" && localOrgData.user.name != name) {
        params["name"] = name
        requiredUpdate = true
    }

    if(mission != localOrgData.user.purpose) {
        params["purpose"] = mission
        requiredUpdate = true
    }

    if(url != localOrgData.user.url) {
        params["url"] = url
        requiredUpdate = true
    }

    if(desc != localOrgData.user.desc) {
        params["desc"] = desc
        requiredUpdate = true
    }

    if(self.logoImageUrl != "") {
        params["logoUrl"] = self.logoImageUrl
        requiredUpdate = true
    }

    if(self.orgCoverImage != "") {
        params["imageUrl"] = self.orgCoverImage
        requiredUpdate = true
    }

    if(!requiredUpdate) {
        toastr.warning("Nothing to update")
        return false
    }

    api.makeApiRequest({
        type: "orgUpdate",
        data: {'p' : JSON.stringify(params),"access_token": orgSignIn.getAccessToken()},
        success: function(response) {
            toastr.success("Account information updated")
            $("#accountUpdateButton").prop('disabled', true)
            orgSignIn.getOrgUserData(
                function(){},
                function(){}
            )
        },
        error: function(error) {
            switch(error.errorCode) {
                case "OrgNameTooLong":
                    orgUtil.setInputError("accountName", "Account name too long")
                    break
                case "OrgDescTooLong":
                    orgUtil.setInputError("accountDescription", "Description too long")
                    break
                case "OrgPurposeTooLong": break
                    orgUtil.setInputError("accountMission", "Mission statement too long")
                    break
                case "InvalidEmail": break
                    orgUtil.setInputError("accountEmail", "Invalid email id")
                    break
                case "UserAlreadyExist":
                    orgUtil.setInputError("accountEmail", "User with this email already exists")
                    break
                default:
                    toastr.error(genericError)
                    break
            }
        },
        expired: function() { orgSignIn.onInValidAccessToken() },
        extend: function() { orgSignIn.extendCookieLife() }
    })
    return false
}

OrgMain.prototype.showLegalDoc = function(docType) {
    var self = this
    self.setHeading("Legal")
    $("#btnPP").parent('li').removeClass("active");
    $("#btnTOS").parent('li').removeClass("active");
    $("#btnFee").parent('li').removeClass("active");
    if(docType == "pp") {
        $('#legalPage').attr('data','/pp.html'); $('#legalPage').load('/pp.html');
        $("#btnPP").parent('li').addClass("active")
    }
    else if(docType == "tos") {
        $('#legalPage').attr('data','/tos.html'); $('#legalPage').load('/tos.html');
        $("#btnTOS").parent('li').addClass("active")
    }
    else if(docType == "fee") {
        $('#legalPage').attr('data','/fee.html'); $('#legalPage').load('/fee.html');
        $("#btnFee").parent('li').addClass("active")
    }
    else {
        return
    }
}

OrgMain.prototype.setupQRDownload = function(type, id, url, fileName, size) {
    var self = this

    var imageUrl100 = "images/qr_default.png"
    var imageUrl200 = "images/qr_default2x.png"
    var imageUrl400 = "images/qr_default4x.png"

    if(type == "org") {
        imageUrl100 = "/api/qr_code?size=100" + "&payee=" + id
        imageUrl200 = "/api/qr_code?size=200" + "&payee=" + id
        imageUrl400 = "/api/qr_code?size=400" + "&payee=" + id
    }
    else if(type == "campaign"){
        imageUrl100 = "/api/pp_code?size=100" + "&pp=" + id
        imageUrl200 = "/api/pp_code?size=200" + "&pp=" + id
        imageUrl400 = "/api/pp_code?size=400" + "&pp=" + id
    }
    else {
        return
    }

    $("#donateUrl100").text("URL: " + url)
    $("#donateUrl200").text("URL: " + url)
    $("#donateUrl400").text("URL: " + url)
    $("#qrImage100").prop("src", imageUrl100)
    $("#qrImage200").prop("src", imageUrl200)
    $("#qrImage400").prop("src", imageUrl400)

    var setupDownload = function(divId, fileName, buttonId) {
        var element = $('#' + divId)
        var getCanvas
        html2canvas(element, {
            onrendered: function (canvas) {
                getCanvas = canvas;
                var imageData = getCanvas.toDataURL("image/png", 1.0);
                var newData = imageData.replace(/^data:image\/png/, "data:application/octet-stream");
                $("#" + buttonId).attr("download", fileName + ".png").attr("href", newData);
            }
        });
    }

    var showSizeBlock = function(size) {
        $("#showQrSmall").removeClass("active");
        $("#showQrMed").removeClass("active");
        $("#showQrLarge").removeClass("active");

        $("#smallQRBlock").hide()
        $("#medQRBlock").hide()
        $("#largeQRBlock").hide()

        if(size == "small") {
            $("#showQrSmall").addClass("active")
            $("#smallQRBlock").show()
        }
        else if(size == "med") {
            $("#showQrMed").addClass("active")
            $("#medQRBlock").show()
        }
        else if(size == "large") {
            $("#showQrLarge").addClass("active")
            $("#largeQRBlock").show()
        }
    }

    $("#showQrSmall").off("click")
    $("#showQrSmall").click(function() {
        showSizeBlock("small")
        setupDownload('qrDownload100', fileName, "qrDownload100Button")
    })

    $("#showQrMed").off("click")
    $("#showQrMed").click(function() {
        showSizeBlock("med")
        setupDownload('qrDownload200', fileName, "qrDownload200Button")
    })

    $("#showQrLarge").off("click")
    $("#showQrLarge").click(function() {
        showSizeBlock("large")
        setupDownload('qrDownload400', fileName, "qrDownload400Button")
    })

    $('#qrDownloadModel').modal('show')
    $('#qrDownloadModel').off('shown.bs.modal')
    $('#qrDownloadModel').on('shown.bs.modal', function() {
        showSizeBlock("med")
        setupDownload('qrDownload200', fileName, "qrDownload200Button")
    })

}


var orgMain = new OrgMain()

var BI = function(){
}

BI.prototype.updateActivity = function(type) {
    function aggregateByMonth(data) {
        var aggregatedData = d3.nest()
            .key(function(d) {return d3.time.format('%b %Y')(new Date(d.x)) })
            .rollup(function(values) {
                return d3.sum(values, function(d) { return d.y; });
            })
            .map(data)
        var dataArray = []
        for (var x in aggregatedData) {
            dataArray.push({"x": x, "y" : aggregatedData[x]})
        }
        return dataArray
    }

    function aggregateByWeek(data) {
        var aggregatedData = d3.nest()
            .key(function(d) {return d3.time.format('Week %U %Y')(new Date(d.x)) })
            .rollup(function(values) {
                return d3.sum(values, function(d) { return d.y; });
            })
            .map(data)
        var dataArray = []
        for (var x in aggregatedData) {
            dataArray.push({"x": x, "y" : aggregatedData[x]})
        }
        return dataArray
    }

    $("#aggType").text(type)

    api.makeApiRequest({
        type: "biActivity",
        data: {"access_token": orgSignIn.getAccessToken(), "type": type},
        success: function(dailyActivityData) {
             nv.addGraph(function() {
                 var chart = nv.models.multiBarChart()
                     .margin({left: 30, bottom: 20, right: 0})
                     .showLegend(false);
                 chart.yAxis
                     .showMaxMin(false)
                     .ticks(0)
                     .tickFormat(d3.format(',.f'));

                if(type == "daily") {
                     chart.xAxis
                         .showMaxMin(false)
                         .tickFormat(function(d) { return d3.time.format('%b %d')(new Date(d)) });
                }
                else if(type == "monthly") {
                    chart.xAxis
                        .showMaxMin(false)
                        .tickFormat(function(d) { return d});
                    dailyActivityData[0].values = aggregateByMonth(dailyActivityData[0].values)
                    dailyActivityData[1].values = aggregateByMonth(dailyActivityData[1].values)
                }
                else if(type == "weekly") {
                    chart.xAxis
                        .showMaxMin(false)
                        .tickFormat(function(d) { return d});
                    dailyActivityData[0].values = aggregateByWeek(dailyActivityData[0].values)
                    dailyActivityData[1].values = aggregateByWeek(dailyActivityData[1].values)
                }

                d3.select('#sources-chart-bar svg')
                 .datum(dailyActivityData)
                 .transition().duration(500).call(chart);

                chart.update()
                barChart = chart;

                return chart;
           });
        },
        error: function(error) {
            toastr.error(genericError)
        },
        expired: function() { orgSignIn.onInValidAccessToken() },
        extend: function() { orgSignIn.extendCookieLife() }
    })
}

var bi = new BI()

//var CampaignDonation = function() {
//    this.donationTemplate = "<tr>\
//        <td class='hidden-xs'></td>\
//        <td>\
//            <img class='img-rounded' src='%donorImageUrl%' alt='' height='50'>\
//        </td>\
//        <td>\
//            %donorName%\
//        </td>\
//        <td>\
//            %volunteerName%\
//        </td>\
//        <td class='hidden-xs text-muted'>\
//            %date%\
//        </td>\
//        <td class='text-muted'>\
//            $%amount%\
//        </td>\
//        <td class='width-150'>\
//            %additionalInfo%\
//        </td>\
//    </tr>"
//
//    this.optionsTemplate = "%number%.&nbsp&nbsp<a id='%optionLinkId%' style='margin: 0px 15px 10px 15px'>%optionName%</a><br>"
//}
//
//CampaignDonation.prototype.loadCampaignDonation = function(campaignId) {
// var self = this
//    //get org user data
//    orgSignIn.getOrgUserData(
//        function() {
//            api.makeApiRequest({
//                type: "getPaymentPoint",
//                data: {"access_token": orgSignIn.getAccessToken(), "ppid": campaignId},
//                success: function(campaignData) {
//                    var pledgePresets = campaignData.campaignTypeData == null ? "undefined": campaignData.campaignTypeData.presetOptions;
//                    if(pledgePresets != "undefined" && pledgePresets.length > 0) {
//                        var optionsHtml = ""
//                        var presetCount = 1
//                        pledgePresets.forEach(function(preset) {
//                            var optionsData = {
//                                "%optionLinkId%": campaignData.intid + "_" + preset.id,
//                                "%optionName%"  : preset.name,
//                                "%number%"      : presetCount
//                            }
//                            optionsHtml += self.optionsTemplate.replace(/%\w+%/g, function(all) {
//                                if(typeof(optionsData[all]) != 'undefined') return optionsData[all];
//                                else return all;
//                            });
//                            presetCount++
//                        })
//                        $("#campaignDonationName").text(campaignData.name)
//                        $("#campaignOptionList").html(optionsHtml)
//
//                        pledgePresets.forEach(function(preset) {
//                            $("#" + campaignData.intid + "_" + preset.id).click(function(){
//                                var ids = this.id.split("_")
//                                self.seDonations(ids[0], ids[1], $("#"+ this.id).html(), false)
//                            })
//                        })
//                        self.seDonations(campaignData.intid, pledgePresets[0].id, pledgePresets[0].name, false)
//                    }
//                },
//                error: function(error) {
//                    toastr.error(genericError)
//                },
//                expired: function() { orgSignIn.onInValidAccessToken() },
//                extend: function() { orgSignIn.extendCookieLife() }
//            })
//        },
//        function(error) {
//            toastr.error(genericError)
//        }
//    )
//
//    $("#cashDonations").click(function(){
//       self.seDonations(0, "", "", true)
//    })
//}
//
//CampaignDonation.prototype.volunteerName = function (row){
//    if(row.volunteerInfo != undefined)
//        return row.volunteerInfo.name;
//    else
//        return "";
//}
//
//CampaignDonation.prototype.seDonations = function(campaignId, presetId, presetName, isCash) {
//    var self = this
//
//    var params = {"access_token": orgSignIn.getAccessToken()}
//    if(isCash) {
//        params["campaignIntId"] = ""
//        params["presetId"]  = ""
//        params["donationType"] = "cash"
//    }
//    else {
//        params["campaignIntId"] = campaignId
//        params["presetId"]  = presetId
//        params["donationType"] = ""
//    }
//
//    api.makeApiRequest({
//        type: "getDonations",
//        data: params,
//        success: function(donationList) {
//         if ( $.fn.DataTable.isDataTable("#campaignDonationList") ) {
//             var oTable = $("#campaignDonationList").dataTable();
//             oTable.fnClearTable();
//             if (donationList.length > 0) {
//                oTable.fnAddData(donationList);
//                oTable.fnDraw();
//             }
//         } else {
//            $("#campaignDonationList").dataTable({
//                        data: donationList,
//                        autoWidth: false ,
//                        order: [[ 5, "desc" ]],
//                        dom: "Btip",
//                        buttons: [{extend: 'excel', text: 'Export', title : 'Campaign Details'}],
//                        columns: [
//                            { "data": "payer.image",  "width": "10%" , "orderable" : false, "render" : function (data, type, row) {
//                                                                    return '<img height="50" class="img-rounded" src ="'+data+'"/>'}},
//                            { "data": "payer.name",  "width": "15%"  },
//                            { "data": "volunteerInfo",  "width": "15%", "render": function(data, type, volunteerInfo){ return CampaignDonation.prototype.volunteerName(volunteerInfo);}},
//                            { "data": "status",   "width": "13%" , "render": function(status){return OrgMain.prototype.donationStatus(status);}},
//                            { "data": "method",  "width": "12%"   },
//                            { "data": "created", "sType": "date", "width": "13%" ,  "render": function(data,type, row ){return OrgMain.prototype.dateTimeString(row.created); } },
//                            { "data": "amount",  "width": "12%"  },
//                            { "data": "campaignAdditionalInfo", "width": "10%"}
//                        ]
//                    })
//            }
//
//            if(isCash){
//                $("#selectedOption").text("Cash Donations")
//            } else {
//                $("#selectedOption").text(presetName)
//            }
//
//            $(".searchIcon").click(function(e){
//                    var  id = $(this).attr('id');
//                        event.stopPropagation();
//                        $(".columnSearch").css("visibility", "hidden");
//                        $(".text_filter").val("");
//                        var oTable = $("#campaignDonationList").dataTable();
//                        var oSettings = oTable.fnSettings();
//                        for(iCol = 0; iCol < oSettings.aoPreSearchCols.length; iCol++) {
//                        oSettings.aoPreSearchCols[ iCol ].sSearch = '';
//                        }
//                        oSettings.oPreviousSearch.sSearch = '';
//                        oTable.fnDraw();
//                        $("#filter"+id).css("visibility", "visible");
//                        $(".text_filter").val("search...");
//                     });
//
//        },
//        error: function(error) {
//            toastr.error(genericError)
//        },
//        expired: function() { orgSignIn.onInValidAccessToken() },
//        extend: function() { orgSignIn.extendCookieLife() }
//    })
//}
//
//var campaignDonation = new CampaignDonation()

