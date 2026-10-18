var _____WB$wombat$assign$function_____=function(name){return (globalThis._wb_wombat && globalThis._wb_wombat.local_init && globalThis._wb_wombat.local_init(name))||globalThis[name];};if(!globalThis.__WB_pmw){globalThis.__WB_pmw=function(obj){this.__WB_source=obj;return this;}}{
let window = _____WB$wombat$assign$function_____("window");
let self = _____WB$wombat$assign$function_____("self");
let document = _____WB$wombat$assign$function_____("document");
let location = _____WB$wombat$assign$function_____("location");
let top = _____WB$wombat$assign$function_____("top");
let parent = _____WB$wombat$assign$function_____("parent");
let frames = _____WB$wombat$assign$function_____("frames");
let opener = _____WB$wombat$assign$function_____("opener");
 var Speed_1 = 30; //速度(毫秒)
        var Space_1 = 20; //每次移动(px)
        var PageWidth_1 = 880 * 1; //翻页宽度
        var interval_1 = 5000; //翻页间隔时间
        var fill_1 = 0; //整体移位
        var MoveLock_1 = false;
        var MoveTimeObj_1;
        var MoveWay_1 = "right";
        var Comp_1 = 0;
        var AutoPlayObj_1 = null;
        function GetObj(objName) { if (document.getElementById) { return eval('document.getElementById("' + objName + '")') } else { return eval('document.all.' + objName) } }
        function AutoPlay_1() { clearInterval(AutoPlayObj_1); AutoPlayObj_1 = setInterval('ISL_GoDown_1();ISL_StopDown_1();', interval_1) }
        function ISL_GoUp_1() { if (MoveLock_1) return; clearInterval(AutoPlayObj_1); MoveLock_1 = true; MoveWay_1 = "left"; MoveTimeObj_1 = setInterval('ISL_ScrUp_1();', Speed_1); }
        function ISL_StopUp_1() {
            if (MoveWay_1 == "right") { return }; clearInterval(MoveTimeObj_1); if ((GetObj('ISL_Cont_1').scrollLeft - fill_1) % PageWidth_1 != 0) { Comp_1 = fill_1 - (GetObj('ISL_Cont_1').scrollLeft % PageWidth_1); CompScr_1() } else { MoveLock_1 = false }
            AutoPlay_1()
        }
        function ISL_ScrUp_1() {
            if (GetObj('ISL_Cont_1').scrollLeft <= 0) { GetObj('ISL_Cont_1').scrollLeft = GetObj('ISL_Cont_1').scrollLeft + GetObj('List1_1').offsetWidth }
            GetObj('ISL_Cont_1').scrollLeft -= Space_1
        }
        function ISL_GoDown_1() { clearInterval(MoveTimeObj_1); if (MoveLock_1) return; clearInterval(AutoPlayObj_1); MoveLock_1 = true; MoveWay_1 = "right"; ISL_ScrDown_1(); MoveTimeObj_1 = setInterval('ISL_ScrDown_1()', Speed_1) }
        function ISL_StopDown_1() {
            if (MoveWay_1 == "left") { return }; clearInterval(MoveTimeObj_1); if (GetObj('ISL_Cont_1').scrollLeft % PageWidth_1 - (fill_1 >= 0 ? fill_1 : fill_1 + 1) != 0) { Comp_1 = PageWidth_1 - GetObj('ISL_Cont_1').scrollLeft % PageWidth_1 + fill_1; CompScr_1() } else { MoveLock_1 = false }
            AutoPlay_1()
        }
        function ISL_ScrDown_1() {
            if (GetObj('ISL_Cont_1').scrollLeft >= GetObj('List1_1').scrollWidth) { GetObj('ISL_Cont_1').scrollLeft = GetObj('ISL_Cont_1').scrollLeft - GetObj('List1_1').scrollWidth }
            GetObj('ISL_Cont_1').scrollLeft += Space_1
        }
        function CompScr_1() {
            if (Comp_1 == 0) { MoveLock_1 = false; return }
            var num, TempSpeed = Speed_1, TempSpace = Space_1; if (Math.abs(Comp_1) < PageWidth_1 / 2) { TempSpace = Math.round(Math.abs(Comp_1 / Space_1)); if (TempSpace < 1) { TempSpace = 1 } }
            if (Comp_1 < 0) {
                if (Comp_1 < -TempSpace) { Comp_1 += TempSpace; num = TempSpace } else { num = -Comp_1; Comp_1 = 0 }
                GetObj('ISL_Cont_1').scrollLeft -= num; setTimeout('CompScr_1()', TempSpeed)
            } else {
                if (Comp_1 > TempSpace) { Comp_1 -= TempSpace; num = TempSpace } else { num = Comp_1; Comp_1 = 0 }
                GetObj('ISL_Cont_1').scrollLeft += num; setTimeout('CompScr_1()', TempSpeed)
            }
        }
        function picrun_ini() {
            GetObj("List2_1").innerHTML = GetObj("List1_1").innerHTML;
            GetObj('ISL_Cont_1').scrollLeft = fill_1 >= 0 ? fill_1 : GetObj('List1_1').scrollWidth - Math.abs(fill_1);
            GetObj("ISL_Cont_1").onmouseover = function () { clearInterval(AutoPlayObj_1) }
            GetObj("ISL_Cont_1").onmouseout = function () { AutoPlay_1() }
            AutoPlay_1();
        }
}

/*
     FILE ARCHIVED ON 03:55:36 Mar 07, 2016 AND RETRIEVED FROM THE
     INTERNET ARCHIVE ON 19:56:17 Oct 17, 2026.
     JAVASCRIPT APPENDED BY WAYBACK MACHINE, COPYRIGHT INTERNET ARCHIVE.

     ALL OTHER CONTENT MAY ALSO BE PROTECTED BY COPYRIGHT (17 U.S.C.
     SECTION 108(a)(3)).
*/
/*
playback timings (ms):
  captures_list: 0.505
  exclusion.robots: 0.041
  exclusion.robots.policy: 0.029
  esindex: 0.008
  cdx.remote: 104.22
  LoadShardBlock: 1253.748 (3)
  PetaboxLoader3.resolve: 1231.456 (4)
  PetaboxLoader3.datanode: 102.87 (4)
  load_resource: 125.997
*/