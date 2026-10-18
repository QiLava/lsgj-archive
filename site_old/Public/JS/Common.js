var SiteRoot="/";
Request = {
    QueryString: function (item) {
        var svalue = location.search.match(new RegExp("[\?\&]" + item + "=([^\&]*)(\&?)", "i"));
        return svalue ? svalue[1] : svalue;
    }
}//alert(Request.QueryString("id"));
var _get = function (id) {
    return document.getElementById(id);
};

var _goto = function (url) {
    window.location.href = url;
};

function _random() {
    var rnd = "";
    for (var i = 0; i < 10; i++)
        rnd += Math.floor(Math.random() * 10);
    return rnd;
}
function _refresh() { window.location.reload(false); }
function _isNull(obj) {
    if (typeof (obj) == "undefined") return true;
    if (obj == undefined) return true;
    if (obj == null) return true;
    if (obj == "") return true;
    return false
}
//exfpopup    begin
// onchange 事件时（等同于 失去焦点），提示并限制字符数  
function taCheckOnChange(taId, maxSize) {
    var defaultMaxSize = getDefaultMaxSize();
    var ta = document.getElementById(taId);
    if (!ta) {
        return;
    }
    if (!maxSize) {
        maxSize = defaultMaxSize;
    } else {
        maxSize = parseInt(maxSize);
        if (!maxSize || maxSize < 1) {
            maxSize = defaultMaxSize;
        }
    }
    var taTipDiv = document.getElementById("taTipDiv");
    taTipDiv.innerHTML = ("当前字符数：" + ta.value.length + "，字数限制：" + maxSize);
    if (ta.value.length > maxSize) {
        alert("当前字数 " + ta.value.length + " ，超过最大字符限制数 " + maxSize + " ，点击 \"确定\" 将自动截断。");
        tata.value = ta.value.substring(0, maxSize);
        taTipDiv.innerHTML = ("当前字数：" + ta.value.length + "，字数限制：" + maxSize);
    }
}
// 当键盘输入时，提示并限制字符数  
function taCheckOnKeyUp(taId, maxSize) {
    var defaultMaxSize = getDefaultMaxSize();
    var ta = document.getElementById(taId);
    if (!ta) {
        return;
    }
    if (!maxSize) {
        maxSize = defaultMaxSize;
    } else {
        maxSize = parseInt(maxSize);
        if (!maxSize || maxSize < 1) {
            maxSize = defaultMaxSize;
        }
    }
    if (ta.value.length > maxSize) {
        ta.value = ta.value.substring(0, maxSize);
    }
    var taTipDiv = document.getElementById("taTipDiv");
    taTipDiv.innerHTML = ("当前字数：" + ta.value.length + "，字数限制：" + maxSize);
}
function getDefaultMaxSize() {
    return 300;
}
function StringToArray(str, substr) {
    /* 函数功能：字符串按照指定字符串分割转换为数组 
    参数: 
    str :需转换的字符串 
    substr:分割字符串 
    返回值: 
    转换后的数组 
    */
    var arrTmp = new Array();
    if (substr == "") {
        arrTmp.push(str);
        return arrTmp;
    }
    var i = 0, j = 0, k = str.length;
    while (i < k) {
        j = str.indexOf(substr, i);
        if (j != -1) {
            if (str.substring(i, j) != "") { arrTmp.push(str.substring(i, j)); }
            i = j + 1;
        } else {
            if (str.substring(i, k) != "") { arrTmp.push(str.substring(i, k)); }
            i = k;
        }
    }
    return arrTmp;
}

function ArrayToString(arr, str) {
    /* 函数功能：数组根据分割字符（串）转换为字符串 
    参数: 
    arr:需转换的字符串数组 
    str:分割字符串 
    返回值: 
    转换后的字符串 
    */
    var strTmp = "";
    for (var i = 0; i < arr.length; i++) {
        if (arr[i] != "") {
            if (strTmp == "") {
                strTmp = arr[i];
            } else {
                strTmp = strTmp + str + arr[i];
            }
        }
    }
    return strTmp;
} 

function Alert(txt) {
    $.exfpopup.msgbox(txt);
}
function ErrAlert(txt) {
    $.exfpopup.msgbox(txt, 2);
}
function OpenUrl(_url, _title, _width) {
    // $.exfpopup.url("demo_url.htm", { id: "eurl", title: "自定义的标题", width: 400 });
    $.exfpopup.url(_url, { id: "eurl", title: _title, width: _width });
}

function MsgBox(t, txt) {
    switch (t) {
        case "success":
            jSuccess(txt, {
                VerticalPosition: 'center',
                HorizontalPosition: 'center'
            });
            break;
        case "notice":
            jNotify(txt, {
                VerticalPosition: 'center',
                HorizontalPosition: 'center'
            });
            break;
        case "error":
            jError(txt, {
                VerticalPosition: 'center',
                HorizontalPosition: 'center'
            });
            break;
    }

}

function AjaxPostData(MethodName, datas, CallFun) {
    $.ajax({
        type: "POST",
        url: SiteRoot + "Ajax/Default.aspx?XmlType=" + MethodName,
        data: datas,
//        beforeSend: function () {top.ShowLoading("正在处理请稍等..."); },
//        complete: function () { top.HideLoading(); },
        success: function (msg, textStatus) {
            // $("#textarea").val(msg);
            CallFun(msg);
        },
        error: function (msg) {
            //$("#textarea").val(msg.responseText);
             alert(msg.responseText);
            return;
        }
    });
}



function LoginOutServer() {
	  AjaxPostData("jsLogout", "", function (m){ });
	  _refresh();
}


