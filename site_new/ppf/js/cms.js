/*cms所需js
* 2017-4-26
*/
//判断是否已引用jquery
if(typeof(jQuery)=="undefined"){
	document.write('<script src="/ppf/js/jquery.min.js"></script>');
}
//1.跳转外部地址时打开新窗口
$("[href]").each(function(){
   var href=$(this).attr("href");
   if(href!=''){
	   if(href.indexOf("http")!='-1'){
		   $(this).attr("target","_blank");
	   }
   }
})
//2.js飘窗<%adv(piao1)%>
/** 
 * 在网页中实现飘窗的功能 
 * 可以自定义： 
 * 窗口的起始位置：posLeft，posTop 
 * 飘窗的大小：width，height 
 * 飘窗的图片url，文字text以及连接link的值 
 * 标签模板如下
 * <script>
      var cms_piao1 = new FloatWindow();  
      var cms_option_piao1 = {  
		  posLeft: '0px',  
		  posTop: '0px',  
		  width: '100px',  
		  height: '200px',  
		  href: 'http://www.baidu.com',  
		  target: '_blank',  
		  url: '/error/pic.jpg',  
		  text: '我是text',
          speed: '10'		  
	 };  
	 cms_piao1.init(cms_option_piao1);  
	 cms_piao1.work(); 
   </script>
 *
 *
 *
 *
 */  