function LoginServer() {
    var datas = "u=" + $("#U_username").val() + "&p=" + $("#P_password").val();
	AjaxPostData("LoginServer", datas, function (m){ 
			 switch (m.toString()) {
                case "0":
                    alert("对不起,您输入的用户名不存在!");
                    break;
                case "1":
                    alert("对不起,用户名对应的密码不对!");
                    break;
                case "2":
                   // Alert("登录成功！");
                    IsLogin();
                    break;
                case "4":

                    break;
                case "10":
                    alert("对不起,输入的验证码不对!");
                    break;
                default:
                   alert("登录成功！");
                     //$("#LoginInfo").html(result);
                    break;
                }								 
		   });
    //$('.loader').hide();
    return false;
}

//$.exfpopup.msgbox("你真的要保存吗？", 3, function () { alert("保存"); }, function () { alert("不保存"); })

//exfpopup   end   JsKtlHtml
function jsDebug(t)
{
  if($ ("#textarea")){
	 $("#textarea").show();
	 $("#textarea").val(t);
   }else{
	   
	   
	   }
	
}

jQuery.fn.outerHTML = function(s) {   
    return (s)? this.before(s).remove(): jQuery("<p>").append(this.eq(0).clone()).html();   
}  

function IsLogin() {
      $(".JsLoginUser").each(
		  function (name, object) {
		    $.ajax({
				  type: "POST",
				  url: SiteAppPath + "Ajax/SearchJson.ashx",
				  data: "ktlHtml=" + object.id + "&jsonType=ktlHtml",
				  beforeSend: function () { },
				  complete: function () { },
				  success: function (msg) {
					 if (msg!="0"){
					   $(object).outerHTML(msg);
					    //alert(msg);
					   $(".FalseLogin").hide(); 
					   $(".TrueLogin").show(); 
					 }
				  },
				  error: function (xhr, ajaxOptions, thrownError) {
					  alert(xhr.statusText);
					  //$("#textarea").val(xhr.responseText + xhr.statusText); //
					  return;
				  }
		       });
	 });
}
function getKtlHtml() {
    $(".JsKtlHtml").each(
       function (name, object) {
		  // alert(object.id);
        $.ajax({
            type: "POST",
            url: SiteAppPath + "Ajax/SearchJson.ashx",
            data: "ktlHtml=" + object.id + "&jsonType=ktlHtml",
            beforeSend: function () { $("#Data_Loading").show(); },
            complete: function () { $("#Data_Loading").hide(); },
            success: function (msg) {
				//$(object).after(msg); 
				  $(object).outerHTML(msg);
            },
            error: function (xhr, ajaxOptions, thrownError) {
                alert(xhr.statusText);
                //$("#textarea").val(xhr.responseText + xhr.statusText); //
                return;
            }
        });
      });
}
$(document).ready(function () {
				IsLogin() ;
				getKtlHtml();
				JsCreateHtml();
    });

function addmyvideolist(t, VId) {
    AjaxPostData("AddUserFavorite", "T=" + t + "&PkId=" + VId, function (d) {
        if (d == 0) {
            alert("您已收藏过了");
        }
        else {
            alert("收藏成功！");
        }
    });
    
 }

 function JsCreateHtml() {
     if (typeof (TemplateId) != 'undefined') {
         try {
             if (!_isNull(TemplateId)) {
                 //alert(TemplateId);
                 AjaxPostData("JsCreateHtml", "TempId=" + TemplateId, function (m) { });
             }
         }
         catch (e) {  }
     }
 }


function tabFun(tabId) {
    $("#" + tabId + "-title li").mouseover(function () {
		$(this).css("borderBottom","#FFFFFF 1px solid").siblings().css("borderBottom","");
        $(this).addClass("tabselected").siblings().removeClass();
        $("#" + tabId + "-content > .tabContent").eq($("#" + tabId + "-title li").index(this)).show().siblings().hide();
    });
}
//  $('#tab-title span').click(function(){
//	$(this).addClass("selected").siblings().removeClass();
//	$("#tab-content > ul").slideUp('1500').eq($('#tab-title span').index(this)).slideDown('1500');
//});



function So_formatSize(n) {
    if (!n) return "";
    var l2 = Math.ceil((n.toString().length - 3) / 3);
    var p = ["字节", "K", "M", "G"];
    var s2 = (n / Math.pow(1024, l2)).toString().substr(0, 4);
    if ("." == s2.substr(3)) s2 = s2.substr(0, 3);
    return s2 + p[l2];
}
 
 

var $_JS_LOADED = []; 
function $import(type, src) {
    if (!$_JS_LOADED[src]) {
        if (type == "js") {
            try {
                var xhr = window.ActiveXObject ? new ActiveXObject("Microsoft.XMLHTTP") : new XMLHttpRequest();
                xhr.open("GET", src, false);
                xhr.send(null);

                if (200 == xhr.status || 0 == xhr.status) {
                    if (window.execScript)
                        window.execScript(xhr.responseText);
                    else window.eval.call(window, xhr.responseText);
                }
                $_JS_LOADED[src] = true;
            } catch (e) {
                alert('系统错误: 加载文件"' + src + '"出错! \r\n[在第 ' + e.lineNumber + ' 行出现 ' + e.message + ' 错误]');
            }
        } else if (type == "css") {
            var css = document.createElement("link");
            css.setAttribute("rel", "stylesheet");
            css.setAttribute("type", "text/css");
            css.setAttribute("href", src);
            if (typeof css != "undefined") {
                document.getElementsByTagName("head")[0].appendChild(css);
                $_JS_LOADED[src] = true;
            } else {
                alert('系统错误: 加载文件"' + src + '"出错!');
            }
        }
    }
}