function FloatWindow() {  
    this.domDiv;  
    this.nWidth;  
    this.nHeight;  
    this.oTimer;
    this.speed;	
    this.oDirection = {  
        x: 1,  
        y: -1  
    };  
};  
FloatWindow.prototype = {  
    init: function (option) {  
        if (typeof option === 'undefined') {  
            option = {};  
        }  
        var opt = option;  
  
        var sPosLeft = opt.posLeft || '0px',  
            sPosTop = opt.posTop || '0px',  
            sWidth = opt.width || '100px',  
            sHeight = opt.height || '100px',  
            nZIndex = opt.zIndex || '999',  
            sHref = opt.href || '',  
            sTarget = opt.target || '_blank',  
            sUrl = opt.url || '',  
            sText = opt.text || '';
            this.speed = opt.speed || '1';
            sHex = opt.hex || '#FFFFFF';			
  
        var domDiv = document.createElement('div');  
		domDiv.setAttribute("class", "cms_adv");
        domDiv.style.position = 'fixed';  
        domDiv.style.left = sPosLeft;  
        domDiv.style.top = sPosTop;  
        domDiv.style.zIndex = nZIndex;  
        domDiv.style.width = sWidth;  
        domDiv.style.height = sHeight; 
  
        var that = this;  
        bindEvent(domDiv, 'mouseenter', function () {  
            clearInterval(that.oTimer);  
        });  
        bindEvent(domDiv, 'mouseleave', function () {  
            that.work();  
        });  
        
		var domContent = document.createElement('div');
		domContent.style.width = sWidth;
		domContent.style.height = sHeight; 
        domContent.style.cursor = 'pointer'; 
		var div1_style='width:'+sWidth+';height:'+sHeight+';position:absolute;background:'+sHex+';z-index:-99';
		var img_style='width:'+sWidth+';height:'+sHeight+';position:absolute;z-index:-99';
         
        if(sUrl==''){
			domContent.innerHTML = '<div style="'+div1_style+'"></div><div style="width:100%;height:100%;">'+sText+'</div>';  		
        }else{
			domContent.innerHTML = '<div style="'+div1_style+'"></div><img id="adv_pic" src="'+sUrl+'" onerror="this.src=\'/error/pic.jpg\';" style="'+img_style+'"/><div style="width:100%;height:100%;">'+sText+'</div>';  		
		}
		if(sHref!=''){
			if(sTarget=='1'){
				domContent.onclick=function(){
					window.open(sHref);
				}
			}else{
				domContent.onclick=function(){
					location.href=sHref;
				}
			}
		}
		domDiv.appendChild(domContent);
		
        var domClose = document.createElement('div');  
        domClose.innerHTML = '×';  
        domClose.style.position = 'absolute';  
        domClose.style.top = '0px';  
        domClose.style.right = '0px';  
		domClose.style.padding = '2px 5px';
        domClose.style.color = 'red';  
        domClose.style.cursor = 'pointer';  
  
        bindEvent(domClose, 'mouseenter', function () {  
		    this.style.background = '#C0C0C0';  
        });  
        bindEvent(domClose, 'mouseleave', function () {
            this.style.background = '';		
        });  
        bindEvent(domClose, 'click', function () {  
            domDiv.parentNode.removeChild(domDiv);  
        });  
  
        domDiv.appendChild(domClose);  
  
        document.body.appendChild(domDiv);  
  
        this.domDiv = domDiv;  
        this.nWidth = parseInt(sWidth.replace('px', ''));  
        this.nHeight = parseInt(sHeight.replace('px', ''));  
  
    },  
    work: function () { 
        var domDiv = this.domDiv,  
            nWidth = this.nWidth,  
            nHeight = this.nHeight,  
            oDirection = this.oDirection,
			speed = this.speed;
        this.oTimer = setInterval(function () {  
            var nLeft = 1 * oDirection.x * speed + parseInt(domDiv.style.left.replace('px', ''));  
            var nTop = 1 * oDirection.y * speed + parseInt(domDiv.style.top.replace('px', ''));  
            //var nLeft = 10 * oDirection.x + parseInt(domDiv.style.left.replace('px', ''));  
            //var nTop = 10 * oDirection.y + parseInt(domDiv.style.top.replace('px', ''));  
            var nClientWidth = document.documentElement.clientWidth - nWidth - 2,  
                nClientHeight = document.documentElement.clientHeight - nHeight - 2;  
  
            /** 
             * 这里主要是实现了方向的转换，大家可以参照坐标轴来，我上面定义的oDirection，就是先向右上角，顺时针旋转 
             * 1.当到达顶部，改变y向下运动 
             * 2.当到达右边，改变x向左运动 
             * 3.当到达底部，改变y向上运动 
             * 4.当到达左边，改变x向右运动 
             */  
            if (nTop < 0) {  
                nLeft = nLeft + nTop ;  
                nTop = 0;  
                oDirection.y = 1;  
            } else if (nLeft > nClientWidth) {  
                nTop = nTop - (nLeft - nClientWidth);  
                nLeft = nClientWidth;  
                oDirection.x = -1;  
            } else if (nTop > nClientHeight ) {  
                nLeft = nLeft - (nTop - nClientHeight) ;  
                nTop = nClientHeight ;  
                oDirection.y = -1;  
            } else if (nLeft < 0) {  
                nTop = nTop + nLeft;  
                nLeft = 0;  
                oDirection.x = 1;  
            }  
  
            domDiv.style.left = nLeft + 'px';  
            domDiv.style.top = nTop + 'px';  
        }, 100);  
    }  
};  
  
function bindEvent(elem, event, fun) {  
    if (window.attachEvent) {  
        elem.attachEvent('on' + event, fun);  
    }  
    else {  
        elem.addEventListener(event, fun);  
    }  
}  
  
function getScrollTop() {  
    var scrollPos;  
    if (window.pageYOffset) {  
        scrollPos = window.pageYOffset;  
    }  
    else if (document.compatMode && document.compatMode != 'BackCompat') {  
        scrollPos = document.documentElement.scrollTop;  
    }  
    else if (document.body) {  
        scrollPos = document.body.scrollTop;  
    }  
    return scrollPos;  
}  

//3.文章访问计数
if(queryStr("id")){
	vote({"tbl":"main_article","do":"see","showok":"","callback":"","id":queryStr("id")},null);
}
